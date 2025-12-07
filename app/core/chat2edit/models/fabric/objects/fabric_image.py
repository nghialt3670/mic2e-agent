from typing import List, Literal, Optional

from pydantic import Field

from app.core.chat2edit.models.fabric.filters import FabricFilter
from app.core.chat2edit.models.fabric.objects.fabric_object import FabricObject


class FabricImage(FabricObject):
    """Image object in Fabric.js."""

    type: Literal["Image"] = Field(default="Image", description="Object type")

    # Image source
    src: str = Field(default="", description="Image source URL or data")
    crossOrigin: Optional[str] = Field(default=None, description="CORS setting")

    # Image cropping
    cropX: float = Field(default=0, description="Crop X position")
    cropY: float = Field(default=0, description="Crop Y position")

    # Image filters
    filters: List[FabricFilter] = Field(
        default_factory=list, description="Image filters"
    )

    # Override default dimensions
    width: float = Field(default=200, description="Image width")
    height: float = Field(default=300, description="Image height")
