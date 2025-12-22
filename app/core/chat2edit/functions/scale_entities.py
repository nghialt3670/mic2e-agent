from typing import List, Literal, Optional, Union

from chat2edit.execution.decorators import (
    deepcopy_parameter,
    feedback_empty_list_parameters,
    feedback_ignored_return_value,
    feedback_invalid_parameter_type,
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
@exclude_coroutine
async def scale_entities(
    image: Image,
    entities: List[Union[Image, Object, Text, Box, Point]],
    scale: float,
    axis: Optional[Literal["x", "y"]] = None,
) -> Image:
    image = await inpaint_uninpainted_objects_in_entities(image, entities)

    for entity in entities:
        if axis == "x":
            # Scale only X axis
            entity.scaleX = (entity.scaleX or 1.0) * scale
        elif axis == "y":
            # Scale only Y axis
            entity.scaleY = (entity.scaleY or 1.0) * scale
        else:
            # Scale both axes uniformly
            entity.scaleX = (entity.scaleX or 1.0) * scale
            entity.scaleY = (entity.scaleY or 1.0) * scale

    return image
