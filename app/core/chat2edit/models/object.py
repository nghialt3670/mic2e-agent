from typing import Dict, List, Tuple

from pydantic import Field

from app.core.chat2edit.models.fabric.objects import FabricImage
from app.core.chat2edit.models.referent import Referent


class Object(FabricImage, Referent):
    inpainted: bool = Field(
        default=False, description="Whether the object is inpainted"
    )
