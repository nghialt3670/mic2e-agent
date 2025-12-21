from app.clients.redis_client import RedisClient, redis_client


def get_redis_client() -> RedisClient:
    """Dependency to get the Redis client."""
    return redis_client
