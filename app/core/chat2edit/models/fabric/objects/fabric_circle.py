from typing import Literal

from pydantic import Field

from app.core.chat2edit.models.fabric.objects.fabric_object import FabricObject


class FabricCircle(FabricObject):
    """Circle object in Fabric.js."""

    type: Literal["Circle"] = Field(default="Circle", description="Object type")

    # Circle-specific properties
    radius: float = Field(default=0, description="Circle radius")
    startAngle: float = Field(default=0, description="Start angle in degrees")
    endAngle: float = Field(default=360, description="End angle in degrees")
    counterClockwise: bool = Field(default=False, description="Draw counter-clockwise")
