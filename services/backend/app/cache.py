"""
Response caching with Redis
"""
import json
import hashlib
from functools import wraps
from typing import Optional, Callable, Any
from fastapi import Request, Response
from redis import asyncio as aioredis
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Global Redis client
redis_client: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    """Get Redis client instance."""
    global redis_client
    if redis_client is None:
        redis_client = await aioredis.from_url(
            settings.redis_url,
            decode_responses=True,
            encoding="utf-8"
        )
    return redis_client


async def close_redis():
    """Close Redis connection."""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None


def generate_cache_key(request: Request, prefix: str = "cache") -> str:
    """
    Generate a cache key based on request path and query parameters.
    
    Args:
        request: FastAPI request object
        prefix: Cache key prefix
        
    Returns:
        Cache key string
    """
    # Include path and query params in cache key
    key_data = f"{request.url.path}?{request.url.query}"
    key_hash = hashlib.md5(key_data.encode()).hexdigest()
    return f"{prefix}:{key_hash}"


async def get_cached_response(cache_key: str) -> Optional[dict]:
    """
    Get cached response from Redis.
    
    Args:
        cache_key: Cache key
        
    Returns:
        Cached data or None
    """
    try:
        redis = await get_redis()
        cached = await redis.get(cache_key)
        if cached:
            logger.debug(f"Cache hit: {cache_key}")
            return json.loads(cached)
        logger.debug(f"Cache miss: {cache_key}")
        return None
    except Exception as e:
        logger.error(f"Redis get error: {e}")
        return None


async def set_cached_response(
    cache_key: str,
    data: Any,
    expire: int = 300
) -> bool:
    """
    Store response in Redis cache.
    
    Args:
        cache_key: Cache key
        data: Data to cache
        expire: Expiration time in seconds
        
    Returns:
        True if successful
    """
    try:
        redis = await get_redis()
        serialized = json.dumps(data, default=str)
        await redis.setex(cache_key, expire, serialized)
        logger.debug(f"Cached: {cache_key} (expires in {expire}s)")
        return True
    except Exception as e:
        logger.error(f"Redis set error: {e}")
        return False


async def invalidate_cache_pattern(pattern: str) -> int:
    """
    Invalidate all cache keys matching a pattern.
    
    Args:
        pattern: Redis key pattern (e.g., "cache:stock:*")
        
    Returns:
        Number of keys deleted
    """
    try:
        redis = await get_redis()
        keys = await redis.keys(pattern)
        if keys:
            deleted = await redis.delete(*keys)
            logger.info(f"Invalidated {deleted} cache keys matching: {pattern}")
            return deleted
        return 0
    except Exception as e:
        logger.error(f"Redis invalidate error: {e}")
        return 0


def cache_response(expire: int = 300, key_prefix: str = "cache"):
    """
    Decorator to cache FastAPI route responses.
    
    Args:
        expire: Cache expiration time in seconds
        key_prefix: Cache key prefix
        
    Usage:
        @router.get("/api/v1/stock/levels")
        @cache_response(expire=60, key_prefix="stock")
        async def get_stock_levels(...):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from kwargs
            request: Optional[Request] = kwargs.get('request')
            if not request:
                # No request object, can't cache
                return await func(*args, **kwargs)
            
            # Generate cache key
            cache_key = generate_cache_key(request, prefix=key_prefix)
            
            # Try to get from cache
            cached_data = await get_cached_response(cache_key)
            if cached_data is not None:
                return cached_data
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache the result
            await set_cached_response(cache_key, result, expire=expire)
            
            return result
        return wrapper
    return decorator


# Cache invalidation helpers

async def invalidate_stock_cache():
    """Invalidate all stock-related caches."""
    await invalidate_cache_pattern("cache:stock:*")
    await invalidate_cache_pattern("cache:/api/v1/stock/*")


async def invalidate_sku_cache():
    """Invalidate all SKU-related caches."""
    await invalidate_cache_pattern("cache:sku:*")
    await invalidate_cache_pattern("cache:/api/v1/skus*")


async def invalidate_inventory_cache():
    """Invalidate all inventory-related caches."""
    await invalidate_cache_pattern("cache:inventory:*")
    await invalidate_cache_pattern("cache:/api/v1/inventory*")
