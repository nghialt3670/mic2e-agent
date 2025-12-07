from typing import List, Literal

from pydantic import Field

from app.core.chat2edit.models.fabric.objects.fabric_object import FabricObject


class FabricText(FabricObject):
    """Text object in Fabric.js."""

    type: Literal["Text"] = Field(default="Text", description="Object type")

    # Text content
    text: str = Field(default="Hello, world!", description="Text content")

    # Font properties
    fontSize: float = Field(default=40, description="Font size")
    fontWeight: str = Field(default="normal", description="Font weight")
    fontFamily: str = Field(default="Times New Roman", description="Font family")
    fontStyle: str = Field(default="normal", description="Font style")
    lineHeight: float = Field(default=1.16, description="Line height")

    # Text styling
    charSpacing: float = Field(default=0, description="Character spacing")
    textAlign: str = Field(default="left", description="Text alignment")
    underline: bool = Field(default=False, description="Underline")
    overline: bool = Field(default=False, description="Overline")
    linethrough: bool = Field(default=False, description="Line through")
    textBackgroundColor: str = Field(default="", description="Text background color")

    # Advanced text properties
    styles: List = Field(default_factory=list, description="Character styles")
    pathStartOffset: float = Field(default=0, description="Path start offset")
    pathSide: str = Field(default="left", description="Path side")
    pathAlign: str = Field(default="baseline", description="Path alignment")
    direction: str = Field(default="ltr", description="Text direction")
    textDecorationThickness: float = Field(
        default=66.667, description="Text decoration thickness"
    )
