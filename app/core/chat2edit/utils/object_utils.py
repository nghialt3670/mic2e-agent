from PIL import Image

from app.core.chat2edit.models import Object
from app.utils.image_utils import convert_image_to_data_url


def create_object_from_image_and_mask(
    image: Image.Image,
    mask: Image.Image,
) -> Object:
    bbox = mask.getbbox()
    obj_width = bbox[2] - bbox[0]
    obj_height = bbox[3] - bbox[1]
    obj_image = Image.new("RGBA", (obj_width, obj_height), (0, 0, 0, 0))
    obj_image.paste(image.crop(bbox), (0, 0), mask.crop(bbox))

    obj = Object()
    obj.src = convert_image_to_data_url(obj_image)
    obj.width = obj_width
    obj.height = obj_height
    obj.left = bbox[0] + obj_width / 2 - image.width / 2
    obj.top = bbox[1] + obj_height / 2 - image.height / 2

    return obj
