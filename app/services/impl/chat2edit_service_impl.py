import asyncio
from typing import Any, Awaitable, Callable, Dict, Optional, Tuple

from chat2edit import Chat2Edit, Chat2EditCallbacks
from chat2edit.models import ExecutionBlock, Message
from chat2edit.prompting.llms import GoogleLlm, Llm, OpenAILlm
from pydantic import TypeAdapter

from app.clients.redis_client import RedisClient
from app.clients.storage_client import StorageClient
from app.core.chat2edit.mic2e_context_provider import Mic2eContextProvider
from app.core.chat2edit.mic2e_context_strategy import CONTEXT_TYPE, Mic2eContextStrategy
from app.core.chat2edit.mic2e_prompting_strategy import Mic2ePromptingStrategy
from app.core.chat2edit.models import Image
from app.env import GOOGLE_API_KEY, OPENAI_API_KEY
from app.schemas.chat2edit_schemas import (
    AttachmentModel,
    Chat2EditGenerateRequestModel,
    Chat2EditGenerateResponseModel,
    LlmConfig,
    MessageModel,
)
from app.services.chat2edit_service import Chat2EditService
from app.utils.factories import create_uuid4


class Chat2EditServiceImpl(Chat2EditService):
    def __init__(self, storage_client: StorageClient, redis_client: RedisClient):
        self._storage_client = storage_client
        self._redis_client = redis_client
        self._context_provider = Mic2eContextProvider()
        self._context_strategy = Mic2eContextStrategy()
        self._prompting_strategy = Mic2ePromptingStrategy()

    async def generate(
        self, request: Chat2EditGenerateRequestModel, cycle_id: Optional[str] = None
    ) -> Chat2EditGenerateResponseModel:
        """Generate a Chat2Edit response. If cycle_id is provided, publish progress to Redis."""

        # If this cycle ID has been used before (e.g. regenerate), clear any
        # previous progress events so each generation starts fresh.
        if cycle_id:
            await self._redis_client.clear_progress(cycle_id)

        print("use qwen")
        print(request)

        if request.use_qwen:
            if cycle_id:
                await self._redis_client.publish_progress(
                    cycle_id,
                    "request",
                    message="Routing request to Qwen API...",
                )
            try:
                # 1. Resolve and download source image
                pil_image = None
                if request.message.attachments:
                    file_id = request.message.attachments[0].file_id
                    core_image = await self._download_image_attachment(file_id)
                    pil_image = core_image.get_image()
                elif request.context_file_id:
                    context = await self._download_context(request.context_file_id)
                    from app.core.chat2edit.models.image import Image as CoreImage
                    for val in context.values():
                        if isinstance(val, CoreImage):
                            pil_image = val.get_image()
                            break

                if not pil_image:
                    raise ValueError("No input image found in attachments or context")

                # 2. Call DashScope Qwen API
                import base64
                import httpx
                from io import BytesIO
                from PIL import Image as PILImage
                from app.env import DASHSCOPE_API_KEY

                if not DASHSCOPE_API_KEY:
                    raise ValueError("DASHSCOPE_API_KEY is not configured")

                clean_api_key = DASHSCOPE_API_KEY.strip('"' + "'")

                # Resize image to a maximum dimension of 1024 to keep base64 payload size small and prevent ReadError
                max_dimension = 1024
                if max(pil_image.width, pil_image.height) > max_dimension:
                    pil_image.thumbnail((max_dimension, max_dimension))

                buffered = BytesIO()
                rgb_image = pil_image.convert("RGB") if pil_image.mode != "RGB" else pil_image
                rgb_image.save(buffered, format="JPEG", quality=85)
                img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                image_data_url = f"data:image/jpeg;base64,{img_str}"

                headers = {
                    "Authorization": f"Bearer {clean_api_key}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "model": "qwen-image-edit",
                    "input": {
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {"image": image_data_url},
                                    {"text": request.message.text}
                                ]
                            }
                        ]
                    }
                }

                async with httpx.AsyncClient(timeout=300.0) as client:
                    url = "https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
                    try:
                        response = await client.post(url, json=payload, headers=headers)
                        if response.status_code == 200:
                            print(f"[Qwen API Success] Status: {response.status_code}, Body: {response.text}")
                        else:
                            print(f"[Qwen API Error] Status: {response.status_code}, Body: {response.text}")
                        response.raise_for_status()
                    except httpx.HTTPStatusError as err:
                        error_body = err.response.text
                        print(f"[Qwen API HTTPStatusError] Status: {err.response.status_code}, Body: {error_body}")
                        raise RuntimeError(f"Qwen API error (HTTP {err.response.status_code}): {error_body}") from err

                    res_data = response.json()

                    # Handle asynchronous tasks (if task_id is present, poll for completion)
                    task_id = res_data.get("output", {}).get("task_id")
                    if task_id:
                        status_url = f"https://dashscope-intl.aliyuncs.com/api/v1/tasks/{task_id}"
                        while True:
                            await asyncio.sleep(2)
                            try:
                                status_resp = await client.get(status_url, headers=headers)
                                if status_resp.status_code != 200:
                                    print(f"[Qwen Task Status Error] Status: {status_resp.status_code}, Body: {status_resp.text}")
                                status_resp.raise_for_status()
                            except httpx.HTTPStatusError as err:
                                error_body = err.response.text
                                print(f"[Qwen Task Status HTTPStatusError] Status: {err.response.status_code}, Body: {error_body}")
                                raise RuntimeError(f"Qwen task status check error (HTTP {err.response.status_code}): {error_body}") from err
                            status_data = status_resp.json()
                            task_status = status_data.get("output", {}).get("task_status")
                            if task_status == "SUCCEEDED":
                                res_data = status_data
                                break
                            elif task_status in ["FAILED", "CANCELED"]:
                                raise RuntimeError(f"Qwen task {task_status}: {status_data.get('output', {}).get('message')}")

                    # Extract result image URL
                    # Primary path: output.choices[0].message.content[0].image
                    # (actual response format from qwen-image-edit intl endpoint)
                    output_url = None
                    choices = res_data.get("output", {}).get("choices", [])
                    if choices:
                        content = choices[0].get("message", {}).get("content", [])
                        if isinstance(content, list):
                            for item in content:
                                if "image" in item:
                                    output_url = item["image"]
                                    break

                    # Fallback path: output.results[0].url (older/async task format)
                    if not output_url:
                        output_results = res_data.get("output", {}).get("results", [])
                        if output_results:
                            output_url = output_results[0].get("url")

                    if not output_url:
                        raise RuntimeError(f"Could not extract result image URL from Qwen response: {res_data}")

                    print(f"[Qwen API] Extracted output image URL: {output_url}")

                    try:
                        img_resp = await client.get(output_url)
                        img_resp.raise_for_status()
                    except httpx.HTTPStatusError as err:
                        print(f"[Qwen Image Download Error] Status: {err.response.status_code}")
                        raise RuntimeError(f"Failed to download Qwen result image: {err}") from err
                    edited_pil_image = PILImage.open(BytesIO(img_resp.content)).convert("RGB")

                # 3. Create CoreImage representation and upload
                from app.core.chat2edit.models.image import Image as CoreImage
                from app.utils.image_utils import convert_image_to_data_url
                from chat2edit.models.message import Message as Chat2EditMessage
                from chat2edit.models import ChatCycle

                # Build CoreImage by constructing via model_validate so Pydantic resolves the
                # FabricGroup.objects discriminator (FabricChild union) correctly.
                # We include the Fabric.js layout properties (originX, originY, left, top)
                # that the frontend's createFigObjectFromImageFile produces, otherwise
                # Fabric.js Group.fromObject() will render a black canvas.
                img_data_url = convert_image_to_data_url(edited_pil_image)
                img_w = edited_pil_image.width
                img_h = edited_pil_image.height
                output_core_image = CoreImage.model_validate({
                    "left": img_w / 2,
                    "top": img_h / 2,
                    "width": img_w,
                    "height": img_h,
                    "objects": [{
                        "type": "Image",
                        "src": img_data_url,
                        "width": img_w,
                        "height": img_h,
                        "originX": "center",
                        "originY": "center",
                        "left": 0,
                        "top": 0,
                        "selectable": False,
                    }]
                })
                res_file_id = await self._upload_image_attachment(output_core_image)

                # 4. Construct result
                response_text = "Here is your edited image."
                response_message = Chat2EditMessage(text=response_text, attachments=[output_core_image])

                updated_context = {"image": output_core_image}
                context_file_id = await self._upload_context(updated_context)

                request_attachments = []
                if request.message.attachments:
                    orig_file_id = request.message.attachments[0].file_id
                    orig_core_image = await self._download_image_attachment(orig_file_id)
                    request_attachments.append(orig_core_image)

                request_chat2edit_msg = Chat2EditMessage(text=request.message.text, attachments=request_attachments)
                chat_cycle = ChatCycle(request=request_chat2edit_msg, cycles=[])

                result = Chat2EditGenerateResponseModel(
                    cycle=chat_cycle,
                    message=await self._create_response_message(response_message),
                    context_file_id=context_file_id,
                )

                if cycle_id:
                    await self._redis_client.publish_progress(
                        cycle_id,
                        "complete",
                        message="Generation completed successfully",
                        data=result.model_dump(mode="json"),
                    )
                return result

            except Exception as e:
                if cycle_id:
                    await self._redis_client.publish_progress(
                        cycle_id,
                        "error",
                        message=str(e),
                    )
                raise

        # Create callbacks if cycle_id is provided
        callbacks = None
        flush_progress: Optional[Callable[[], Awaitable[None]]] = None
        if cycle_id:
            callbacks, flush_progress = self._create_callbacks(cycle_id)

        chat2edit = Chat2Edit(
            llm=self._create_llm(request.llm_config),
            context_provider=self._context_provider,
            context_strategy=self._context_strategy,
            prompting_strategy=self._prompting_strategy,
            config=request.chat2edit_config,
            callbacks=callbacks,
        )

        message = await self._create_request_message(request.message)
        context = (
            await self._download_context(request.context_file_id)
            if request.context_file_id
            else {}
        )

        try:
            response, cycle, updated_context = await chat2edit.generate(
                message, request.history, context
            )

            result = Chat2EditGenerateResponseModel(
                cycle=cycle,
                message=(
                    await self._create_response_message(response) if response else None
                ),
                context_file_id=await self._upload_context(updated_context),
            )

            if flush_progress:
                await flush_progress()

            # Publish completion event if cycle_id is provided
            if cycle_id:
                await self._redis_client.publish_progress(
                    cycle_id,
                    "complete",
                    message="Generation completed successfully",
                    data=result.model_dump(mode="json"),
                )

            return result
        except Exception as e:
            if flush_progress:
                await flush_progress()

            # Publish error event if cycle_id is provided
            if cycle_id:
                await self._redis_client.publish_progress(
                    cycle_id,
                    "error",
                    message=str(e),
                )
            raise

    def _create_llm(self, config: LlmConfig) -> Llm:
        if config.provider == "openai":
            llm = OpenAILlm(config.model, **config.params)
            llm.set_api_key(config.api_key or OPENAI_API_KEY)
            return llm
        elif config.provider == "google":
            llm = GoogleLlm(config.model, **config.params)
            llm.set_api_key(config.api_key or GOOGLE_API_KEY)
            return llm
        else:
            raise ValueError(f"Invalid LLM provider: {config.provider}")

    async def _create_request_message(self, message: MessageModel) -> Message:
        file_ids = [attachment.file_id for attachment in message.attachments]
        attachments = await asyncio.gather(
            *map(self._download_image_attachment, file_ids)
        )
        return Message(text=message.text, attachments=attachments)

    async def _create_response_message(self, message: Message) -> MessageModel:
        file_ids = await asyncio.gather(
            *map(self._upload_image_attachment, message.attachments)
        )
        filenames = [f"{create_uuid4()}.fig.json" for _ in file_ids]
        attachments = [
            AttachmentModel(file_id=file_id, filename=filename)
            for file_id, filename in zip(file_ids, filenames)
        ]
        return MessageModel(text=message.text, attachments=attachments)

    async def _download_image_attachment(self, file_id: str) -> Image:
        image_bytes = await self._storage_client.download_file(file_id)
        return TypeAdapter(Image).validate_json(image_bytes)

    async def _upload_image_attachment(self, image: Image) -> str:
        image_bytes = image.model_dump_json().encode("utf-8")
        return await self._storage_client.upload_file(image_bytes, "image.fig.json")

    async def _download_context(self, file_id: str) -> Dict[str, Any]:
        context_bytes = await self._storage_client.download_file(file_id)
        return TypeAdapter(CONTEXT_TYPE).validate_json(context_bytes)

    async def _upload_context(self, context: Dict[str, Any]) -> str:
        context_bytes = TypeAdapter(Dict[str, Any]).dump_json(context)
        return await self._storage_client.upload_file(context_bytes, "context.json")

    def _create_callbacks(
        self, cycle_id: str
    ) -> Tuple[Chat2EditCallbacks, Callable[[], Awaitable[None]]]:
        """Create callbacks that publish progress to Redis in order."""

        redis_client = self._redis_client
        if not redis_client:
            raise ValueError("Redis client is not initialized")

        progress_queue: asyncio.Queue = asyncio.Queue()
        processor_task: Optional[asyncio.Task] = None

        async def _process_queue() -> None:
            while True:
                item = await progress_queue.get()
                try:
                    if item is None:
                        return
                    event_type, message, data = item
                    await redis_client.publish_progress(
                        cycle_id, event_type, message=message, data=data
                    )
                except Exception as e:
                    print(f"Error processing progress queue: {e}")
                finally:
                    progress_queue.task_done()

        processor_task = asyncio.create_task(_process_queue())

        async def flush_progress() -> None:
            await progress_queue.join()
            await progress_queue.put(None)
            if processor_task:
                await processor_task

        def _enqueue_progress(
            event_type: str,
            message: Optional[str] = None,
            data: Optional[Any] = None,
        ) -> None:
            try:
                progress_queue.put_nowait((event_type, message, data))
            except Exception as e:
                print(f"Error enqueueing {event_type} progress: {e}")

        def on_request(message: Message) -> None:
            _enqueue_progress("request", message="Sending request to LLM...", data=message.model_dump())

        def on_prompt(message: Message) -> None:
            _enqueue_progress("prompt", message="Generating prompt...", data=message.model_dump())

        def on_answer(message: Message) -> None:
            _enqueue_progress("answer", message="Received answer from LLM...", data=message.model_dump())

        def on_extract(code: str) -> None:
            _enqueue_progress("extract", message="Extracting code...", data=code)

        def on_execute(block: ExecutionBlock) -> None:
            block_type = getattr(block, 'type', None) or getattr(block, 'block_type', None) or str(type(block).__name__)
            _enqueue_progress("execute", message=f"Executing: {block_type}", data=block.model_dump())

        return (
            Chat2EditCallbacks(
                on_request=on_request,
                on_prompt=on_prompt,
                on_answer=on_answer,
                on_extract=on_extract,
                on_execute=on_execute,
            ),
            flush_progress,
        )
