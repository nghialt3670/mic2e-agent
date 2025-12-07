from typing import Generic, Literal, Optional, TypeVar

from PIL import Image
from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    code: int = Field(default=200)
    message: Optional[str] = Field(default=None)
    data: T = Field()


class Point(BaseModel):
    x: int
    y: int


class Box(BaseModel):
    x_min: int
    y_min: int
    x_max: int
    y_max: int


class MaskLabeledPoint(Point):
    label: Literal[0, 1] = 1


class GeneratedMask(BaseModel):
    image: Image.Image
    score: float

    class Config:
        arbitrary_types_allowed = True
