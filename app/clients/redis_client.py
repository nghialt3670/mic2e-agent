import json
from typing import Any, Dict, Optional
from redis.asyncio import Redis

from app.env import REDIS_HOST, REDIS_PORT


class RedisClient:
    """Redis client for storing and retrieving Chat2Edit progress events."""

    def __init__(self, host: str, port: int):
        self._redis_host = host
        self._redis_port = port
        self._redis = Redis(
            host=self._redis_host, port=self._redis_port, decode_responses=False
        )
        self._progress_prefix = "chat2edit:progress:"
        self._progress_ttl = 3600

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._redis.close()

    async def publish_progress(
        self,
        cycle_id: str,
        event_type: str,
        message: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Publish a progress event for a cycle."""
        event = {
            "type": event_type,
            "message": message,
            "data": data,
        }
        # Use both list (for history) and pubsub (for real-time)
        key = f"{self._progress_prefix}{cycle_id}"

        # Store in list for retrieval
        await self._redis.rpush(key, json.dumps(event))
        await self._redis.expire(key, self._progress_ttl)

        # Publish to channel for WebSocket listeners
        await self._redis.publish(
            f"{self._progress_prefix}channel:{cycle_id}", json.dumps(event)
        )

    async def get_progress_history(self, cycle_id: str) -> list[Dict[str, Any]]:
        """Get all progress events for a cycle."""
        key = f"{self._progress_prefix}{cycle_id}"
        events = await self._redis.lrange(key, 0, -1)
        return [json.loads(event) for event in events]

    async def clear_progress(self, cycle_id: str) -> None:
        """Clear progress data for a cycle."""
        key = f"{self._progress_prefix}{cycle_id}"
        await self._redis.delete(key)

    async def subscribe_to_progress(self, cycle_id: str):
        """Subscribe to progress updates for a cycle. Returns a pubsub object."""
        pubsub = self._redis.pubsub()
        channel = f"{self._progress_prefix}channel:{cycle_id}"
        await pubsub.subscribe(channel)
        return pubsub

    async def close(self) -> None:
        """Close the Redis connection."""
        await self._redis.close()


# Global Redis client instance
redis_client = RedisClient(REDIS_HOST, REDIS_PORT)
