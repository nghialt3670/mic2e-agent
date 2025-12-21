from typing import List

from chat2edit.execution.decorators import (
    deepcopy_parameter,
    feedback_empty_list_parameters,
    feedback_ignored_return_value,
    feedback_invalid_parameter_type,
    feedback_unexpected_error,
)
from chat2edit.prompting.stubbing.decorators import exclude_coroutine

from app.core.chat2edit.models.image import Image
from app.core.chat2edit.models.object import Object
from app.core.chat2edit.utils.inpaint_utils import inpaint_objects_with_prompt
from app.core.chat2edit.utils.image_utils import get_own_objects


@feedback_ignored_return_value
@deepcopy_parameter("image")
@feedback_unexpected_error
@feedback_invalid_parameter_type
@feedback_empty_list_parameters(["objects"])
@exclude_coroutine
async def inpaint_objects(image: Image, objects: List[Object], prompt: str) -> Image:
    own_objects = get_own_objects(image, objects)
    image = await inpaint_objects_with_prompt(image, own_objects, prompt)
    image = image.remove_objects(own_objects)
    return image
