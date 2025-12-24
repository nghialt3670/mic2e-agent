from typing import List, Optional

from chat2edit.execution.decorators import (
    feedback_ignored_return_value,
    feedback_invalid_parameter_type,
    feedback_missing_all_optional_parameters,
    feedback_unexpected_error,
)
from chat2edit.prompting.stubbing.decorators import exclude_coroutine

from app.clients.inference_client import inference_client
from app.core.chat2edit.models import Box, Image, Object, Point, Scribble
from app.core.chat2edit.utils.object_utils import create_object_from_image_and_mask
from app.core.chat2edit.utils.scribble_utils import convert_scribble_to_mask_image
from app.schemas.common_schemas import Box as InferenceBox
from app.schemas.common_schemas import MaskLabeledPoint
from app.utils.image_utils import convert_mask_image_to_points
from app.core.chat2edit.utils import get_same_objects


@feedback_ignored_return_value
@feedback_unexpected_error
@feedback_invalid_parameter_type
@feedback_missing_all_optional_parameters(
    [
        "box",
        "positive_points",
        "negative_points",
        "positive_scribble",
        "negative_scribble",
    ]
)
@exclude_coroutine
async def segment_object(
    image: Image,
    box: Optional[Box] = None,
    positive_points: Optional[List[Point]] = None,
    negative_points: Optional[List[Point]] = None,
    positive_scribble: Optional[Scribble] = None,
    negative_scribble: Optional[Scribble] = None,
) -> Object:
    pil_image = image.get_image()
    img_width = pil_image.width
    img_height = pil_image.height

    inference_box = None
    points = []

    if box is not None:
        adjusted_left = int(box.left + img_width / 2)
        adjusted_top = int(box.top + img_height / 2)
        adjusted_right = int(adjusted_left + box.width)
        adjusted_bottom = int(adjusted_top + box.height)

        inference_box = InferenceBox(
            x_min=adjusted_left,
            y_min=adjusted_top,
            x_max=adjusted_right,
            y_max=adjusted_bottom,
        )

    if positive_points:
        for point in positive_points:
            x = int(point.left + img_width / 2)
            y = int(point.top + img_height / 2)
            points.append(MaskLabeledPoint(x=x, y=y, label=1))

    if negative_points:
        for point in negative_points:
            x = int(point.left + img_width / 2)
            y = int(point.top + img_height / 2)
            points.append(MaskLabeledPoint(x=x, y=y, label=0))

    if positive_scribble:
        scribble_mask = convert_scribble_to_mask_image(positive_scribble, image)
        scribble_points = convert_mask_image_to_points(scribble_mask)
        for x, y in scribble_points:
            points.append(MaskLabeledPoint(x=x, y=y, label=1))

    if negative_scribble:
        scribble_mask = convert_scribble_to_mask_image(negative_scribble, image)
        scribble_points = convert_mask_image_to_points(scribble_mask)
        for x, y in scribble_points:
            points.append(MaskLabeledPoint(x=x, y=y, label=0))

    mask = await inference_client.sam3_generate_mask(
        pil_image,
        points=points if points else None,
        box=inference_box,
    )

    obj = create_object_from_image_and_mask(pil_image, mask)
    obj.image_id = image.id

    image.remove_objects(get_same_objects(image, [obj]))
    image.add_object(obj)
    
    return obj
