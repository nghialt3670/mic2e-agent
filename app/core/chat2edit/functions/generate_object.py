from chat2edit.execution.decorators import (
    deepcopy_parameter,
    feedback_ignored_return_value,
    feedback_invalid_parameter_type,
    feedback_unexpected_error,
)
from chat2edit.prompting.stubbing.decorators import exclude_coroutine

from app.clients.inference_client import inference_client
from app.core.chat2edit.models import Image, Scribble
from app.core.chat2edit.utils.object_utils import create_object_from_image_and_mask
from app.core.chat2edit.utils.scribble_utils import convert_scribble_to_mask_image
from app.utils.image_utils import convert_data_url_to_image, expand_mask_image


@feedback_ignored_return_value
@deepcopy_parameter("image")
@feedback_unexpected_error
@feedback_invalid_parameter_type
@exclude_coroutine
async def generate_object(image: Image, prompt: str, location: Scribble) -> Image:
    mask = convert_scribble_to_mask_image(location, image)
    expanded_mask = expand_mask_image(mask)
    pil_image = image.get_image()
    inpainted_image = await inference_client.sd_inpaint(
        image=pil_image,
        mask=expanded_mask,
        prompt=prompt,
    )
    obj = create_object_from_image_and_mask(inpainted_image, mask)
    obj.left -= pil_image.width / 2
    obj.top -= pil_image.height / 2
    image.add_object(obj)
    return image
