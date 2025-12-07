from fastapi import APIRouter, Depends

from app.dependencies.chat2edit_dependencies import get_chat2edit_service
from app.schemas.chat2edit_schemas import (
    Chat2EditGenerateRequestModel,
    Chat2EditGenerateResponseModel,
)
from app.schemas.common_schemas import ResponseModel
from app.services.chat2edit_service import Chat2EditService

router = APIRouter(prefix="/chat2edit", tags=["chat2edit"])


@router.post("/generate", response_model=ResponseModel[Chat2EditGenerateResponseModel])
async def generate(
    request: Chat2EditGenerateRequestModel,
    service: Chat2EditService = Depends(get_chat2edit_service),
):
    return ResponseModel(data=await service.generate(request))
