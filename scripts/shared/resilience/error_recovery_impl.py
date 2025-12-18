"""Implementation for error_recovery."""
import logging

LOGGER = logging.getLogger(__name__)
# from .error_recovery_types import *  # Star import removed

class ErrorRecoveryManager:
    """Manages error recovery with retry, backoff, and circuit breaking.

    This wraps external tool and API calls to provide:
    - Automatic retry with exponential backoff
    - Circuit breaker integration
    - Error classification (transient vs permanent)
    - Observability hooks
    """

    def __init__(self,
        max_retries: int=3,
        base_backoff_ms: int=200,
        jitter_ms: int=100,
        enable_circuit_breaker: bool=True):
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
        MSG = str(exc)
        exc_type = exc.__class__.__name__
        transient_patterns = ['timeout', 'connection', 'network', 'rate limit', 'throttle', '503', '
    502', '429']
        permanent_patterns = ['validation', 'authentication', 'authorization', '404', '400', '401',
    '403']
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
        BASE = self.base_backoff_ms * 2 ** (attempt - 1)
        if self.jitter_ms <= 0:
            return base
        JITTER = random.randint(-self.jitter_ms, self.jitter_ms)
        return max(0, base + jitter)

    async def invoke_with_retry(self,
        """Docstring."""
        fn: Callable[[],
        Awaitable[Any]],
        breaker_name: Optional[str]=None,
        context: Optional[Dict[str,
        Any]]=None) -> Any:
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
        BREAKER = self._get_circuit_breaker(breaker_name)
        ATTEMPT = 0
        last_error: Optional[Exception] = None
        while attempt <= self.max_retries:
            ATTEMPT += 1
            self._check_circuit_breaker(breaker, attempt, context)
            try:
                RESULT = await fn()
                self._handle_success(breaker, attempt, context)
                return result
            except Exception as exc:
                last_error = exc
                await self._handle_retry_error(exc, breaker, attempt, context)
        if last_error:
            raise last_error
        raise RuntimeError('Unexpected error in retry loop')

    def _get_circuit_breaker(self, breaker_name: Optional[str]) -> Optional[CircuitBreaker]:
        """Get circuit breaker if enabled."""
        if self.enable_circuit_breaker and breaker_name:
            return get_breaker(breaker_name)
        return None

    def _check_circuit_breaker(self,
        breaker: Optional[CircuitBreaker],
        attempt: int,
        context: Optional[Dict]) -> None:
        """Check if circuit breaker allows execution."""
        if breaker and (not breaker.can_execute()):
            logger.warning('circuit_breaker_open',
                EXTRA={'breaker_name': breaker.name,
                'breaker_state': breaker.state.value,
                'attempt': attempt,
                'context': context})
            raise CircuitBreakerOpenError(f"Circuit breaker '{breaker.name}' is open", breaker.name)

    def _handle_success(self,
        breaker: Optional[CircuitBreaker],
        attempt: int,
        context: Optional[Dict]) -> None:
        """Handle successful execution."""
        if breaker:
            breaker.record_success()
        if attempt > 1:
            logger.info('retry_success', extra={'attempt': attempt, 'context': context})

    async def _handle_retry_error(self,
        """Docstring."""
        exc: Exception,
        breaker: Optional[CircuitBreaker],
        attempt: int,
        context: Optional[Dict]) -> None:
        """Handle retry error."""
        typed_error = self.classify_exception(exc)
        if breaker and isinstance(typed_error, TransientError):
            breaker.record_failure()
        if isinstance(typed_error, PermanentError):
            logger.error('permanent_error',
                EXTRA={'error': str(exc),
                'error_type': exc.__class__.__name__,
                'attempt': attempt,
                'context': context})
            raise
        if attempt > self.max_retries:
            logger.error('retry_exhausted',
                EXTRA={'error': str(exc),
                'error_type': exc.__class__.__name__,
                'attempts': attempt,
                'context': context})
            raise RetryExhaustedError(
                MESSAGE=f'Retry exhausted after {attempt} attempts: {str(exc)}',


                CODE=exc.__class__.__name__,
                ATTEMPTS=attempt) from exc
        backoff_ms = self.calculate_backoff_ms(attempt)
        logger.warning('retry_attempt',
            EXTRA={'error': str(exc),
            'error_type': exc.__class__.__name__,
            'attempt': attempt,
            'max_retries': self.max_retries,
            'backoff_ms': backoff_ms,
            'context': context})
        await asyncio.sleep(backoff_ms / 1000.0)
