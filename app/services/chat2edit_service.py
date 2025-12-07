from abc import ABC, abstractmethod

from app.schemas.chat2edit_schemas import (
    Chat2EditGenerateRequestModel,
    Chat2EditGenerateResponseModel,
)


class Chat2EditService(ABC):
    @abstractmethod
    async def generate(
        self, request: Chat2EditGenerateRequestModel
    ) -> Chat2EditGenerateResponseModel:
        pass
