"""
Shared API Components
LEVEL 5 - Common API patterns, models, and utilities shared across engines
"""

from .models import *
from .responses import *
from .decorators import *
from .exceptions import *

# Conditionally import middleware (requires FastAPI)
try:
    from .middleware import *
    _MIDDLEWARE_AVAILABLE = True
except ImportError:
    _MIDDLEWARE_AVAILABLE = False

__all__ = [
    # Base models
    "BaseRequest",
    "BaseResponse",
    "PaginatedRequest",
    "PaginatedResponse",
    "SearchRequest",
    "ErrorResponse",
    "ValidationErrorResponse",
    "RateLimitResponse",
    "AuthenticationResponse",
    "HealthCheckResponse",
    "BatchRequest",
    "BatchResponse",

    # Response utilities
    "create_success_response",
    "create_error_response",
    "create_paginated_response",
    "create_search_response",
    "create_health_check_response",
    "create_batch_response",
    "APIResponse",
    "ResponseFormatter",

    # Decorators
    "rate_limit",
    "validate_request",
    "handle_errors",
    "log_api_calls",
    "cache_response",
    "require_auth",
    "RateLimiter",

    # Exceptions
    "APIException",
    "ValidationAPIException",
    "AuthenticationAPIException",
    "AuthorizationAPIException",
    "RateLimitAPIException",
    "NotFoundAPIException",
    "ConflictAPIException",
    "BadRequestAPIException",
    "ServiceUnavailableAPIException",
    "TimeoutAPIException",
    "QuotaExceededAPIException",
]

# Add middleware to exports only if available
if _MIDDLEWARE_AVAILABLE:
    __all__.extend([
        "RequestIDMiddleware",
        "TimingMiddleware",
        "LoggingMiddleware",
        "ErrorHandlingMiddleware",
        "SecurityHeadersMiddleware",
        "CompressionMiddleware",
        "add_shared_middleware",
        "DEFAULT_CORS_CONFIG"
    ])
