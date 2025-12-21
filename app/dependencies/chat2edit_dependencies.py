from fastapi import Request

from app.clients.storage_client import storage_client
from app.dependencies.redis_dependencies import get_redis_client
from app.services.chat2edit_service import Chat2EditService
from app.services.impl.chat2edit_service_impl import Chat2EditServiceImpl


def get_chat2edit_service(request: Request) -> Chat2EditService:
    return Chat2EditServiceImpl(storage_client, get_redis_client())
