from pydantic import BaseModel, Field


class BrightnessFilter(BaseModel):
    """Brightness filter for Fabric.js."""

    type: str = Field(default="Brightness", description="Filter type")
    brightness: float = Field(default=0, description="Brightness amount")

    class Config:
        extra = "allow"  # Allow additional fields for extensibility
