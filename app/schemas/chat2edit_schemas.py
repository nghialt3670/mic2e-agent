from typing import Any, Dict, List, Literal, Optional

from chat2edit import Chat2EditConfig
from chat2edit.models import ChatCycle
from pydantic import BaseModel, Field

from app.env import GOOGLE_API_KEY


class AttachmentModel(BaseModel):
    file_id: str
    filename: str


class MessageModel(BaseModel):
    text: str
    attachments: List[AttachmentModel] = Field(default_factory=list)


class LlmConfig(BaseModel):
    provider: Literal["openai", "google"] = Field(default="google")
    api_key: Optional[str] = Field(default=None)
    model: str
    params: Dict[str, Any] = Field(default_factory=dict)


DEFAULT_LLM_CONFIG = LlmConfig(
    provider="google", api_key=GOOGLE_API_KEY, model="gemini-2.5-flash", params={}
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
    message: Optional[MessageModel] = Field(default=None)
    cycle: ChatCycle
    context_file_id: str


class Chat2EditProgressEventModel(BaseModel):
    type: Literal[
        "request", "prompt", "answer", "extract", "execute", "complete", "error"
    ]
    message: Optional[str] = Field(default=None)
    # Use Any here because some callbacks currently publish strings or other
    # non-dict payloads (e.g. reprs) into `data`. The frontend already treats
    # this as an opaque JSON-like value.
    data: Optional[Any] = Field(default=None)
