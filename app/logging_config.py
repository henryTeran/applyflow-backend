"""
Logging configuration using structlog.
"""

import logging
import sys
from typing import Any
import structlog
from pythonjsonlogger import jsonlogger

from app.config import settings


def setup_logging():
    """
    Configure structured logging with structlog and JSON output.
    
    In development: Pretty console output
    In production: JSON logs for log aggregation systems
    """
    
    # Determine log level
    log_level = logging.DEBUG if settings.debug else logging.INFO
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )
    
    # Shared processors for all environments
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    if settings.debug:
        # Development: Pretty console output with colors
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(
                colors=True,
                exception_formatter=structlog.dev.plain_traceback,
            )
        ]
    else:
        # Production: JSON output for log aggregation
        processors = shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = None) -> structlog.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Structured logger instance
        
    Example:
        logger = get_logger(__name__)
        logger.info("user_registered", user_id=123, email="user@example.com")
        logger.error("database_error", error=str(e), query=query)
    """
    return structlog.get_logger(name)


class LoggingMiddleware:
    """
    ASGI middleware for logging HTTP requests and responses.
    """
    
    def __init__(self, app):
        self.app = app
        self.logger = get_logger("http")
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Log request
        self.logger.info(
            "http_request",
            method=scope["method"],
            path=scope["path"],
            query_string=scope.get("query_string", b"").decode(),
            client=scope.get("client"),
        )
        
        # Process request
        await self.app(scope, receive, send)


# Request ID context manager
class RequestIDContext:
    """Context manager for adding request ID to all logs in a request."""
    
    def __init__(self, request_id: str):
        self.request_id = request_id
        self.token = None
    
    def __enter__(self):
        self.token = structlog.contextvars.bind_contextvars(
            request_id=self.request_id
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        structlog.contextvars.unbind_contextvars("request_id")


# Initialize logging on module import
setup_logging()

# Export logger instance
logger = get_logger(__name__)
