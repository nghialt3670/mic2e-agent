from typing import List

from chat2edit.execution.decorators import feedback_invalid_parameter_type, respond
from chat2edit.models import Message

from app.core.chat2edit.models import Image


@respond
@feedback_invalid_parameter_type
def respond_user(text: str, attachments: List[Image] = []) -> Message:
    return Message(text=text, attachments=attachments)
