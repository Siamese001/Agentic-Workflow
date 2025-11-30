"""
Shared API Middleware
LEVEL 5 - FastAPI-specific middleware for shared API functionality
"""

import time
import uuid
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import Request, Response, HTTPException
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import RequestResponseEndpoint

from .responses import APIResponse
from .exceptions import APIException

logger = logging.getLogger(__name__)

class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add unique request IDs to all requests"""

    def __init__(self, app, header_name: str = "X-Request-ID"):
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Generate or extract request ID
        request_id = request.headers.get(self.header_name) or str(uuid.uuid4())

        # Add request ID to request state
        request.state.request_id = request_id

        # Process request
        response = await call_next(request)

        # Add request ID to response headers
        response.headers[self.header_name] = request_id

        return response

class TimingMiddleware(BaseHTTPMiddleware):
    """Middleware to track request processing time"""

    def __init__(self, app, header_name: str = "X-Processing-Time"):
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Record start time
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000

        # Add timing to response headers
        response.headers[self.header_name] = f"{processing_time_ms:.2f}"

        # Add timing to request state for potential use in endpoints
        request.state.processing_time_ms = processing_time_ms

        # Log timing information
        logger.info(
            "Request processed",
            extra={
                "method": request.method,
                "url": str(request.url),
                "processing_time_ms": processing_time_ms,
                "status_code": response.status_code
            }
        )

        return response

class LoggingMiddleware(BaseHTTPMiddleware):
    """Enhanced logging middleware for API requests"""

    def __init__(
        self,
        app,
        log_level: str = "info",
        log_request_body: bool = False,
        log_response_body: bool = False,
        max_body_size: int = 1000,
        sensitive_headers: Optional[list] = None
    ):
        super().__init__(app)
        self.log_level = log_level.lower()
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.max_body_size = max_body_size
        self.sensitive_headers = sensitive_headers or [
            "authorization", "x-api-key", "cookie", "set-cookie"
        ]

    def _sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Remove sensitive header values"""
        sanitized = {}
        for key, value in headers.items():
            if key.lower() in [h.lower() for h in self.sensitive_headers]:
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = value
        return sanitized

    def _truncate_body(self, body: str) -> str:
        """Truncate body if too large"""
        if len(body) <= self.max_body_size:
            return body
        return body[:self.max_body_size] + "... (truncated)"

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Prepare request log data
        request_start = datetime.utcnow()
        request_headers = dict(request.headers)

        log_data = {
            "event": "api_request",
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "headers": self._sanitize_headers(request_headers),
            "timestamp": request_start.isoformat()
        }

        # Add request ID if available
        if hasattr(request.state, 'request_id'):
            log_data["request_id"] = request.state.request_id

        # Log request body if enabled
        if self.log_request_body:
            try:
                body = await request.body()
                if body:
                    body_str = body.decode('utf-8', errors='ignore')
                    log_data["body"] = self._truncate_body(body_str)
            except Exception as e:
                logger.warning(f"Failed to read request body: {e}")

        # Log request
        log_func = getattr(logger, self.log_level, logger.info)
        log_func(f"API Request: {request.method} {request.url}", extra=log_data)

        # Process request
        response = await call_next(request)

        # Prepare response log data
        response_end = datetime.utcnow()
        processing_time = (response_end - request_start).total_seconds() * 1000

        response_log_data = {
            "event": "api_response",
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "processing_time_ms": processing_time,
            "timestamp": response_end.isoformat()
        }

        # Add request ID if available
        if hasattr(request.state, 'request_id'):
            response_log_data["request_id"] = request.state.request_id

        # Log response body if enabled
        if self.log_response_body:
            try:
                # Note: This requires the response body to be readable
                # FastAPI responses might not be readable after being sent
                response_log_data["response_size"] = len(str(response.body))
            except Exception as e:
                logger.warning(f"Failed to read response body: {e}")

        # Log response
        log_func(f"API Response: {response.status_code} ({processing_time:.2f}ms)", extra=response_log_data)

        return response

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware to handle API exceptions and convert to proper responses"""

    def __init__(
        self,
        app,
        include_stack_trace: bool = False,
        log_errors: bool = True
    ):
        super().__init__(app)
        self.include_stack_trace = include_stack_trace
        self.log_errors = log_errors

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            response = await call_next(request)
            return response
        except APIException as e:
            # Handle our custom API exceptions
            if self.log_errors:
                logger.error(
                    f"API Exception: {e.error_code} - {e.message}",
                    extra={
                        "error_code": e.error_code,
                        "error_type": e.error_type,
                        "request_id": getattr(request.state, 'request_id', None),
                        "url": str(request.url),
                        "method": request.method
                    }
                )

            # Convert to JSON response
            from fastapi.responses import JSONResponse
            error_dict = e.to_dict()

            if self.include_stack_trace and e.stack_trace:
                error_dict["stack_trace"] = e.stack_trace

            # Add request ID if available
            if hasattr(request.state, 'request_id'):
                error_dict["request_id"] = request.state.request_id

            return JSONResponse(
                status_code=self._get_status_code_for_exception(e),
                content=error_dict
            )
        except HTTPException as e:
            # Handle FastAPI HTTP exceptions
            if self.log_errors:
                logger.error(
                    f"HTTP Exception: {e.status_code} - {e.detail}",
                    extra={
                        "status_code": e.status_code,
                        "request_id": getattr(request.state, 'request_id', None),
                        "url": str(request.url),
                        "method": request.method
                    }
                )

            from fastapi.responses import JSONResponse
            error_response = APIResponse.error(
                error_code=f"HTTP_{e.status_code}",
                message=str(e.detail),
                error_type="http_error"
            )

            if hasattr(request.state, 'request_id'):
                error_response["request_id"] = request.state.request_id

            return JSONResponse(
                status_code=e.status_code,
                content=error_response
            )
        except Exception as e:
            # Handle unexpected exceptions
            if self.log_errors:
                logger.error(
                    f"Unexpected error: {str(e)}",
                    extra={
                        "error_type": type(e).__name__,
                        "request_id": getattr(request.state, 'request_id', None),
                        "url": str(request.url),
                        "method": request.method
                    },
                    exc_info=True
                )

            from fastapi.responses import JSONResponse
            error_response = APIResponse.error(
                error_code="INTERNAL_SERVER_ERROR",
                message="An unexpected error occurred",
                error_type="internal"
            )

            if self.include_stack_trace:
                import traceback
                error_response["stack_trace"] = traceback.format_exc()

            if hasattr(request.state, 'request_id'):
                error_response["request_id"] = request.state.request_id

            return JSONResponse(
                status_code=500,
                content=error_response
            )

    def _get_status_code_for_exception(self, exception: APIException) -> int:
        """Map API exceptions to HTTP status codes"""
        status_code_map = {
            "VALIDATION_FAILED": 400,
            "AUTHENTICATION_FAILED": 401,
            "ACCESS_DENIED": 403,
            "NOT_FOUND": 404,
            "CONFLICT": 409,
            "RATE_LIMIT_EXCEEDED": 429,
            "SERVICE_UNAVAILABLE": 503,
            "TIMEOUT": 408,
            "QUOTA_EXCEEDED": 429,
            "BAD_REQUEST": 400
        }

        return status_code_map.get(exception.error_code, 500)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to responses"""

    def __init__(
        self,
        app,
        custom_headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(app)
        self.custom_headers = custom_headers or {}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)

        # Add security headers
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'"
        }

        # Add custom headers
        security_headers.update(self.custom_headers)

        # Apply headers
        for header, value in security_headers.items():
            response.headers[header] = value

        return response

class CompressionMiddleware(BaseHTTPMiddleware):
    """Simple compression middleware for large responses"""

    def __init__(
        self,
        app,
        minimum_size: int = 1024,  # 1KB
        compressible_types: Optional[list] = None
    ):
        super().__init__(app)
        self.minimum_size = minimum_size
        self.compressible_types = compressible_types or [
            "application/json",
            "text/html",
            "text/css",
            "text/javascript",
            "application/javascript"
        ]

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)

        # Check if response should be compressed
        content_type = response.headers.get("content-type", "").split(";")[0]
        content_length = response.headers.get("content-length")

        if (content_type in self.compressible_types and
            content_length and
            int(content_length) > self.minimum_size):

            # Add compression header (actual compression would be handled by web server)
            response.headers["Content-Encoding"] = "gzip"

        return response

# Utility functions for adding middleware to FastAPI apps
def add_shared_middleware(
    app,
    enable_request_id: bool = True,
    enable_timing: bool = True,
    enable_logging: bool = True,
    enable_error_handling: bool = True,
    enable_security_headers: bool = True,
    enable_compression: bool = False,
    cors_config: Optional[Dict[str, Any]] = None,
    **middleware_kwargs
):
    """
    Add all shared middleware to a FastAPI application
    
    Args:
        app: FastAPI application instance
        enable_request_id: Enable request ID middleware
        enable_timing: Enable timing middleware
        enable_logging: Enable logging middleware
        enable_error_handling: Enable error handling middleware
        enable_security_headers: Enable security headers middleware
        enable_compression: Enable compression middleware
        cors_config: CORS configuration dictionary
        **middleware_kwargs: Additional arguments for middleware
    """

    # Add CORS middleware if configured
    if cors_config:
        app.add_middleware(
            CORSMiddleware,
            **cors_config
        )

    # Add shared middleware in order
    if enable_request_id:
        app.add_middleware(
            RequestIDMiddleware,
            header_name=middleware_kwargs.get("request_id_header", "X-Request-ID")
        )

    if enable_timing:
        app.add_middleware(
            TimingMiddleware,
            header_name=middleware_kwargs.get("timing_header", "X-Processing-Time")
        )

    if enable_logging:
        app.add_middleware(
            LoggingMiddleware,
            log_level=middleware_kwargs.get("log_level", "info"),
            log_request_body=middleware_kwargs.get("log_request_body", False),
            log_response_body=middleware_kwargs.get("log_response_body", False),
            max_body_size=middleware_kwargs.get("max_body_size", 1000),
            sensitive_headers=middleware_kwargs.get("sensitive_headers")
        )

    if enable_security_headers:
        app.add_middleware(
            SecurityHeadersMiddleware,
            custom_headers=middleware_kwargs.get("custom_security_headers", {})
        )

    if enable_compression:
        app.add_middleware(
            CompressionMiddleware,
            minimum_size=middleware_kwargs.get("compression_min_size", 1024),
            compressible_types=middleware_kwargs.get("compressible_types")
        )

    # Error handling should be last (closest to the app)
    if enable_error_handling:
        app.add_middleware(
            ErrorHandlingMiddleware,
            include_stack_trace=middleware_kwargs.get("include_stack_trace", False),
            log_errors=middleware_kwargs.get("log_errors", True)
        )

# Default CORS configuration for shared use
DEFAULT_CORS_CONFIG = {
    "allow_origins": ["*"],  # Configure appropriately for production
    "allow_credentials": True,
    "allow_methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    "allow_headers": ["*"],
    "expose_headers": ["X-Request-ID", "X-Processing-Time"]
}
