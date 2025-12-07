from typing import Union

from app.core.chat2edit.models.fabric.filters.base_filter import BaseFilter
from app.core.chat2edit.models.fabric.filters.black_white_filter import BlackWhiteFilter
from app.core.chat2edit.models.fabric.filters.blur_filter import BlurFilter
from app.core.chat2edit.models.fabric.filters.brightness_filter import BrightnessFilter
from app.core.chat2edit.models.fabric.filters.contrast_filter import ContrastFilter
from app.core.chat2edit.models.fabric.filters.invert_filter import InvertFilter
from app.core.chat2edit.models.fabric.filters.saturation_filter import SaturationFilter

FabricFilter = Union[
    BaseFilter,
    BlackWhiteFilter,
    BlurFilter,
    BrightnessFilter,
    ContrastFilter,
    InvertFilter,
    SaturationFilter,
]

__all__ = [
    "BaseFilter",
    "BlackWhiteFilter",
    "BlurFilter",
    "BrightnessFilter",
    "ContrastFilter",
    "InvertFilter",
    "SaturationFilter",
]
