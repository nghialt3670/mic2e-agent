from typing import Any, Dict, List

from chat2edit.context.providers import ContextProvider
from chat2edit.models import ChatCycle

from app.core.chat2edit.functions.apply_filter import apply_filter
from app.core.chat2edit.functions.detect_objects import detect_objects
from app.core.chat2edit.functions.flip_entities import flip_entities
from app.core.chat2edit.functions.paste_entities import paste_entities
from app.core.chat2edit.functions.remove_entities import remove_entities
from app.core.chat2edit.functions.respond_user import respond_user
from app.core.chat2edit.functions.rotate_entities import rotate_entities
from app.core.chat2edit.functions.scale_entities import scale_entities
from app.core.chat2edit.functions.segment_object import segment_object
from app.core.chat2edit.functions.shift_entities import shift_entities
from app.core.chat2edit.mic2e_exemplars import MIC2E_EXEMPLARS


class Mic2eContextProvider(ContextProvider):
    def __init__(self):
        super().__init__()

    def get_context(self) -> Dict[str, Any]:
        return {
            "apply_filter": apply_filter,
            "segment_object": segment_object,
            "detect_objects": detect_objects,
            "remove_entities": remove_entities,
            "rotate_entities": rotate_entities,
            "paste_entities": paste_entities,
            "shift_entities": shift_entities,
            "scale_entities": scale_entities,
            "flip_entities": flip_entities,
            "respond_user": respond_user,
        }

    def get_exemplars(self) -> List[ChatCycle]:
        return MIC2E_EXEMPLARS
