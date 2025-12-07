from typing import Any, Dict, List, Literal, Optional

from chat2edit import Chat2EditConfig
from chat2edit.models import ChatCycle
from pydantic import BaseModel, Field

from app.env import OPENAI_API_KEY


class AttachmentModel(BaseModel):
    file_id: str


class MessageModel(BaseModel):
    text: str
    attachments: List[AttachmentModel]


class LlmConfig(BaseModel):
    provider: Literal["openai", "google"] = Field(default="openai")
    api_key: Optional[str] = Field(default=None)
    model: str
    params: Dict[str, Any] = Field(default_factory=dict)


DEFAULT_LLM_CONFIG = LlmConfig(
    provider="openai", api_key=OPENAI_API_KEY, model="gpt-3.5-turbo", params={}
)


DEFAULT_CHAT2EDIT_CONFIG = Chat2EditConfig(
    max_prompt_cycles=5,
    max_llm_exchanges=2,
)


class Chat2EditGenerateRequestModel(BaseModel):
    llm_config: LlmConfig = Field(default=DEFAULT_LLM_CONFIG)
    chat2edit_config: Chat2EditConfig = Field(default=DEFAULT_CHAT2EDIT_CONFIG)
    message: MessageModel
    history: List[ChatCycle] = Field(default=[])
    context_file_id: Optional[str] = Field(default=None)


class Chat2EditGenerateResponseModel(BaseModel):
    message: MessageModel
    cycle: Optional[ChatCycle] = Field(default=None)
    context_file_id: Optional[str] = Field(default=None)
