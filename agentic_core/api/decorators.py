"""
Shared API Decorators
LEVEL 5 - Common decorators for API functionality
"""

import asyncio
import time
import logging
from functools import wraps
from typing import Callable, Dict, List, Optional, Tuple
from datetime import datetime, timedelta

from .exceptions import (
    APIException,
    ValidationAPIException,
    RateLimitAPIException,
    AuthenticationAPIException
)

logger = logging.getLogger(__name__)

class RateLimiter:
    """Simple in-memory rate limiter for API endpoints"""

    def __init__(self):
        self.requests: Dict[str, List[datetime]] = {}

    def is_allowed(
        self,
        key: str,
        limit: int,
        window_seconds: int
    ) -> Tuple[bool, datetime]:
        """Check if request is allowed and return reset time"""
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=window_seconds)

        # Clean old requests
        if key in self.requests:
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if req_time > window_start
            ]
        else:
            self.requests[key] = []

        # Check if under limit
        if len(self.requests[key]) < limit:
            self.requests[key].append(now)
            return True, now + timedelta(seconds=window_seconds)

        # Rate limited - return reset time
        oldest_request = min(self.requests[key])
        reset_time = oldest_request + timedelta(seconds=window_seconds)
        return False, reset_time

# Global rate limiter instance
rate_limiter = RateLimiter()

def rate_limit(
    requests_per_minute: int = 60,
    requests_per_hour: int = 1000,
    requests_per_day: int = 10000,
    key_func: Optional[Callable] = None
):
    """
    Rate limiting decorator for API endpoints

    Args:
        requests_per_minute: Requests allowed per minute
        requests_per_hour: Requests allowed per hour
        requests_per_day: Requests allowed per day
        key_func: Function to extract rate limit key from request
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Extract rate limit key
            if key_func:
                try:
                    key = key_func(*args, **kwargs)
                except Exception:
                    key = "default"
            else:
                # Try to get user ID from first argument or kwargs
                key = "default"
                if args and hasattr(args[0], 'user_id'):
                    key = str(args[0].user_id)
                elif 'user_id' in kwargs:
                    key = str(kwargs['user_id'])

            # Check rate limits
            now = datetime.utcnow()

            # Check minute limit
            allowed, reset_time = rate_limiter.is_allowed(
                f"{key}:minute", requests_per_minute, 60
            )
            if not allowed:
                retry_after = int((reset_time - now).total_seconds())
                raise RateLimitAPIException(
                    message="Rate limit exceeded (per minute)",
                    limit=requests_per_minute,
                    reset_time=reset_time,
                    retry_after=retry_after
                )

            # Check hour limit
            allowed, reset_time = rate_limiter.is_allowed(
                f"{key}:hour", requests_per_hour, 3600
            )
            if not allowed:
                retry_after = int((reset_time - now).total_seconds())
                raise RateLimitAPIException(
                    message="Rate limit exceeded (per hour)",
                    limit=requests_per_hour,
                    reset_time=reset_time,
                    retry_after=retry_after
                )

            # Check day limit
            allowed, reset_time = rate_limiter.is_allowed(
                f"{key}:day", requests_per_day, 86400
            )
            if not allowed:
                retry_after = int((reset_time - now).total_seconds())
                raise RateLimitAPIException(
                    message="Rate limit exceeded (per day)",
                    limit=requests_per_day,
                    reset_time=reset_time,
                    retry_after=retry_after
                )

            # Execute function
            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For sync functions, just execute (rate limiting would need async context)
            return func(*args, **kwargs)

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

def validate_request(validator_func: Callable):
    """
    Request validation decorator

    Args:
        validator_func: Function that validates request and raises ValidationAPIException if invalid
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                # Validate request
                validator_func(*args, **kwargs)
                return await func(*args, **kwargs)
            except ValidationAPIException:
                raise
            except Exception as e:
                raise ValidationAPIException(
                    message=f"Request validation failed: {str(e)}",
                    validation_errors=[{"field": "general", "message": str(e)}]
                )

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                # Validate request
                validator_func(*args, **kwargs)
                return func(*args, **kwargs)
            except ValidationAPIException:
                raise
            except Exception as e:
                raise ValidationAPIException(
                    message=f"Request validation failed: {str(e)}",
                    validation_errors=[{"field": "general", "message": str(e)}]
                )

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

def handle_errors(
    default_error_message: str = "An unexpected error occurred",
    log_errors: bool = True,
    include_stack_trace: bool = False
):
    """
    Error handling decorator for API endpoints

    Args:
        default_error_message: Default error message for unhandled exceptions
        log_errors: Whether to log errors
        include_stack_trace: Whether to include stack trace in response (development only)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)

                # Log successful execution
                if log_errors:
                    execution_time = (time.time() - start_time) * 1000
                    logger.info(
                        f"API call {func.__name__} completed successfully",
                        extra={
                            "function": func.__name__,
                            "execution_time_ms": execution_time,
                            "args_count": len(args),
                            "kwargs_count": len(kwargs)
                        }
                    )

                return result

            except APIException:
                # Re-raise API exceptions as-is
                if log_errors:
                    execution_time = (time.time() - start_time) * 1000
                    logger.warning(
                        f"API call {func.__name__} failed with API exception",
                        extra={
                            "function": func.__name__,
                            "execution_time_ms": execution_time,
                            "exception_type": "APIException"
                        }
                    )
                raise

            except Exception as e:
                # Handle unexpected exceptions
                execution_time = (time.time() - start_time) * 1000

                if log_errors:
                    logger.error(
                        f"API call {func.__name__} failed with unexpected error: {str(e)}",
                        extra={
                            "function": func.__name__,
                            "execution_time_ms": execution_time,
                            "exception_type": type(e).__name__,
                            "error_message": str(e)
                        },
                        exc_info=True
                    )

                # Create API exception
                api_exception = APIException(
                    message=default_error_message,
                    error_code="INTERNAL_SERVER_ERROR",
                    error_type="internal"
                )

                if include_stack_trace:
                    import traceback
                    api_exception.stack_trace = traceback.format_exc()

                raise api_exception

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)

                # Log successful execution
                if log_errors:
                    execution_time = (time.time() - start_time) * 1000
                    logger.info(
                        f"API call {func.__name__} completed successfully",
                        extra={
                            "function": func.__name__,
                            "execution_time_ms": execution_time,
                            "args_count": len(args),
                            "kwargs_count": len(kwargs)
                        }
                    )

                return result

            except APIException:
                # Re-raise API exceptions as-is
                if log_errors:
                    execution_time = (time.time() - start_time) * 1000
                    logger.warning(
                        f"API call {func.__name__} failed with API exception",
                        extra={
                            "function": func.__name__,
                            "execution_time_ms": execution_time,
                            "exception_type": "APIException"
                        }
                    )
                raise

            except Exception as e:
                # Handle unexpected exceptions
                execution_time = (time.time() - start_time) * 1000

                if log_errors:
                    logger.error(
                        f"API call {func.__name__} failed with unexpected error: {str(e)}",
                        extra={
                            "function": func.__name__,
                            "execution_time_ms": execution_time,
                            "exception_type": type(e).__name__,
                            "error_message": str(e)
                        },
                        exc_info=True
                    )

                # Create API exception
                api_exception = APIException(
                    message=default_error_message,
                    error_code="INTERNAL_SERVER_ERROR",
                    error_type="internal"
                )

                if include_stack_trace:
                    import traceback
                    api_exception.stack_trace = traceback.format_exc()

                raise api_exception

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

def log_api_calls(
    log_level: str = "info",
    include_args: bool = False,
    include_kwargs: bool = False,
    sensitive_params: List[str] = None
):
    """
    API call logging decorator

    Args:
        log_level: Log level to use ('debug', 'info', 'warning', 'error')
        include_args: Whether to include function arguments in logs
        include_kwargs: Whether to include keyword arguments in logs
        sensitive_params: List of parameter names to sanitize in logs
    """
    if sensitive_params is None:
        sensitive_params = ["password", "token", "secret", "key", "auth"]

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()

            # Prepare log data
            log_data = {
                "function": func.__name__,
                "module": func.__module__,
                "start_time": datetime.utcnow().isoformat()
            }

            # Add arguments if requested
            if include_args and args:
                log_data["args_count"] = len(args)
                if len(args) <= 3:  # Only log if few args
                    log_data["args"] = [str(arg) for arg in args]

            if include_kwargs and kwargs:
                # Sanitize sensitive parameters
                sanitized_kwargs = {}
                for key, value in kwargs.items():
                    if any(sensitive in key.lower() for sensitive in sensitive_params):
                        sanitized_kwargs[key] = "[REDACTED]"
                    else:
                        sanitized_kwargs[key] = str(value)
                log_data["kwargs"] = sanitized_kwargs

            # Log function call
            log_func = getattr(logger, log_level.lower(), logger.info)
            log_func(f"API call started: {func.__name__}", extra=log_data)

            try:
                result = await func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000

                # Log successful completion
                log_data.update({
                    "success": True,
                    "execution_time_ms": execution_time,
                    "end_time": datetime.utcnow().isoformat()
                })

                log_func(f"API call completed: {func.__name__}", extra=log_data)
                return result

            except Exception as e:
                execution_time = (time.time() - start_time) * 1000

                # Log error
                log_data.update({
                    "success": False,
                    "execution_time_ms": execution_time,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "end_time": datetime.utcnow().isoformat()
                })

                logger.error(f"API call failed: {func.__name__}", extra=log_data)
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()

            # Prepare log data
            log_data = {
                "function": func.__name__,
                "module": func.__module__,
                "start_time": datetime.utcnow().isoformat()
            }

            # Add arguments if requested
            if include_args and args:
                log_data["args_count"] = len(args)
                if len(args) <= 3:  # Only log if few args
                    log_data["args"] = [str(arg) for arg in args]

            if include_kwargs and kwargs:
                # Sanitize sensitive parameters
                sanitized_kwargs = {}
                for key, value in kwargs.items():
                    if any(sensitive in key.lower() for sensitive in sensitive_params):
                        sanitized_kwargs[key] = "[REDACTED]"
                    else:
                        sanitized_kwargs[key] = str(value)
                log_data["kwargs"] = sanitized_kwargs

            # Log function call
            log_func = getattr(logger, log_level.lower(), logger.info)
            log_func(f"API call started: {func.__name__}", extra=log_data)

            try:
                result = func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000

                # Log successful completion
                log_data.update({
                    "success": True,
                    "execution_time_ms": execution_time,
                    "end_time": datetime.utcnow().isoformat()
                })

                log_func(f"API call completed: {func.__name__}", extra=log_data)
                return result

            except Exception as e:
                execution_time = (time.time() - start_time) * 1000

                # Log error
                log_data.update({
                    "success": False,
                    "execution_time_ms": execution_time,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "end_time": datetime.utcnow().isoformat()
                })

                logger.error(f"API call failed: {func.__name__}", extra=log_data)
                raise

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

def cache_response(
    ttl_seconds: int = 300,
    max_size: int = 1000,
    key_func: Optional[Callable] = None
):
    """
    Response caching decorator for API endpoints

    Args:
        ttl_seconds: Time to live for cached responses
        max_size: Maximum number of cached responses
        key_func: Function to generate cache key from request
    """
    cache = {}

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                try:
                    cache_key = key_func(*args, **kwargs)
                except Exception:
                    cache_key = str(hash(str(args) + str(sorted(kwargs.items()))))
            else:
                cache_key = str(hash(str(args) + str(sorted(kwargs.items()))))

            # Check cache
            now = datetime.utcnow()
            if cache_key in cache:
                cached_data, cached_time = cache[cache_key]
                if (now - cached_time).total_seconds() < ttl_seconds:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return cached_data
                else:
                    # Cache expired
                    del cache[cache_key]

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            if len(cache) >= max_size:
                # Remove oldest entry (simple LRU)
                oldest_key = min(cache.keys(), key=lambda k: cache[k][1])
                del cache[oldest_key]

            cache[cache_key] = (result, now)
            logger.debug(f"Cached response for {func.__name__}")

            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For sync functions, just execute (caching would need async context)
            return func(*args, **kwargs)

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

def require_auth(
    auth_func: Callable,
    required_scopes: List[str] = None
):
    """
    Authentication decorator for API endpoints

    Args:
        auth_func: Function that performs authentication and returns user info
        required_scopes: List of required permission scopes
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                # Perform authentication
                user_info = auth_func(*args, **kwargs)

                if not user_info:
                    raise AuthenticationAPIException(
                        message="Authentication failed",
                        auth_method="decorator"
                    )

                # Check scopes if required
                if required_scopes:
                    user_scopes = user_info.get("scopes", [])
                    missing_scopes = [scope for scope in required_scopes if scope not in user_scopes]
                    if missing_scopes:
                        raise AuthenticationAPIException(
                            message="Insufficient permissions",
                            auth_method="decorator",
                            required_scopes=required_scopes
                        )

                # Add user info to kwargs
                kwargs["current_user"] = user_info

                return await func(*args, **kwargs)

            except AuthenticationAPIException:
                raise
            except Exception as e:
                raise AuthenticationAPIException(
                    message=f"Authentication error: {str(e)}",
                    auth_method="decorator"
                )

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                # Perform authentication
                user_info = auth_func(*args, **kwargs)

                if not user_info:
                    raise AuthenticationAPIException(
                        message="Authentication failed",
                        auth_method="decorator"
                    )

                # Check scopes if required
                if required_scopes:
                    user_scopes = user_info.get("scopes", [])
                    missing_scopes = [scope for scope in required_scopes if scope not in user_scopes]
                    if missing_scopes:
                        raise AuthenticationAPIException(
                            message="Insufficient permissions",
                            auth_method="decorator",
                            required_scopes=required_scopes
                        )

                # Add user info to kwargs
                kwargs["current_user"] = user_info

                return func(*args, **kwargs)

            except AuthenticationAPIException:
                raise
            except Exception as e:
                raise AuthenticationAPIException(
                    message=f"Authentication error: {str(e)}",
                    auth_method="decorator"
                )

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator
