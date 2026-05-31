from typing import List, Union

from PIL import Image as PILImage

from app.clients.inference_client import inference_client
from app.core.chat2edit.models.box import Box
from app.core.chat2edit.models.image import Image
from app.core.chat2edit.models.object import Object
from app.core.chat2edit.models.point import Point
from app.core.chat2edit.models.text import Text
from app.utils.image_utils import convert_data_url_to_image, expand_mask_image


async def inpaint_objects(image: Image, objects: List[Object]) -> Image:
    composite_mask = create_composite_mask(image, objects)
    expanded_mask = expand_mask_image(composite_mask)
    pil_image = image.get_image()

    inpainted_image = await inference_client.object_clear_inpaint(
        pil_image, expanded_mask, "remove the instance of the object"
    )
    image.set_image(inpainted_image)

    for object in objects:
        object.inpainted = True

    return image


async def inpaint_objects_with_prompt(
    image: Image, objects: List[Object], prompt: str
) -> Image:
    """Inpaint objects in an image using Stable Diffusion with a custom text prompt.

    Args:
        image: The image containing the objects to inpaint
        objects: List of objects to inpaint
        prompt: Text prompt describing what to generate in the masked areas

    Returns:
        Image with the objects inpainted according to the prompt
    """
    composite_mask = create_composite_mask(image, objects)
    expanded_mask = expand_mask_image(composite_mask)
    pil_image = image.get_image()

    inpainted_image = await inference_client.sd_inpaint(
        image=pil_image,
        mask=expanded_mask,
        prompt=prompt,
    )

    image.set_image(inpainted_image)

    for object in objects:
        object.inpainted = True

    return image


async def inpaint_uninpainted_objects_in_entities(
    image: Image, entities: List[Union[Image, Object, Text, Box, Point]]
) -> Image:
    objects_to_inpaint = [
        entity
        for entity in entities
        if isinstance(entity, Object)
        and not entity.inpainted
        and entity.image_id == image.id
    ]

    if len(objects_to_inpaint) > 0:
        image = await inpaint_objects(image, objects_to_inpaint)

    return image


def create_composite_mask(image: Image, objects: List[Object]) -> PILImage.Image:
    if not objects:
        raise ValueError("Cannot create mask from empty object list")

    mask = PILImage.new("L", (int(image.width), int(image.height)), 0)
    for object in objects:
        object_image = convert_data_url_to_image(object.src)
        object_mask = object_image.convert("RGBA").getchannel("A")
        mask.paste(
            object_mask,
            (int(object.left - object.width / 2 + image.width / 2), int(object.top - object.height / 2 + image.height / 2)),
        )

    return mask
