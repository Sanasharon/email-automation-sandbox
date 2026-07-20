import logging
import time
from typing import Callable, Awaitable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("api.request")

class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start_time = time.time()
        
        # Don't log healthchecks to avoid noise
        if request.url.path.startswith("/health"):
            return await call_next(request)

        request_id = getattr(request.state, "request_id", "unknown")
        
        # Log Request
        logger.info(
            f"Request Started | ID: {request_id} | Method: {request.method} | Path: {request.url.path} | Client IP: {request.client.host if request.client else 'unknown'}"
        )

        response = None
        try:
            response = await call_next(request)
        except Exception as e:
            process_time = (time.time() - start_time) * 1000
            logger.error(
                f"Request Failed | ID: {request_id} | Method: {request.method} | Path: {request.url.path} | Duration: {process_time:.2f}ms | Error: {str(e)}"
            )
            raise
        
        process_time = (time.time() - start_time) * 1000
        
        # Log Response
        logger.info(
            f"Request Completed | ID: {request_id} | Method: {request.method} | Path: {request.url.path} | Status: {response.status_code} | Duration: {process_time:.2f}ms"
        )
        
        return response
