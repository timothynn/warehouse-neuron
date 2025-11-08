"""
Request/Response logging middleware
"""
import time
import logging
import uuid
from fastapi import Request

logger = logging.getLogger(__name__)


async def log_requests_middleware(request: Request, call_next):
    """
    Log all API requests and responses with timing information.
    """
    # Generate unique request ID
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Log request
    logger.info(
        f"Request {request_id}: {request.method} {request.url.path}",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
        }
    )
    
    # Process request and measure time
    start_time = time.time()
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response {request_id}: {response.status_code} ({duration:.2f}s)",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "duration": duration,
            }
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        return response
    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            f"Error {request_id}: {e} ({duration:.2f}s)",
            extra={
                "request_id": request_id,
                "error": str(e),
                "duration": duration,
            },
            exc_info=True
        )
        raise
