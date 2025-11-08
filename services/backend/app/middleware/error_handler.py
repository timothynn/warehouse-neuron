"""
Error handling middleware for consistent error responses
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


def serialize_error(obj):
    """Custom JSON serializer for error objects"""
    if isinstance(obj, (ValueError, Exception)):
        return str(obj)
    if isinstance(obj, dict):
        return {k: serialize_error(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [serialize_error(item) for item in obj]
    return str(obj)


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors"""
    logger.error(f"Database error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Database error occurred",
            "error_code": "DB_ERROR",
            "path": request.url.path,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


async def value_error_handler(request: Request, exc: ValueError):
    """Handle validation errors"""
    logger.warning(f"Validation error on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": str(exc),
            "error_code": "VALIDATION_ERROR",
            "path": request.url.path,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    logger.warning(f"Request validation error on {request.url.path}")
    
    # Extract just the error messages in a simple format
    error_messages = []
    try:
        for err in exc.errors():
            field = ".".join(str(x) for x in err.get("loc", []))
            msg = str(err.get("msg", ""))
            error_messages.append(f"{field}: {msg}")
    except:
        error_messages = ["Validation error occurred"]
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "; ".join(error_messages),
            "error_code": "REQUEST_VALIDATION_ERROR",
            "path": request.url.path,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors"""
    logger.error(f"Unexpected error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred",
            "error_code": "INTERNAL_ERROR",
            "path": request.url.path,
            "request_id": request.headers.get("X-Request-ID", "unknown"),
            "timestamp": datetime.utcnow().isoformat()
        }
    )
