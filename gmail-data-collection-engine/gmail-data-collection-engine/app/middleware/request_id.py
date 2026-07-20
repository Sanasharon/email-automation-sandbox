import logging
import time
import uuid
from typing import Callable, Awaitable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from contextvars import ContextVar

# Context variable to hold the request ID for tracing
request_id_contextvar: ContextVar[str] = ContextVar("request_id", default="")

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Check if client passed a request ID, otherwise generate one
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request_id_contextvar.set(request_id)
        
        # Add to request state for easy access in endpoints
        request.state.request_id = request_id
        
        response = await call_next(request)
        
        # Inject back into the response header
        response.headers["X-Request-ID"] = request_id
        return response
