"""
Rate limiting middleware using SlowAPI.
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from app.config import settings


# Create limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.rate_limit_per_minute}/minute"],
    storage_uri=settings.redis_url,
    strategy="fixed-window"
)


def setup_rate_limiting(app):
    """
    Setup rate limiting for FastAPI app.
    
    Args:
        app: FastAPI application instance
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Custom rate limit decorators for different use cases
def rate_limit_strict(limit: str = "10/minute"):
    """
    Strict rate limit for sensitive endpoints.
    
    Args:
        limit: Rate limit string (e.g., "10/minute", "100/hour")
        
    Example:
        @router.post("/sensitive-action")
        @rate_limit_strict("5/minute")
        async def sensitive_action():
            ...
    """
    return limiter.limit(limit)


def rate_limit_generous(limit: str = "100/minute"):
    """
    Generous rate limit for public endpoints.
    
    Args:
        limit: Rate limit string
    """
    return limiter.limit(limit)
