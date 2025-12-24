from math import degrees
from typing import List, Literal, Union

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
@feedback_mismatch_list_parameters(["entities", "angles", "units", "directions"])
@exclude_coroutine
async def rotate_entities(
    image: Image,
    entities: List[Union[Image, Object, Text, Box, Point]],
    angles: List[float],
    units: List[Literal["degree", "radian"]],
    directions: List[Literal["cw", "ccw"]],
) -> Image:
    image = await inpaint_uninpainted_objects_in_entities(image, entities)

    own_entities = get_own_objects(image, entities)
    for entity, angle, unit, direction in zip(own_entities, angles, units, directions):
        delta = degrees(angle) if unit == "radian" else angle
        if direction == "ccw":
            delta = -delta
        # Fabric-style angle is in degrees
        entity.angle = (entity.angle or 0) + delta

    return image
