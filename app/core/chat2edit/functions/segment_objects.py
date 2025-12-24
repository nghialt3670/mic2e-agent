from copy import deepcopy
from typing import List
from chat2edit.execution.signaling import set_feedback
from chat2edit.models import Feedback
from chat2edit.execution.decorators import (
    feedback_ignored_return_value,
    feedback_invalid_parameter_type,
    feedback_unexpected_error,
)
from chat2edit.prompting.stubbing.decorators import exclude_coroutine

from app.clients.inference_client import inference_client

from app.core.chat2edit.models import Box, Image, Object, Text
from app.core.chat2edit.utils.object_utils import create_object_from_image_and_mask
from app.core.chat2edit.utils import get_same_objects


@feedback_ignored_return_value
@feedback_unexpected_error
@feedback_invalid_parameter_type
@exclude_coroutine
async def segment_objects(
    image: Image, prompt: str, expected_quantity: int
) -> List[Object]:
    pil_image = image.get_image()
    generated_masks = await inference_client.sam3_generate_masks_by_text(
        pil_image, prompt
    )
    objects = [
        create_object_from_image_and_mask(pil_image, mask.image)
        for mask in generated_masks
    ]
    for obj in objects:
        obj.image_id = image.id

    image.remove_objects(get_same_objects(image, objects))
    image.add_objects(objects)

    if len(generated_masks) != expected_quantity:
        annotated_image = deepcopy(image)
        for i, obj in enumerate(objects):
            index = Text(
                text=f"{i + 1}",
                left=obj.left,
                top=obj.top,
                fontSize=min(obj.width, obj.height) / 2,
                fill="red",
            )
            bbox = Box(
                left=obj.left,
                top=obj.top,
                width=obj.width,
                height=obj.height,
                stroke="red",
                strokeWidth=min(obj.width, obj.height) / 20,
                fill="transparent",
            )
            annotated_image.add_object(index)
            annotated_image.add_object(bbox)

        # Persist a stable variable name on the annotated image so the context
        # strategy can use it when generating varnames.
        annotated_image.name = "annotated_image"

        set_feedback(
            Feedback(
                type="prompt_based_object_detection_quantity_mismatch",
                severity="warning",
                attachments=[annotated_image],
                details={
                    "prompt": prompt,
                    "expected_quantity": expected_quantity,
                    "detected_quantity": len(generated_masks),
                },
            )
        )

    return objects
