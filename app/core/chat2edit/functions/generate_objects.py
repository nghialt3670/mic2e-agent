from typing import List

from chat2edit.execution.decorators import (
    deepcopy_parameter,
    feedback_empty_list_parameters,
    feedback_ignored_return_value,
    feedback_invalid_parameter_type,
    feedback_unexpected_error,
    feedback_mismatch_list_parameters,
)
from chat2edit.prompting.stubbing.decorators import exclude_coroutine

from app.clients.inference_client import inference_client
from app.core.chat2edit.models import Box, Image


@feedback_ignored_return_value
@feedback_unexpected_error
@feedback_invalid_parameter_type
@feedback_empty_list_parameters(["phrases", "locations"])
@feedback_mismatch_list_parameters(["phrases", "locations"])
@exclude_coroutine
@deepcopy_parameter("image")
async def generate_objects(
    image: Image,
    prompt: str,
    phrases: List[str],
    locations: List[Box],
) -> Image:
    pil_image = image.get_image()
    img_width = pil_image.width
    img_height = pil_image.height

    normalized_locations = []

    for location in locations:
        adjusted_left = location.left + img_width / 2
        adjusted_top = location.top + img_height / 2

        x_min = adjusted_left
        y_min = adjusted_top
        x_max = adjusted_left + location.width
        y_max = adjusted_top + location.height

        normalized_box = [
            max(0.0, min(1.0, x_min / img_width)),
            max(0.0, min(1.0, y_min / img_height)),
            max(0.0, min(1.0, x_max / img_width)),
            max(0.0, min(1.0, y_max / img_height)),
        ]
        normalized_locations.append(normalized_box)

    result_image = await inference_client.gligen_inpaint(
        image=pil_image,
        prompt=prompt,
        phrases=phrases,
        locations=normalized_locations,
        seed=42,
    )

    image.set_image(result_image)
    return image
