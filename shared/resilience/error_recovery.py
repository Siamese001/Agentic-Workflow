"""Error Recovery Manager with retry logic and circuit breaker integration.

Phase 1 - Pillar 8: Tool Ecosystem (Resilience Middleware)
"""

import asyncio
import logging
import random
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Awaitable, Optional, Dict

from .circuit_breaker import CircuitBreaker, CircuitBreakerOpenError, get_breaker

logger = logging.getLogger(__name__)


class RecoveryStrategy(Enum):
    RETRY = "retry"
    FAIL_FAST = "fail_fast"
    ESCALATE = "escalate"
    CIRCUIT_BREAK = "circuit_break"


@dataclass
class ResilienceError:
    """Base descriptor for resilience errors."""
    message: str
    code: str
    details: Optional[Dict[str, Any]] = None


@dataclass
class TransientError(ResilienceError):
    """Temporary error that may succeed on retry."""
    pass


@dataclass
class PermanentError(ResilienceError):
    """Permanent error that will not succeed on retry."""
    pass


@dataclass
class RetryExhaustedError(ResilienceError):
    """Error indicating all retry attempts have been exhausted."""
    attempts: int = 0


class ErrorRecoveryManager:
    """Manages error recovery with retry, backoff, and circuit breaking.
    
    This wraps external tool and API calls to provide:
    - Automatic retry with exponential backoff
    - Circuit breaker integration
    - Error classification (transient vs permanent)
    - Observability hooks
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        base_backoff_ms: int = 200,
        jitter_ms: int = 100,
        enable_circuit_breaker: bool = True,
    ):
        self.max_retries = max_retries
        self.base_backoff_ms = base_backoff_ms
        self.jitter_ms = jitter_ms
        self.enable_circuit_breaker = enable_circuit_breaker
    
    def classify_exception(self, exc: Exception) -> ResilienceError:
        """Map a Python exception to a typed resilience error descriptor.
        
        Args:
            exc: The exception to classify
            
        Returns:
            ResilienceError subclass (TransientError or PermanentError)
        """
        msg = str(exc)
        exc_type = exc.__class__.__name__
        
        transient_patterns = [
            "timeout",
            "connection",
            "network",
            "rate limit",
            "throttle",
            "503",
            "502",
            "429",
        ]
        
        permanent_patterns = [
            "validation",
            "authentication",
            "authorization",
            "404",
            "400",
            "401",
            "403",
        ]
        
        msg_lower = msg.lower()
        
        for pattern in permanent_patterns:
            if pattern in msg_lower:
                return PermanentError(message=msg, code=exc_type)
        
        for pattern in transient_patterns:
            if pattern in msg_lower:
                return TransientError(message=msg, code=exc_type)
        
        return TransientError(message=msg, code=exc_type)
    
    def calculate_backoff_ms(self, attempt: int) -> int:
        """Calculate backoff delay with exponential growth and jitter.
        
        Args:
            attempt: Current attempt number (1-indexed)
            
        Returns:
            Backoff delay in milliseconds
        """
        base = self.base_backoff_ms * (2 ** (attempt - 1))
        
        if self.jitter_ms <= 0:
            return base
        
        jitter = random.randint(-self.jitter_ms, self.jitter_ms)
        return max(0, base + jitter)
    
    async def invoke_with_retry(
        self,
        fn: Callable[[], Awaitable[Any]],
        breaker_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Invoke an awaitable with retry + backoff + optional circuit breaker.
        
        Args:
            fn: Async function to invoke
            breaker_name: Optional circuit breaker name
            context: Optional context for logging
            
        Returns:
            Result from successful invocation
            
        Raises:
            Exception: If all retries exhausted or permanent error
        """
        breaker: Optional[CircuitBreaker] = None
        if self.enable_circuit_breaker and breaker_name:
            breaker = get_breaker(breaker_name)
        
        attempt = 0
        last_error: Optional[Exception] = None
        
        while attempt <= self.max_retries:
            attempt += 1
            
            if breaker and not breaker.can_execute():
                error_msg = f"Circuit breaker '{breaker.name}' is open"
                logger.warning(
                    "circuit_breaker_open",
                    extra={
                        "breaker_name": breaker.name,
                        "breaker_state": breaker.state.value,
                        "attempt": attempt,
                        "context": context,
                    },
                )
                raise CircuitBreakerOpenError(error_msg, breaker.name)
            
            try:
                result = await fn()
                
                if breaker:
                    breaker.record_success()
                
                if attempt > 1:
                    logger.info(
                        "retry_success",
                        extra={
                            "attempt": attempt,
                            "context": context,
                        },
                    )
                
                return result
                
            except Exception as exc:
                last_error = exc
                typed_error = self.classify_exception(exc)
                
                if breaker and isinstance(typed_error, TransientError):
                    breaker.record_failure()
                
                if isinstance(typed_error, PermanentError):
                    logger.error(
                        "permanent_error",
                        extra={
                            "error": str(exc),
                            "error_type": exc.__class__.__name__,
                            "attempt": attempt,
                            "context": context,
                        },
                    )
                    raise
                
                if attempt > self.max_retries:
                    logger.error(
                        "retry_exhausted",
                        extra={
                            "error": str(exc),
                            "error_type": exc.__class__.__name__,
                            "attempts": attempt,
                            "context": context,
                        },
                    )
                    raise RetryExhaustedError(
                        message=f"Retry exhausted after {attempt} attempts: {str(exc)}",
                        code=exc.__class__.__name__,
                        attempts=attempt,
                    ) from exc
                
                backoff_ms = self.calculate_backoff_ms(attempt)
                
                logger.warning(
                    "retry_attempt",
                    extra={
                        "error": str(exc),
                        "error_type": exc.__class__.__name__,
                        "attempt": attempt,
                        "max_retries": self.max_retries,
                        "backoff_ms": backoff_ms,
                        "context": context,
                    },
                )
                
                await asyncio.sleep(backoff_ms / 1000.0)
        
        if last_error:
            raise last_error
        
        raise RuntimeError("Unexpected error in retry loop")
