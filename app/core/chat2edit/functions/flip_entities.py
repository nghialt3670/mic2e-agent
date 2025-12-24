from typing import List, Literal, Union

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
from app.core.chat2edit.utils.image_utils import get_own_objects


@feedback_ignored_return_value
@deepcopy_parameter("image")
@feedback_unexpected_error
@feedback_invalid_parameter_type
@feedback_empty_list_parameters(["entities"])
@feedback_mismatch_list_parameters(["entities", "axes"])
@exclude_coroutine
async def flip_entities(
    image: Image,
    entities: List[Union[Image, Object, Text, Box, Point]],
    axes: List[Literal["x", "y"]],
) -> Image:
    image = await inpaint_uninpainted_objects_in_entities(image, entities)

    own_entities = get_own_objects(image, entities)
    for entity, axis in zip(own_entities, axes):
        if axis == "x":
            entity.flipX = not entity.flipX
        elif axis == "y":
            entity.flipY = not entity.flipY

    return image
