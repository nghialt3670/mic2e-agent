from typing import Annotated, ClassVar, List, Optional, Union

from PIL import ImageEnhance, ImageFilter, ImageOps
from PIL.Image import Image as PILImage
from pydantic import Field

from app.core.chat2edit.models.box import Box
from app.core.chat2edit.models.fabric.filters import FabricFilter
from app.core.chat2edit.models.fabric.filters.black_white_filter import BlackWhiteFilter
from app.core.chat2edit.models.fabric.filters.blur_filter import BlurFilter
from app.core.chat2edit.models.fabric.filters.brightness_filter import BrightnessFilter
from app.core.chat2edit.models.fabric.filters.contrast_filter import ContrastFilter
from app.core.chat2edit.models.fabric.filters.invert_filter import InvertFilter
from app.core.chat2edit.models.fabric.filters.saturation_filter import SaturationFilter
from app.core.chat2edit.models.fabric.objects import (
    FabricGroup,
    FabricImage,
    FabricObject,
)
from app.core.chat2edit.models.object import Object
from app.core.chat2edit.models.point import Point
from app.core.chat2edit.models.referent import Referent
from app.core.chat2edit.models.scribble import Scribble
from app.core.chat2edit.models.text import Text
from app.utils.factories import create_image_filename
from app.utils.image_utils import convert_data_url_to_image, convert_image_to_data_url

Entity: ClassVar = Annotated[
    Union["Image", Object, Box, Point, Scribble, Text], Field(discriminator="type")
]


def _apply_filter_to_pil_image(image: PILImage, filter: FabricFilter) -> PILImage:
    """
    Apply a filter to a PIL image.
    
    Filter values are in range [-1.0, 1.0], which corresponds to [-100%, +100%].
    """
    if isinstance(filter, BrightnessFilter):
        enhancer = ImageEnhance.Brightness(image)
        factor = 1.0 + filter.brightness  # brightness in [-1.0, 1.0] -> factor in [0.0, 2.0]
        return enhancer.enhance(factor)
    elif isinstance(filter, ContrastFilter):
        enhancer = ImageEnhance.Contrast(image)
        factor = 1.0 + filter.contrast  # contrast in [-1.0, 1.0] -> factor in [0.0, 2.0]
        return enhancer.enhance(factor)
    elif isinstance(filter, SaturationFilter):
        enhancer = ImageEnhance.Color(image)
        factor = 1.0 + filter.saturation  # saturation in [-1.0, 1.0] -> factor in [0.0, 2.0]
        return enhancer.enhance(factor)
    elif isinstance(filter, BlurFilter):
        # Blur filter value in [-1.0, 1.0] -> radius in [0, ~10]
        # Convert to positive radius (0 means no blur, positive means blur)
        radius = max(0, abs(filter.blur) * 10)
        if radius > 0:
            return image.filter(ImageFilter.GaussianBlur(radius=radius))
        return image
    elif isinstance(filter, InvertFilter):
        return ImageOps.invert(image.convert('RGB')).convert(image.mode)
    elif isinstance(filter, BlackWhiteFilter):
        return image.convert('L').convert('RGB')
    else:
        # Unknown filter type, return original image
        return image


class Image(FabricGroup, Referent):
    src: Optional[str] = Field(default=None, description="Image source URL or data")
    filename: str = Field(
        default_factory=create_image_filename, description="Image filename"
    )

    objects: List[Entity] = Field(
        default_factory=list, description="Child objects in the image"
    )
    
    aesthetic_feedback_given: bool = Field(
        default=False, 
        description="Track if aesthetic feedback has been given for this image"
    )

    def from_image(image: PILImage) -> "Image":
        base_image = FabricImage(
            src=convert_image_to_data_url(image), width=image.width, height=image.height
        )
        return Image(objects=[base_image])

    def set_image(self, image: PILImage) -> None:
        if len(self.objects) == 0 or not isinstance(self.objects[0], FabricImage):
            raise ValueError("No base image found")

        self.objects[0].src = convert_image_to_data_url(image)
        self.objects[0].width = image.width
        self.objects[0].height = image.height

    def get_image(self) -> PILImage:
        if len(self.objects) == 0 or not isinstance(self.objects[0], FabricImage):
            raise ValueError("No base image found")

        if not self.objects[0].src:
            raise ValueError("No image src found")

        # Get the base image
        pil_image = convert_data_url_to_image(self.objects[0].src)
        
        # Apply all filters in sequence
        base_image = self.objects[0]
        for filter in base_image.filters:
            pil_image = _apply_filter_to_pil_image(pil_image, filter)
        
        return pil_image

    def get_objects(self) -> List[FabricObject]:
        return self.objects[1:] if len(self.objects) > 1 else []

    def add_object(self, object: FabricObject) -> "Image":
        self.objects.append(object)
        return self

    def add_objects(self, objects: List[FabricObject]) -> "Image":
        self.objects.extend(objects)
        return self

    def remove_object(self, object: FabricObject) -> "Image":
        self.objects = [obj for obj in self.objects if obj.id != object.id]
        return self

    def remove_objects(self, objects: List[FabricObject]) -> "Image":
        object_ids = set([obj.id for obj in objects])
        self.objects = [obj for obj in self.objects if obj.id not in object_ids]
        return self

    def apply_filter(self, filter: FabricFilter) -> "Image":
        for object in self.objects:
            if isinstance(object, FabricImage):
                object.filters.append(filter)
            elif isinstance(object, Image):
                object.apply_filter(filter)

        return self
