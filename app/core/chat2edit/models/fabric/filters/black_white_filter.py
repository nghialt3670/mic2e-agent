from pydantic import BaseModel, Field


class BlackWhiteFilter(BaseModel):
    """Black and white filter for Fabric.js."""

    type: str = Field(default="BlackWhite", description="Filter type")
    colorsOnly: bool = Field(default=False, description="Apply only to colors")

    class Config:
        extra = "allow"  # Allow additional fields for extensibility
