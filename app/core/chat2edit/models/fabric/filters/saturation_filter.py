from pydantic import BaseModel, Field


class SaturationFilter(BaseModel):
    """Saturation filter for Fabric.js."""

    type: str = Field(default="Saturation", description="Filter type")
    saturation: float = Field(default=0, description="Saturation amount")

    class Config:
        extra = "allow"  # Allow additional fields for extensibility
