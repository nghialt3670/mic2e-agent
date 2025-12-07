from pydantic import BaseModel, Field


class BaseFilter(BaseModel):
    """Base class for all Fabric.js filters."""

    type: str = Field(default="BaseFilter", description="Filter type")

    class Config:
        extra = "allow"  # Allow additional fields for extensibility
