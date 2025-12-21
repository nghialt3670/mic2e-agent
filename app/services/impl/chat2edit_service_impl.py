import asyncio
from typing import Any, Dict, Optional

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

        # Create callbacks if cycle_id is provided
        callbacks = None
        if cycle_id:
            callbacks = self._create_callbacks(cycle_id)

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

    def _create_callbacks(self, cycle_id: str) -> Chat2EditCallbacks:
        """Create callbacks that publish progress to Redis in order."""

        # Store reference to redis_client to avoid closure issues
        redis_client = self._redis_client

        if not redis_client:
            raise ValueError("Redis client is not initialized")

        # Create a queue and processor to serialize events
        progress_queue = asyncio.Queue()
        loop = asyncio.get_event_loop()
        processor_task = None

        async def _process_queue():
            """Process progress events sequentially from the queue."""
            while True:
                try:
                    item = await progress_queue.get()
                    if item is None:  # Sentinel to stop
                        break
                    event_type, message, data = item
                    await redis_client.publish_progress(
                        cycle_id, event_type, message=message, data=data
                    )
                    progress_queue.task_done()
                except Exception as e:
                    print(f"Error processing progress queue: {e}")

        # Start the queue processor if loop is running
        if loop.is_running():
            processor_task = asyncio.create_task(_process_queue())

        def _enqueue_progress(event_type: str, message: Optional[str] = None, data: Optional[Any] = None):
            """Enqueue progress event to be processed sequentially."""
            try:
                if loop.is_running() and processor_task:
                    # Put in queue (non-blocking)
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

        return Chat2EditCallbacks(
            on_request=on_request,
            on_prompt=on_prompt,
            on_answer=on_answer,
            on_extract=on_extract,
            on_execute=on_execute,
        )
