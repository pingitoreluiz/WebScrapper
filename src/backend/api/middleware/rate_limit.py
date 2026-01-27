"""
Rate limiting middleware

Simple in-memory rate limiting for API endpoints.
"""

from fastapi import Request, HTTPException, status
from time import time
from collections import defaultdict
from typing import Dict, Tuple

from ....utils.logger import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """
    In-memory rate limiter
    
    Tracks requests per IP address with sliding window.
    """
    
    def __init__(self, requests_per_minute: int = 60):
        """
        Initialize rate limiter
        
        Args:
            requests_per_minute: Maximum requests allowed per minute
        """
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list[float]] = defaultdict(list)
    
    def is_allowed(self, client_ip: str) -> Tuple[bool, int]:
        """
        Check if request is allowed
        
        Args:
            client_ip: Client IP address
            
        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        now = time()
        minute_ago = now - 60
        
        # Clean old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > minute_ago
        ]
        
        # Check limit
        current_requests = len(self.requests[client_ip])
        
        if current_requests >= self.requests_per_minute:
            return False, 0
        
        # Add current request
        self.requests[client_ip].append(now)
        
        remaining = self.requests_per_minute - (current_requests + 1)
        return True, remaining


# Global rate limiter instance
_rate_limiter = RateLimiter(requests_per_minute=60)


async def rate_limit_middleware(request: Request):
    """
    Rate limiting dependency
    
    Usage:
        >>> @app.get("/endpoint", dependencies=[Depends(rate_limit_middleware)])
        >>> async def endpoint():
        ...     return {"message": "Success"}
    """
    client_ip = request.client.host if request.client else "unknown"
    
    allowed, remaining = _rate_limiter.is_allowed(client_ip)
    
    if not allowed:
        logger.warning("rate_limit_exceeded", client_ip=client_ip)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again later.",
            headers={"Retry-After": "60"}
        )
    
    logger.debug("rate_limit_check", client_ip=client_ip, remaining=remaining)
