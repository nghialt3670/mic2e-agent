import asyncio
from typing import Any, Dict

from chat2edit import Chat2Edit
from chat2edit.models import Message
from chat2edit.prompting.llms import GoogleLlm, Llm, OpenAILlm
from pydantic import TypeAdapter

from app.clients.storage_client import StorageClient
from app.core.chat2edit.mic2e_context_provider import Mic2eContextProvider
from app.core.chat2edit.mic2e_context_strategy import Mic2eContextStrategy
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


class Chat2EditServiceImpl(Chat2EditService):
    def __init__(self, storage_client: StorageClient):
        self._storage_client = storage_client
        self._context_provider = Mic2eContextProvider()
        self._context_strategy = Mic2eContextStrategy()
        self._prompting_strategy = Mic2ePromptingStrategy()

    async def generate(
        self, request: Chat2EditGenerateRequestModel
    ) -> Chat2EditGenerateResponseModel:
        chat2edit = Chat2Edit(
            llm=self._create_llm(request.llm_config),
            context_provider=self._context_provider,
            context_strategy=self._context_strategy,
            prompting_strategy=self._prompting_strategy,
            config=request.chat2edit_config,
        )

        message = await self._create_request_message(request.message)
        context = (
            await self._download_context(request.context_file_id)
            if request.context_file_id
            else {}
        )
        response, cycle, updated_context = await chat2edit.generate(
            message, request.history, context
        )

        return Chat2EditGenerateResponseModel(
            cycle=cycle,
            message=(
                await self._create_response_message(response)
                if response
                else MessageModel(text="")
            ),
            context_file_id=await self._upload_context(updated_context),
        )

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
        attachments = [AttachmentModel(file_id=file_id) for file_id in file_ids]
        return MessageModel(text=message.text, attachments=attachments)

    async def _download_image_attachment(self, file_id: str) -> Image:
        image_bytes = await self._storage_client.download_file(file_id)
        return TypeAdapter(Image).validate_json(image_bytes)

    async def _upload_image_attachment(self, image: Image) -> str:
        image_bytes = image.model_dump_json().encode("utf-8")
        return await self._storage_client.upload_file(image_bytes, "image.fig.json")

    async def _download_context(self, file_id: str) -> Dict[str, Any]:
        context_bytes = await self._storage_client.download_file(file_id)
        return TypeAdapter(Dict[str, Any]).validate_json(context_bytes)

    async def _upload_context(self, context: Dict[str, Any]) -> str:
        context_bytes = TypeAdapter(Dict[str, Any]).dump_json(context)
        return await self._storage_client.upload_file(context_bytes, "context.json")
