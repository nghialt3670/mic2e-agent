from pydantic import BaseModel, Field


class BlurFilter(BaseModel):
    """Blur filter for Fabric.js."""

    type: str = Field(default="Blur", description="Filter type")
    blur: float = Field(default=0, description="Blur amount")

    class Config:
        extra = "allow"  # Allow additional fields for extensibility
