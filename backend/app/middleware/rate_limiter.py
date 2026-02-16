"""Redis-based token bucket rate limiter middleware."""

import time
import asyncio
from typing import Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from app.config import settings


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Token bucket rate limiter using Redis."""

    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.redis_client: Optional[object] = None
        self._initialized = False

    async def _init_redis(self):
        if self._initialized:
            return
        self._initialized = True
        if REDIS_AVAILABLE:
            try:
                self.redis_client = aioredis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=2,
                )
                await self.redis_client.ping()
            except Exception:
                self.redis_client = None

    async def dispatch(self, request: Request, call_next):
        await self._init_redis()

        # Skip rate limiting if Redis is not available
        if self.redis_client is None:
            return await call_next(request)

        # Use IP + path as rate limit key
        client_ip = request.client.host if request.client else "unknown"
        key = f"rate_limit:{client_ip}:{request.url.path}"

        try:
            # Token bucket: check current count
            current = await self.redis_client.get(key)
            if current is not None and int(current) >= self.requests_per_minute:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded. Please try again later."},
                )

            # Increment counter with TTL
            pipe = self.redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, 60)
            await pipe.execute()
        except Exception:
            # Fail open — don't block requests if Redis has issues
            pass

        return await call_next(request)
