from typing import List, Literal, Optional, Tuple, Union

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


@feedback_ignored_return_value
@deepcopy_parameter("image")
@feedback_unexpected_error
@feedback_invalid_parameter_type
@feedback_empty_list_parameters(["entities"])
@feedback_mismatch_list_parameters(["entities", "positions"])
@exclude_coroutine
async def paste_entities(
    image: Image,
    entities: List[Union[Image, Object, Text, Box, Point]],
    positions: List[
        Union[
            Tuple[float, float],
            Literal[
                "center",
                "top",
                "bottom",
                "left",
                "right",
                "top-left",
                "top-right",
                "bottom-left",
                "bottom-right",
            ],
        ]
    ],
    anchor: Optional[Union[Image, Object, Text, Box, Point]] = None,
) -> Image:
    image_width = image.get_image().width
    image_height = image.get_image().height

    for entity, position in zip(entities, positions):
        if isinstance(position, tuple):
            x, y = position
        else:
            if anchor is None or isinstance(anchor, Image):
                # Use image as anchor (current behavior)
                x, y = _calculate_position_coordinates(
                    position, image_width, image_height, entity.width, entity.height
                )

            else:
                # Use entity as anchor - position target outside the anchor entity
                x, y = _calculate_entity_anchor_position(
                    position, anchor, entity.width, entity.height
                )

        entity.left = x
        entity.top = y
        image.add_object(entity)

    return image


def _calculate_position_coordinates(
    position: Literal[
        "center",
        "top",
        "bottom",
        "left",
        "right",
        "top-left",
        "top-right",
        "bottom-left",
        "bottom-right",
    ],
    image_width: int,
    image_height: int,
    entity_width: float,
    entity_height: float,
) -> Tuple[float, float]:
    center_x = (image_width - entity_width) / 2 - image_width / 2 + entity_width / 2
    center_y = (image_height - entity_height) / 2 - image_height / 2 + entity_height / 2

    left_x = - image_width / 2 + entity_width / 2
    right_x = image_width / 2 - entity_width / 2
    top_y = - image_height / 2 + entity_height / 2
    bottom_y = image_height / 2 - entity_height / 2

    position_map = {
        "top-left": (left_x, top_y),
        "top": (center_x, top_y),
        "top-right": (right_x, top_y),
        "left": (left_x, center_y),
        "center": (center_x, center_y),
        "right": (right_x, center_y),
        "bottom-left": (left_x, bottom_y),
        "bottom": (center_x, bottom_y),
        "bottom-right": (right_x, bottom_y),
    }

    return position_map[position]


def _calculate_entity_anchor_position(
    position: Literal[
        "center",
        "top",
        "bottom",
        "left",
        "right",
        "top-left",
        "top-right",
        "bottom-left",
        "bottom-right",
    ],
    anchor: Union[Object, Text, Box, Point],
    entity_width: float,
    entity_height: float,
) -> Tuple[float, float]:
    """Calculate position relative to anchor entity, placing target outside the anchor."""
    # Anchor entity boundaries
    anchor_width = anchor.width
    anchor_height = anchor.height
    anchor_left = anchor.left
    anchor_top = anchor.top

    top = anchor_top - entity_height / 2 - anchor_height / 2
    bottom = anchor_top + anchor_height / 2 + entity_height / 2
    left = anchor_left - entity_width / 2 - anchor_width / 2
    right = anchor_left + anchor_width / 2 + entity_width / 2

    # Calculate target entity position (outside the anchor)
    position_map = {
        "top-left": (left, top),
        "top": (anchor_left, top),
        "top-right": (right, top),
        "left": (left, anchor_top),
        "center": (anchor_left, anchor_top),
        "right": (right, anchor_top),
        "bottom-left": (left, bottom),
        "bottom": (anchor_left, bottom),
        "bottom-right": (right, bottom),
    }

    return position_map[position]
