from chat2edit.execution.decorators import (
    feedback_ignored_return_value,
    feedback_invalid_parameter_type,
    feedback_unexpected_error,
)
from chat2edit.prompting.stubbing.decorators import exclude_coroutine
from rembg import remove

from app.clients.inference_client import inference_client
from app.core.chat2edit.models import Object
from app.core.chat2edit.utils.object_utils import create_object_from_image_and_mask


@feedback_ignored_return_value
@feedback_unexpected_error
@feedback_invalid_parameter_type
@exclude_coroutine
async def generate_object(prompt: str) -> Object:
    # Generate image using Flux
    generated_image = await inference_client.flux_generate(prompt)
    
    # Remove background using rembg to get the main object
    # rembg returns an RGBA image with transparent background
    object_image = remove(generated_image)
    
    # Convert RGBA to mask (alpha channel)
    mask = object_image.split()[-1]  # Get alpha channel as mask
    
    # Create object from the generated image and mask
    obj = create_object_from_image_and_mask(object_image.convert("RGB"), mask)
    
    return obj

