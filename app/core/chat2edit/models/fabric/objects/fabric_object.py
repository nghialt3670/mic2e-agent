from typing import Optional

from pydantic import BaseModel, Field

from app.utils.factories import create_uuid4


class FabricObject(BaseModel):
    """Base class for all Fabric.js objects."""

    # Custom fields
    id: str = Field(default_factory=create_uuid4, description="Object id")

    # Fabric.js fields
    # Type and version
    type: str = Field(default="FabricObject", description="Object type")
    version: str = Field(default="6.7.1", description="Fabric.js version")

    # Position and dimensions
    originX: str = Field(default="center", description="Horizontal origin")
    originY: str = Field(default="center", description="Vertical origin")
    left: float = Field(default=0, description="Left position")
    top: float = Field(default=0, description="Top position")
    width: float = Field(default=0, description="Object width")
    height: float = Field(default=0, description="Object height")

    # Fill and stroke
    fill: str = Field(default="rgb(0,0,0)", description="Fill color")
    stroke: Optional[str] = Field(default=None, description="Stroke color")
    strokeWidth: float = Field(default=1, description="Stroke width")
    strokeDashArray: Optional[list] = Field(
        default=None, description="Stroke dash pattern"
    )
    strokeLineCap: str = Field(default="butt", description="Stroke line cap")
    strokeDashOffset: float = Field(default=0, description="Stroke dash offset")
    strokeLineJoin: str = Field(default="miter", description="Stroke line join")
    strokeUniform: bool = Field(default=False, description="Uniform stroke scaling")
    strokeMiterLimit: float = Field(default=4, description="Stroke miter limit")

    # Transform
    scaleX: float = Field(default=1, description="Horizontal scale")
    scaleY: float = Field(default=1, description="Vertical scale")
    angle: float = Field(default=0, description="Rotation angle")
    flipX: bool = Field(default=False, description="Horizontal flip")
    flipY: bool = Field(default=False, description="Vertical flip")
    skewX: float = Field(default=0, description="Horizontal skew")
    skewY: float = Field(default=0, description="Vertical skew")

    # Appearance
    opacity: float = Field(default=1, description="Opacity (0-1)")
    shadow: Optional[dict] = Field(default=None, description="Shadow properties")
    visible: bool = Field(default=True, description="Visibility")
    backgroundColor: str = Field(default="", description="Background color")

    # Rendering
    fillRule: str = Field(default="nonzero", description="Fill rule")
    paintFirst: str = Field(default="fill", description="Paint order")
    globalCompositeOperation: str = Field(
        default="source-over", description="Composite operation"
    )

    class Config:
        extra = "allow"  # Allow additional fields for extensibility
