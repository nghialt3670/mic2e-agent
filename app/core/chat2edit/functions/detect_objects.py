from typing import List

from chat2edit.execution.decorators import (
    feedback_ignored_return_value,
    feedback_invalid_parameter_type,
    feedback_unexpected_error,
)
from chat2edit.execution.exceptions import FeedbackException
from chat2edit.prompting.stubbing.decorators import exclude_coroutine

from app.clients.inference_client import inference_client
from app.core.chat2edit.mic2e_feedbacks import (
    PromptBasedObjectDetectionQuantityMismatchFeedback,
)
from app.core.chat2edit.models import Image, Object
from app.core.chat2edit.utils.object_utils import create_object_from_image_and_mask


@feedback_ignored_return_value
@feedback_unexpected_error
@feedback_invalid_parameter_type
@exclude_coroutine
async def detect_objects(
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
    image.add_objects(objects)

    if len(generated_masks) != expected_quantity:
        raise FeedbackException(
            PromptBasedObjectDetectionQuantityMismatchFeedback(
                severity="error",
                prompt=prompt,
                expected_quantity=expected_quantity,
                detected_quantity=len(generated_masks),
                function="detect_objects",
                attachments=[image, *objects],
            )
        )

    return objects
