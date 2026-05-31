from typing import Literal, Optional, Union

from chat2edit.execution.decorators import (
    feedback_invalid_parameter_type,
    feedback_unexpected_error,
)
from chat2edit.prompting.stubbing.decorators import exclude_coroutine

from app.core.chat2edit.models import Box, Image, Object, Point, Text


def _get_entity_bounding_box(
    entity: Union[Object, Text, Box, Point],
    image_width: int,
    image_height: int,
) -> tuple[int, int, int, int]:
    half_width = entity.width / 2
    half_height = entity.height / 2
    center_x = entity.left if entity.originX == "center" else entity.left + half_width
    center_y = entity.top if entity.originY == "center" else entity.top + half_height
    center_x = center_x + image_width / 2
    center_y = center_y + image_height / 2
    
    x_min = int(center_x - half_width)
    y_min = int(center_y - half_height)
    x_max = int(center_x + half_width)
    y_max = int(center_y + half_height)
    
    return x_min, y_min, x_max, y_max


def _shift_box_by_position(
    x_min: int,
    y_min: int,
    x_max: int,
    y_max: int,
    position: Literal[
        "left",
        "right",
        "top",
        "bottom",
        "top-left",
        "top-right",
        "bottom-left",
        "bottom-right",
    ],
    image_width: int,
    image_height: int,
) -> tuple[int, int, int, int]:
    """
    Shift a bounding box based on position relative to image boundaries.
    
    The box is shifted so that the specified edge/corner aligns with the image boundary.
    """
    box_width = x_max - x_min
    box_height = y_max - y_min
    
    position_map = {
        "left": (max(0, x_min - box_width), y_min, max(0, x_max - box_width), y_max),
        "right": (min(image_width, x_min + box_width), y_min, min(image_width, x_max + box_width), y_max),
        "top": (x_min, max(0, y_min - box_height), x_max, max(0, y_max - box_height)),
        "bottom": (x_min, min(image_height, y_min + box_height), x_max, min(image_height, y_max + box_height)),
        "top-left": (max(0, x_min - box_width), max(0, y_min - box_height), max(0, x_max - box_width), max(0, y_max - box_height)),
        "top-right": (min(image_width, x_min + box_width), max(0, y_min - box_height), min(image_width, x_max + box_width), max(0, y_max - box_height)),
        "bottom-left": (max(0, x_min - box_width), min(image_height, y_min + box_height), max(0, x_max - box_width), min(image_height, y_max + box_height)),
        "bottom-right": (min(image_width, x_min + box_width), min(image_height, y_min + box_height), min(image_width, x_max + box_width), min(image_height, y_max + box_height)),
    }
    
    return position_map[position]


@feedback_unexpected_error
@feedback_invalid_parameter_type
def get_box(
    image: Image,
    entity: Union[Object, Text, Box, Point],
    position: Optional[
        Literal[
            "left",
            "right",
            "top",
            "bottom",
            "top-left",
            "top-right",
            "bottom-left",
            "bottom-right",
        ]
    ] = None,
) -> Box:
    pil_image = image.get_image()
    image_width = pil_image.width
    image_height = pil_image.height
    
    x_min, y_min, x_max, y_max = _get_entity_bounding_box(
        entity, image_width, image_height
    )
    
    if position is not None:
        x_min, y_min, x_max, y_max = _shift_box_by_position(
            x_min, y_min, x_max, y_max, position, image_width, image_height
        )
    
    box_width = x_max - x_min
    box_height = y_max - y_min
    
    return Box(
        left=x_min - image_width / 2,
        top=y_min - image_height / 2,
        width=box_width,
        height=box_height,
        originX="left",
        originY="top",
    )

