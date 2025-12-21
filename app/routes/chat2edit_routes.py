import asyncio
import json
import logging

from typing import List

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.clients.redis_client import RedisClient
from app.dependencies.chat2edit_dependencies import get_chat2edit_service
from app.dependencies.redis_dependencies import get_redis_client
from app.schemas.chat2edit_schemas import (
    Chat2EditGenerateRequestModel,
    Chat2EditGenerateResponseModel,
    Chat2EditProgressEventModel,
)
from app.schemas.common_schemas import ResponseModel
from app.services.chat2edit_service import Chat2EditService

router = APIRouter(prefix="/chat2edit", tags=["chat2edit"])
logger = logging.getLogger(__name__)


@router.post("/generate", response_model=ResponseModel[Chat2EditGenerateResponseModel])
async def generate(
    request: Chat2EditGenerateRequestModel,
    service: Chat2EditService = Depends(get_chat2edit_service),
):
    return ResponseModel(data=await service.generate(request))


@router.post("/generate/{cycle_id}")
async def generate_with_progress(
    cycle_id: str,
    request: Chat2EditGenerateRequestModel,
    service: Chat2EditService = Depends(get_chat2edit_service),
):
    """Start generation with progress tracking. Progress can be monitored via WebSocket."""
    # Start generation in background task
    asyncio.create_task(service.generate(request, cycle_id))
    return ResponseModel(
        data={
            "cycle_id": cycle_id,
            "message": "Generation started. Connect to WebSocket for progress.",
        }
    )


@router.websocket("/progress/{cycle_id}")
async def websocket_progress(
    websocket: WebSocket,
    cycle_id: str,
    redis_client: RedisClient = Depends(get_redis_client),
):
    """WebSocket endpoint for streaming Chat2Edit progress by cycle ID."""
    await websocket.accept()
    logger.info(f"WebSocket connected for cycle {cycle_id}")

    pubsub = None
    try:
        # Send any existing progress history first
        history = await redis_client.get_progress_history(cycle_id)
        for event in history:
            await websocket.send_json(event)

        # Subscribe to new progress updates
        pubsub = await redis_client.subscribe_to_progress(cycle_id)

        # Listen for new messages
        while True:
            message = await pubsub.get_message(
                ignore_subscribe_messages=True, timeout=30
            )
            if message and message["type"] == "message":
                event = json.loads(message["data"])
                await websocket.send_json(event)

                # Close connection after complete or error event
                if event.get("type") in ["complete", "error"]:
                    logger.info(
                        f"Generation finished for cycle {cycle_id}, closing WebSocket"
                    )
                    break

            # Check if WebSocket is still connected
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
            except asyncio.TimeoutError:
                pass
            except:
                # Client disconnected
                break

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for cycle {cycle_id}")
    except Exception as e:
        logger.error(f"WebSocket error for cycle {cycle_id}: {e}")
        try:
            await websocket.send_json(
                {
                    "type": "error",
                    "message": str(e),
                }
            )
        except:
            pass
    finally:
        if pubsub:
            await pubsub.unsubscribe()
            await pubsub.close()
        try:
            await websocket.close()
        except:
            pass
        logger.info(f"WebSocket cleanup completed for cycle {cycle_id}")


@router.get(
    "/progress/{cycle_id}",
    response_model=ResponseModel[List[Chat2EditProgressEventModel]],
)
async def get_progress(
    cycle_id: str,
    redis_client: RedisClient = Depends(get_redis_client),
):
    """
    Polling endpoint to fetch all progress events for a given cycle.

    The frontend can call this endpoint periodically to get real-time updates
    without using WebSockets.
    """
    events = await redis_client.get_progress_history(cycle_id)
    # events are already JSON-serializable dicts compatible with Chat2EditProgressEventModel
    # Just wrap them in the standard ResponseModel
    return ResponseModel[List[Chat2EditProgressEventModel]](data=events)
