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
            Point,
            Box,
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
        if isinstance(position, Point):
            x = position.left
            y = position.top
        elif isinstance(position, Box):
            # Position entity within the box and scale to fit
            x, y, scale = _calculate_box_position_and_scale(
                position, entity, image_width, image_height
            )
            # Apply scaling to fit within box
            entity.scaleX = (entity.scaleX or 1.0) * scale
            entity.scaleY = (entity.scaleY or 1.0) * scale
        elif isinstance(position, tuple):
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


def _calculate_box_position_and_scale(
    box: Box,
    entity: Union[Object, Text, Box, Point],
    image_width: int,
    image_height: int,
) -> Tuple[float, float, float]:
    """
    Calculate position and scale for entity to fit within the box.
    
    Returns:
        Tuple of (x, y, scale) where x, y are the center coordinates
        in Fabric.js centered coordinate system, and scale is the factor
        to apply to fit the entity within the box.
    """
    # Get box dimensions considering origin
    box_half_width = box.width / 2
    box_half_height = box.height / 2
    
    # Convert box center to absolute coordinates
    if box.originX == "center":
        box_center_x = box.left + image_width / 2
    else:
        box_center_x = box.left + image_width / 2 + box_half_width
    
    if box.originY == "center":
        box_center_y = box.top + image_height / 2
    else:
        box_center_y = box.top + image_height / 2 + box_half_height
    
    # Get entity's current scaled dimensions
    entity_scaled_width = entity.width * (entity.scaleX or 1.0)
    entity_scaled_height = entity.height * (entity.scaleY or 1.0)
    
    # Calculate scale factors to fit within box
    scale_x = box.width / entity_scaled_width if entity_scaled_width > 0 else 1.0
    scale_y = box.height / entity_scaled_height if entity_scaled_height > 0 else 1.0
    
    # Use minimum scale to maintain aspect ratio and ensure entity fits
    scale = min(scale_x, scale_y, 1.0)  # Don't scale up, only down
    
    # Position entity at box center (in Fabric.js centered coordinates)
    x = box_center_x - image_width / 2
    y = box_center_y - image_height / 2
    
    return x, y, scale


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
