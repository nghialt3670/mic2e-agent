from copy import deepcopy
from typing import List, Literal, Tuple, Union

from chat2edit.execution.decorators import (
    deepcopy_parameter,
    feedback_empty_list_parameters,
    feedback_ignored_return_value,
    feedback_invalid_parameter_type,
    feedback_mismatch_list_parameters,
)
from chat2edit.prompting.stubbing.decorators import exclude_coroutine

from app.core.chat2edit.models import Box, Image, Object, Point, Text
from app.core.chat2edit.utils import inpaint_uninpainted_objects_in_entities
from app.core.chat2edit.utils.image_utils import get_own_objects


@feedback_ignored_return_value
@deepcopy_parameter("image")
@feedback_invalid_parameter_type
@feedback_empty_list_parameters(["entities"])
@feedback_mismatch_list_parameters(["entities", "offsets"])
@exclude_coroutine
async def shift_entities(
    image: Image,
    entities: List[Union[Image, Object, Text, Box, Point]],
    offsets: List[Tuple[int, int]],
    unit: Literal["pixel", "percentage"],
) -> Image:
    image_width = image.get_image().width
    image_height = image.get_image().height

    image = await inpaint_uninpainted_objects_in_entities(image, entities)

    own_entities = get_own_objects(image, entities)
    for entity, (dx, dy) in zip(own_entities, offsets):
        if unit == "pixel":
            entity.left = entity.left + dx
            entity.top = entity.top + dy
        elif unit == "percentage":
            dx_pixels = dx * image_width
            dy_pixels = dy * image_height
            entity.left = entity.left + dx_pixels
            entity.top = entity.top + dy_pixels

    return deepcopy(image)
