from typing import List, Literal, Union

from pydantic import Field

from app.core.chat2edit.models.fabric.objects.fabric_object import FabricObject


class FabricPath(FabricObject):
    """Path object in Fabric.js (used for scribbles and custom paths)."""

    type: Literal["Path"] = Field(default="Path", description="Object type")

    # Path-specific properties
    # Path can be either:
    # 1. SVG path string (e.g., "M 100 200 L 150 250 Q 200 200 250 250")
    # 2. List of command arrays where each command is a list with command type and coordinates
    #    Examples:
    #      ["M", x, y] - Move to point
    #      ["L", x, y] - Line to point
    #      ["Q", x1, y1, x2, y2] - Quadratic curve to point
    path: Union[str, List[List[Union[str, float]]]] = Field(
        default="", description="Path commands as SVG string or list of command arrays"
    )
