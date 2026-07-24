"""
Rate Limiting Middleware.
Simple in-memory token bucket rate limiter for API endpoints.
"""
import time
import logging
from collections import defaultdict
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("rate_limiter")

# Default: 60 requests per minute per IP
DEFAULT_RATE_LIMIT = 60
DEFAULT_WINDOW_SECONDS = 60

# Stricter limits for auth endpoints
AUTH_RATE_LIMIT = 10
AUTH_WINDOW_SECONDS = 60

# Very strict for login
LOGIN_RATE_LIMIT = 5
LOGIN_WINDOW_SECONDS = 60

_rate_limits = {
    "/api/v1/auth/login": (LOGIN_RATE_LIMIT, LOGIN_WINDOW_SECONDS),
    "/api/v1/auth/register": (AUTH_RATE_LIMIT, AUTH_WINDOW_SECONDS),
}


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, default_limit: int = DEFAULT_RATE_LIMIT, default_window: int = DEFAULT_WINDOW_SECONDS):
        super().__init__(app)
        self.default_limit = default_limit
        self.default_window = default_window
        self._buckets = defaultdict(list)

    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _get_limit(self, path: str) -> tuple:
        for pattern, (limit, window) in _rate_limits.items():
            if path.startswith(pattern):
                return limit, window
        return self.default_limit, self.default_window

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/health") or request.url.path.startswith("/api/v1/events"):
            return await call_next(request)

        client_ip = self._get_client_ip(request)
        path = request.url.path
        limit, window = self._get_limit(path)
        bucket_key = f"{client_ip}:{path}"

        now = time.time()
        self._buckets[bucket_key] = [t for t in self._buckets[bucket_key] if now - t < window]

        if len(self._buckets[bucket_key]) >= limit:
            logger.warning(f"Rate limit exceeded for {client_ip} on {path}")
            return Response(
                content='{"detail":"Rate limit exceeded. Please try again later."}',
                status_code=429,
                media_type="application/json",
                headers={"Retry-After": str(window), "X-RateLimit-Limit": str(limit), "X-RateLimit-Remaining": "0"}
            )

        self._buckets[bucket_key].append(now)
        remaining = limit - len(self._buckets[bucket_key])

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        return response
