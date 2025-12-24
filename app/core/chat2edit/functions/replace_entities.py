from typing import List, Union

from chat2edit.execution.decorators import (
    deepcopy_parameter,
    feedback_empty_list_parameters,
    feedback_ignored_return_value,
    feedback_invalid_parameter_type,
    feedback_mismatch_list_parameters,
    feedback_unexpected_error,
)
from chat2edit.prompting.stubbing.decorators import exclude_coroutine

from app.core.chat2edit.models import Box, Image, Object, Point, Text
from app.core.chat2edit.utils import inpaint_uninpainted_objects_in_entities


@feedback_ignored_return_value
@deepcopy_parameter("image")
@feedback_unexpected_error
@feedback_invalid_parameter_type
@feedback_empty_list_parameters(["entities"])
@feedback_mismatch_list_parameters(["targets", "replacements"])
@exclude_coroutine
async def replace_entities(
    image: Image, 
    targets: List[Union[Image, Object, Text, Box, Point]],
    replacements: List[Union[Image, Object, Text, Box, Point]]
) -> Image:
    image = await inpaint_uninpainted_objects_in_entities(image, targets)
    image.remove_objects(targets)
    for target, replacement in zip(targets, replacements):
        replacement.left = target.left
        replacement.top = target.top
        target_scaled_w = target.width * target.scaleX
        target_scaled_h = target.height * target.scaleY
        replacement_scaled_w = replacement.width * replacement.scaleX
        replacement_scaled_h = replacement.height * replacement.scaleY
        scale = (target_scaled_w + target_scaled_h) / (replacement_scaled_w + replacement_scaled_h)
        replacement.scaleX *= scale
        replacement.scaleY *= scale

    image.add_objects(replacements)
    return image
