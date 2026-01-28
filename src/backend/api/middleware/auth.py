"""
Authentication middleware

Simple API key authentication for protected endpoints.
"""

from fastapi import Header, HTTPException, status
from typing import Optional

from ...core.config import get_config
from ....utils.logger import get_logger

logger = get_logger(__name__)


async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """
    Verify API key from header

    Args:
        x_api_key: API key from X-API-Key header

    Returns:
        API key if valid

    Raises:
        HTTPException: 401 if API key is missing or invalid

    Usage:
        >>> @app.get("/protected")
        >>> async def protected_route(api_key: str = Depends(verify_api_key)):
        ...     return {"message": "Access granted"}
    """
    config = get_config()

    if not x_api_key:
        logger.warning("api_key_missing")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Provide X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if x_api_key != config.api.api_key:
        logger.warning("api_key_invalid", provided_key=x_api_key[:10] + "...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    logger.debug("api_key_verified")
    return x_api_key


# Optional: More permissive check for read-only endpoints
async def verify_api_key_optional(
    x_api_key: Optional[str] = Header(None),
) -> Optional[str]:
    """
    Optional API key verification

    Returns None if no key provided, validates if present.
    """
    if not x_api_key:
        return None

    config = get_config()

    if x_api_key != config.api.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )

    return x_api_key
