from typing import List, Literal, Optional, Union

from chat2edit.execution.decorators import (
    deepcopy_parameter,
    feedback_empty_list_parameters,
    feedback_ignored_return_value,
    feedback_invalid_parameter_type,
    feedback_unexpected_error,
)

from app.core.chat2edit.models import Image, Object
from app.core.chat2edit.models.fabric.filters import (
    BlackWhiteFilter,
    BlurFilter,
    BrightnessFilter,
    ContrastFilter,
    InvertFilter,
    SaturationFilter,
)
from app.core.chat2edit.utils import get_own_objects


@feedback_ignored_return_value
@deepcopy_parameter("image")
@feedback_unexpected_error
@feedback_invalid_parameter_type
@feedback_empty_list_parameters(["entities"])
def apply_filter(
    image: Image,
    filter_name: Literal[
        "blackWhite", "blur", "brightness", "contrast", "invert", "saturation"
    ],
    filter_value: Optional[float] = None,
    entities: Optional[List[Union[Image, Object]]] = None,
) -> Image:
    filter_obj = None

    if filter_name == "blackWhite":
        filter_obj = BlackWhiteFilter()
    elif filter_name == "blur":
        blur_value = filter_value if filter_value is not None else 0
        filter_obj = BlurFilter(blur=blur_value)
    elif filter_name == "brightness":
        brightness_value = filter_value if filter_value is not None else 0
        filter_obj = BrightnessFilter(brightness=brightness_value)
    elif filter_name == "contrast":
        contrast_value = filter_value if filter_value is not None else 0
        filter_obj = ContrastFilter(contrast=contrast_value)
    elif filter_name == "invert":
        filter_obj = InvertFilter()
    elif filter_name == "saturation":
        saturation_value = filter_value if filter_value is not None else 0
        filter_obj = SaturationFilter(saturation=saturation_value)

    if entities:
        own_objects = get_own_objects(image.get_objects())
        for obj in own_objects:
            if isinstance(obj, Image):
                obj.apply_filter(filter_obj)
            elif isinstance(obj, Object):
                obj.filters.append(filter_obj)
    else:
        image = image.apply_filter(filter_obj)

    return image
