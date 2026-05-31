from typing import Any, Dict, List

from chat2edit.context.providers import ContextProvider
from chat2edit.models import Exemplar

from app.core.chat2edit.functions.apply_filter import apply_filter
from app.core.chat2edit.functions.segment_objects import segment_objects
from app.core.chat2edit.functions.flip_entities import flip_entities
from app.core.chat2edit.functions.generate_object import generate_object
from app.core.chat2edit.functions.generate_objects import generate_objects
from app.core.chat2edit.functions.get_box import get_box
from app.core.chat2edit.functions.inpaint_objects import inpaint_objects
from app.core.chat2edit.functions.paste_entities import paste_entities
from app.core.chat2edit.functions.remove_entities import remove_entities
from app.core.chat2edit.functions.replace_entities import replace_entities
from app.core.chat2edit.functions.respond_user import respond_user
from app.core.chat2edit.functions.rotate_entities import rotate_entities
from app.core.chat2edit.functions.scale_entities import scale_entities
from app.core.chat2edit.functions.segment_object import segment_object
from app.core.chat2edit.functions.shift_entities import shift_entities
from app.core.chat2edit.mic2e_exemplars import create_mic2e_exemplars


class Mic2eContextProvider(ContextProvider):
    def __init__(self, interactive: bool = True):
        super().__init__()
        self.interactive = interactive

    def get_context(self) -> Dict[str, Any]:
        context = {
            "apply_filter": apply_filter,
            "segment_objects": segment_objects,
            "inpaint_objects": inpaint_objects,
            "remove_entities": remove_entities,
            "replace_entities": replace_entities,
            "rotate_entities": rotate_entities,
            "paste_entities": paste_entities,
            "shift_entities": shift_entities,
            "scale_entities": scale_entities,
            "flip_entities": flip_entities,
            "respond_user": respond_user,
        }

        # Only include interaction-dependent functions if interactive is enabled
        if self.interactive:
            context.update({
                "get_box": get_box,
                "segment_object": segment_object,
                "generate_object": generate_object,
                "generate_objects": generate_objects,
            })
        
        return context

    def get_exemplars(self) -> List[Exemplar]:
        """Get exemplars based on interactive mode."""
        return create_mic2e_exemplars(interactive=self.interactive)
