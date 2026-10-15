"""
CipherPage Token-Bucket & Sliding Window Rate Limiter
Conforms to SRS v2.2 SEC-02, CODE-03, AI-05, SEC-07
"""

import hashlib
import time
from collections import defaultdict
from typing import Callable, Dict, List, Tuple, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import redis
from app.core.config import settings

# Rate limit tiers: (max_requests, window_seconds)
TIERS: Dict[str, Tuple[int, int]] = {
    # Code submissions rate limit (CODE-03)
    "/api/v1/submissions/": (10, 60),
    # GenAI Coding Mentor & RAG Assistant (AI-05, SEC-07)
    "/api/v1/ai/mentor": (15, 60),
    "/api/v1/ai/learning-assistant": (15, 60),
    # Default General API tier
    "default": (120, 60)
}

class InMemoryRateLimiter:
    """Sliding-window request rate limiter with automatic TTL cleanup."""
    def __init__(self):
        # Maps (identifier, endpoint_tier) -> list of request timestamps
        self.history: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, identifier: str, endpoint: str) -> Tuple[bool, int, int, int]:
        """
        Check whether request is within rate limits.
        Returns: (allowed, remaining, limit, retry_after)
        """
        now = time.time()
        
        # Match endpoint to tier
        limit, window = TIERS.get("default")
        tier_key = "default"
        for prefix, tier in TIERS.items():
            if prefix != "default" and endpoint.startswith(prefix):
                limit, window = tier
                tier_key = prefix
                break

        key = f"{identifier}:{tier_key}"
        window_start = now - window

        # Purge timestamps outside the active window
        valid_timestamps = [ts for ts in self.history[key] if ts > window_start]
        self.history[key] = valid_timestamps

        count = len(valid_timestamps)
        if count >= limit:
            oldest = valid_timestamps[0]
            retry_after = max(1, int(window - (now - oldest)))
            return False, 0, limit, retry_after

        # Record this request
        self.history[key].append(now)
        remaining = max(0, limit - count - 1)
        return True, remaining, limit, 0

class SlidingWindowRateLimiter:
    """Redis-backed distributed sliding window rate limiter with in-memory fallback."""
    def __init__(self):
        self._in_memory = InMemoryRateLimiter()
        self._redis_client: Optional[redis.Redis] = None

    def _get_redis(self) -> Optional[redis.Redis]:
        if self._redis_client:
            try:
                self._redis_client.ping()
                return self._redis_client
            except Exception:
                self._redis_client = None
        try:
            self._redis_client = redis.from_url(settings.REDIS_URL, socket_timeout=1.0)
            self._redis_client.ping()
            return self._redis_client
        except Exception:
            return None

    def is_allowed(self, identifier: str, endpoint: str) -> Tuple[bool, int, int, int]:
        limit, window = TIERS.get("default")
        tier_key = "default"
        for prefix, tier in TIERS.items():
            if prefix != "default" and endpoint.startswith(prefix):
                limit, window = tier
                tier_key = prefix
                break

        r = self._get_redis()
        if not r:
            return self._in_memory.is_allowed(identifier, endpoint)

        try:
            now = time.time()
            redis_key = f"ratelimit:{tier_key}:{identifier}"
            pipe = r.pipeline()
            pipe.zremrangebyscore(redis_key, 0, now - window)
            pipe.zcard(redis_key)
            pipe.zadd(redis_key, {str(now): now})
            pipe.expire(redis_key, window + 5)
            results = pipe.execute()

            current_count = results[1]
            if current_count >= limit:
                oldest_entries = r.zrange(redis_key, 0, 0, withscores=True)
                retry_after = max(1, int(window - (now - oldest_entries[0][1]))) if oldest_entries else window
                return False, 0, limit, retry_after

            remaining = max(0, limit - current_count - 1)
            return True, remaining, limit, 0
        except Exception:
            return self._in_memory.is_allowed(identifier, endpoint)

limiter = SlidingWindowRateLimiter()

class RateLimitingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Ignore metrics, documentation, and health check endpoints
        if request.url.path in ("/metrics", "/health", "/docs", "/openapi.json"):
            return await call_next(request)

        # Identify client securely by SHA-256 token hash or Client IP
        auth_header = request.headers.get("authorization", "").strip()
        client_ip = request.client.host if request.client else "127.0.0.1"
        if auth_header:
            token_clean = auth_header.replace("Bearer ", "").strip()
            identifier = f"token:{hashlib.sha256(token_clean.encode('utf-8')).hexdigest()}"
        else:
            identifier = f"ip:{client_ip}"

        allowed, remaining, limit, retry_after = limiter.is_allowed(identifier, request.url.path)

        if not allowed:
            return JSONResponse(
                status_code=429,
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(retry_after)
                },
                content={
                    "detail": f"Rate limit exceeded ({limit} requests/min). Please try again in {retry_after} seconds.",
                    "code": "RATE_LIMIT_EXCEEDED"
                }
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
