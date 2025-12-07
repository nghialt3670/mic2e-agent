from typing import Annotated, ClassVar, List, Literal, Union

from pydantic import BaseModel, Field

from app.core.chat2edit.models.fabric.objects.fabric_circle import FabricCircle
from app.core.chat2edit.models.fabric.objects.fabric_image import FabricImage
from app.core.chat2edit.models.fabric.objects.fabric_object import FabricObject
from app.core.chat2edit.models.fabric.objects.fabric_path import FabricPath
from app.core.chat2edit.models.fabric.objects.fabric_rect import FabricRect
from app.core.chat2edit.models.fabric.objects.fabric_text import FabricText


class LayoutManager(BaseModel):
    """Layout manager for group objects."""

    type: str = Field(default="layoutManager", description="Layout manager type")
    strategy: str = Field(default="fit-content", description="Layout strategy")


class FabricGroup(FabricObject):
    """Group object in Fabric.js that contains multiple objects."""

    type: Literal["Group"] = Field(default="Group", description="Object type")

    # Group-specific properties
    subTargetCheck: bool = Field(
        default=False, description="Enable sub-target checking"
    )
    interactive: bool = Field(default=False, description="Interactive group")

    # Layout management
    layoutManager: LayoutManager = Field(
        default_factory=LayoutManager, description="Layout manager configuration"
    )

    # Child objects
    FabricChild: ClassVar = Annotated[
        Union[
            FabricCircle,
            FabricImage,
            FabricPath,
            FabricRect,
            FabricText,
        ],
        Field(discriminator="type"),
    ]

    objects: List[FabricChild] = Field(
        default_factory=list, description="Child objects in the group"
    )

    # Override default stroke
    stroke: None = Field(default=None, description="Stroke color")
    strokeWidth: float = Field(default=0, description="Stroke width")
