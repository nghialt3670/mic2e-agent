from typing import Optional

from pydantic import BaseModel, Field


class Variable(BaseModel):
    """Base model for values that carry a stable variable name for contextualization."""

    name: Optional[str] = Field(
        default=None, description="Explicit variable name used in context"
    )


