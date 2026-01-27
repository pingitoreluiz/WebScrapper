"""
Request logging middleware

Logs all API requests with timing information.
"""

from fastapi import Request
from time import time

from ....utils.logger import get_logger

logger = get_logger(__name__)


async def log_requests_middleware(request: Request, call_next):
    """
    Log all requests with timing
    
    This is a middleware function, not a dependency.
    Add to app with: app.middleware("http")(log_requests_middleware)
    """
    start_time = time()
    
    # Log request
    logger.info(
        "request_started",
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host if request.client else "unknown"
    )
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time() - start_time
    
    # Log response
    logger.info(
        "request_completed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=round(duration * 1000, 2)
    )
    
    # Add timing header
    response.headers["X-Process-Time"] = str(duration)
    
    return response
