from pydantic import BaseModel, Field


class InvertFilter(BaseModel):
    """Invert filter for Fabric.js."""

    type: str = Field(default="Invert", description="Filter type")
    alpha: bool = Field(default=False, description="Invert alpha channel")
    invert: bool = Field(default=True, description="Invert colors")

    class Config:
        extra = "allow"  # Allow additional fields for extensibility
