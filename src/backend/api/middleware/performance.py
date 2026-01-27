"""
Performance monitoring middleware for FastAPI

Tracks request metrics and adds performance headers
"""

from time import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, Histogram, Gauge
import structlog

logger = structlog.get_logger()

# Prometheus metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

active_requests = Gauge(
    'http_requests_active',
    'Number of active HTTP requests'
)


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware to track request performance"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Track active requests
        active_requests.inc()
        
        # Start timer
        start_time = time()
        
        # Get endpoint path
        path = request.url.path
        method = request.method
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time() - start_time
            
            # Add performance header
            response.headers["X-Process-Time"] = f"{duration:.4f}"
            
            # Record metrics
            request_count.labels(
                method=method,
                endpoint=path,
                status=response.status_code
            ).inc()
            
            request_duration.labels(
                method=method,
                endpoint=path
            ).observe(duration)
            
            # Log slow requests
            if duration > 1.0:
                logger.warning(
                    "slow_request",
                    method=method,
                    path=path,
                    duration=duration,
                    status=response.status_code
                )
            
            return response
            
        except Exception as e:
            # Record error
            request_count.labels(
                method=method,
                endpoint=path,
                status=500
            ).inc()
            
            logger.error(
                "request_error",
                method=method,
                path=path,
                error=str(e)
            )
            raise
            
        finally:
            # Decrement active requests
            active_requests.dec()


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # HSTS (only in production with HTTPS)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


class CacheControlMiddleware(BaseHTTPMiddleware):
    """Middleware to add cache control headers"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Cache static assets
        if request.url.path.startswith("/static/"):
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        
        # Cache API responses (short TTL)
        elif request.url.path.startswith("/api/"):
            if request.method == "GET":
                response.headers["Cache-Control"] = "public, max-age=60"
                response.headers["ETag"] = f'"{hash(response.body)}"'
        
        return response
