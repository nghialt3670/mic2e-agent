from typing import Optional

from pydantic import BaseModel, Field

from app.utils.factories import create_color, create_uuid4


class Reference(BaseModel):
    label: str
    value: str = Field(default_factory=create_uuid4)
    color: str = Field(default_factory=create_color)


from app.core.chat2edit.models.variable import Variable


class Referent(Variable):
    reference: Optional[Reference] = Field(
        default=None, description="The reference of the referent"
    )
    ephemeral: bool = Field(
        default=False, description="Whether the referent is ephemeral"
    )
