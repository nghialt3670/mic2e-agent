import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # No Redis initialization needed here - it's handled in redis_client.py
    logger.info("Application startup")

    yield

    # Cleanup if needed
    logger.info("Application shutdown")
