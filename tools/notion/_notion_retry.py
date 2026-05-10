#!/usr/bin/env python3
"""_notion_retry.py — Notion API retry decorator with exponential backoff.

Pure logic. No I/O at import. Safe to import from any hook or write path.

Retry policy:
  - Max 3 attempts for retryable errors (429, 502, 503, 504)
  - Exponential backoff: 1s, 2s, 4s (respects Retry-After header if present)
  - Non-retryable (400, 401, 404, 409): fail fast
  - Idempotency key header on PATCH operations

Constitutional: §25 (MCP serialization), §36 (plan registration)
"""
from __future__ import annotations

import functools
import json
import time
import urllib.error
from dataclasses import dataclass, field
from typing import Any, Callable, TypeVar

# ---------------------------------------------------------------------------
# Retry configuration
# ---------------------------------------------------------------------------

MAX_RETRIES = 3
BASE_BACKOFF_SECONDS = 1.0
MAX_BACKOFF_SECONDS = 4.0
RETRYABLE_STATUS_CODES = {429, 502, 503, 504}
NON_RETRYABLE_STATUS_CODES = {400, 401, 403, 404, 409, 410, 422}


# ---------------------------------------------------------------------------
# Retry state tracking
# ---------------------------------------------------------------------------

@dataclass
class RetryContext:
    """Context for a retry operation."""
    attempt: int = 0
    max_retries: int = MAX_RETRIES
    last_error: Exception | None = None
    last_status_code: int | None = None
    total_delay_ms: float = 0.0
    succeeded: bool = False
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "attempt": self.attempt,
            "max_retries": self.max_retries,
            "last_status_code": self.last_status_code,
            "total_delay_ms": round(self.total_delay_ms, 2),
            "succeeded": self.succeeded,
        }


@dataclass
class RetryResult:
    """Result of a retryable operation."""
    success: bool
    result: Any = None
    error: Exception | None = None
    context: RetryContext = field(default_factory=RetryContext)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "context": self.context.to_dict(),
            "error": str(self.error) if self.error else None,
        }


# ---------------------------------------------------------------------------
# HTTP status code extraction
# ---------------------------------------------------------------------------

def _extract_status_code(error: Exception) -> int | None:
    """Extract HTTP status code from an exception."""
    if isinstance(error, urllib.error.HTTPError):
        return error.code
    # Handle wrapped exceptions
    if hasattr(error, '__cause__') and isinstance(error.__cause__, urllib.error.HTTPError):
        return error.__cause__.code
    return None


def _extract_retry_after(error: Exception) -> float | None:
    """Extract Retry-After header value from an HTTP error."""
    http_error = None
    if isinstance(error, urllib.error.HTTPError):
        http_error = error
    elif hasattr(error, '__cause__') and isinstance(error.__cause__, urllib.error.HTTPError):
        http_error = error.__cause__
    
    if http_error and hasattr(http_error, 'headers'):
        retry_after = http_error.headers.get('Retry-After')
        if retry_after:
            try:
                return float(retry_after)
            except (ValueError, TypeError):
                pass
    return None


def _is_retryable(error: Exception) -> bool:
    """Determine if an error is retryable."""
    status_code = _extract_status_code(error)
    
    if status_code is None:
        # Network-level errors (timeout, connection reset) are retryable
        return True
    
    # Explicitly retryable
    if status_code in RETRYABLE_STATUS_CODES:
        return True
    
    # Explicitly non-retryable
    if status_code in NON_RETRYABLE_STATUS_CODES:
        return False
    
    # Default: retry 5xx, don't retry 4xx
    return status_code >= 500


# ---------------------------------------------------------------------------
# Backoff calculation
# ---------------------------------------------------------------------------

def _calculate_backoff(attempt: int, error: Exception | None = None) -> float:
    """Calculate delay before next retry attempt.
    
    Args:
        attempt: Current attempt number (0-indexed)
        error: The exception from the failed attempt (for Retry-After header)
    
    Returns:
        Seconds to delay
    """
    # Check for Retry-After header on 429 responses
    if error:
        retry_after = _extract_retry_after(error)
        if retry_after is not None:
            return retry_after
    
    # Exponential backoff: 1s, 2s, 4s
    delay = BASE_BACKOFF_SECONDS * (2 ** attempt)
    return min(delay, MAX_BACKOFF_SECONDS)


# ---------------------------------------------------------------------------
# Retry decorator
# ---------------------------------------------------------------------------

F = TypeVar('F', bound=Callable[..., Any])

def with_retry(
    max_retries: int = MAX_RETRIES,
    on_retry: Callable[[Exception, int, float], None] | None = None,
) -> Callable[[F], F]:
    """Decorator that adds retry logic to a function.
    
    Args:
        max_retries: Maximum number of retry attempts
        on_retry: Optional callback(error, attempt_number, delay_seconds)
    
    Returns:
        Decorated function that returns RetryResult
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> RetryResult:
            context = RetryContext(max_retries=max_retries)
            
            for attempt in range(max_retries + 1):
                context.attempt = attempt
                
                try:
                    result = func(*args, **kwargs)
                    context.succeeded = True
                    return RetryResult(success=True, result=result, context=context)
                
                except Exception as e:
                    context.last_error = e
                    context.last_status_code = _extract_status_code(e)
                    
                    # Don't retry if explicitly non-retryable
                    if not _is_retryable(e):
                        return RetryResult(
                            success=False,
                            error=e,
                            context=context,
                        )
                    
                    # Last attempt failed
                    if attempt >= max_retries:
                        return RetryResult(
                            success=False,
                            error=e,
                            context=context,
                        )
                    
                    # Calculate and apply backoff
                    delay = _calculate_backoff(attempt, e)
                    context.total_delay_ms += delay * 1000
                    
                    # Notify callback if provided
                    if on_retry:
                        on_retry(e, attempt, delay)
                    
                    # Wait before next attempt
                    time.sleep(delay)
            
            # Should never reach here
            return RetryResult(success=False, context=context)
        
        return wrapper  # type: ignore[return-value]
    
    return decorator


# ---------------------------------------------------------------------------
# Utility for urllib requests
# ---------------------------------------------------------------------------

def make_idempotency_key() -> str:
    """Generate a unique idempotency key for PATCH operations."""
    import uuid
    return str(uuid.uuid4())


def add_idempotency_header(headers: dict[str, str]) -> dict[str, str]:
    """Add Idempotency-Key header to request headers."""
    headers = headers.copy()
    headers['Idempotency-Key'] = make_idempotency_key()
    return headers


# ---------------------------------------------------------------------------
# Retry-aware HTTP request wrapper
# ---------------------------------------------------------------------------

@dataclass
class HTTPResponse:
    """Simplified HTTP response for retry wrapper."""
    status: int
    body: bytes
    headers: dict[str, str]


def _urlopen_with_retry(
    request: urllib.request.Request,
    max_retries: int = MAX_RETRIES,
    timeout: float | None = None,
) -> RetryResult:
    """Execute a urllib request with retry logic.
    
    This is a standalone function (not decorator) for one-off urllib calls.
    """
    context = RetryContext(max_retries=max_retries)
    
    for attempt in range(max_retries + 1):
        context.attempt = attempt
        
        try:
            import urllib.request
            response = urllib.request.urlopen(request, timeout=timeout)
            
            body = response.read()
            headers = dict(response.headers)
            context.succeeded = True
            
            return RetryResult(
                success=True,
                result=HTTPResponse(
                    status=response.status,
                    body=body,
                    headers=headers,
                ),
                context=context,
            )
        
        except urllib.error.HTTPError as e:
            context.last_error = e
            context.last_status_code = e.code
            
            # Non-retryable: fail fast
            if e.code in NON_RETRYABLE_STATUS_CODES:
                return RetryResult(
                    success=False,
                    error=e,
                    context=context,
                )
            
            # Last attempt
            if attempt >= max_retries:
                return RetryResult(
                    success=False,
                    error=e,
                    context=context,
                )
            
            # Retryable: backoff and retry
            if e.code in RETRYABLE_STATUS_CODES or e.code >= 500:
                delay = _calculate_backoff(attempt, e)
                context.total_delay_ms += delay * 1000
                time.sleep(delay)
                continue
            
            # Unknown 4xx: don't retry
            return RetryResult(success=False, error=e, context=context)
        
        except Exception as e:
            # Network errors (timeout, connection reset) are retryable
            context.last_error = e
            
            if attempt >= max_retries:
                return RetryResult(success=False, error=e, context=context)
            
            delay = _calculate_backoff(attempt, e)
            context.total_delay_ms += delay * 1000
            time.sleep(delay)
    
    return RetryResult(success=False, context=context)


def urlopen_with_retry(
    request: urllib.request.Request,
    max_retries: int = MAX_RETRIES,
    timeout: float | None = None,
) -> HTTPResponse:
    """Execute a urllib request with retry, raising on failure.
    
    This is a convenience wrapper that either returns the HTTPResponse
    or raises the last exception after retries are exhausted.
    """
    result = _urlopen_with_retry(request, max_retries, timeout)
    
    if result.success:
        return result.result
    else:
        raise result.error or Exception("Unknown error after retries")
