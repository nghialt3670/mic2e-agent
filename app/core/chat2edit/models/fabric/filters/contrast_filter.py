from pydantic import BaseModel, Field


class ContrastFilter(BaseModel):
    """Contrast filter for Fabric.js."""

    type: str = Field(default="Contrast", description="Filter type")
    contrast: float = Field(default=0, description="Contrast amount")

    class Config:
        extra = "allow"  # Allow additional fields for extensibility
