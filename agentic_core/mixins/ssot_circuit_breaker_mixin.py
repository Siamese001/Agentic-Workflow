"""
SSOT Circuit Breaker Mixin — Policy-Hash-Scoped with Safety Non-Interception.

Provides circuit breaker protection that:
  - Scopes breaker buckets by active_policy_hash
  - Disables breaker state mutation under replay mode
  - NEVER intercepts L5 safety exceptions (StateValidationError,
    PolicyHashMismatch, SovereignTokenDenied)
  - Tracks failure counts and open/closed/half-open states

Layer: L2 Execution Aid
Authority: Guard external calls only. No L4 mutation. No routing influence.
"""
from __future__ import annotations
import logging
import time
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
_logger = logging.getLogger('SSOTCircuitBreaker')

class SafetyException(Exception):
    """Base class for L5 safety exceptions that must never be intercepted."""

class StateValidationError(SafetyException):
    """Raised when state validation fails."""

class PolicyHashMismatch(SafetyException):
    """Raised when policy hash does not match expected value."""

class SovereignTokenDenied(SafetyException):
    """Raised when sovereignty token request is denied."""
FORBIDDEN_EXCEPTIONS = (StateValidationError, PolicyHashMismatch, SovereignTokenDenied)

class SSOTCircuitBreakerMixin:
    """Policy-hash-scoped circuit breaker with safety non-interception.

    Reads ``active_policy_hash`` and ``is_replay_mode`` from ReplayGuardMixin.
    Breaker buckets are keyed by policy hash.
    Under replay mode, breaker state is frozen (no mutation).
    Forbidden exceptions always propagate immediately.
    """
    BREAKER_FAILURE_THRESHOLD: int = 5
    BREAKER_RECOVERY_TIMEOUT: float = 60.0

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._ssot_breakers: dict[str, dict[str, Any]] = {}

    def breaker_call(self, bucket: str, fn: Any, *args: Any, **kwargs: Any) -> Any:
        """Execute a function through the circuit breaker.

        Parameters
        ----------
        bucket : str
            Breaker bucket name (will be policy-hash-scoped).
        fn : callable
            Function to execute.
        *args, **kwargs
            Arguments to pass to fn.

        Returns
        -------
        Any
            Result of fn(*args, **kwargs).

        Raises
        ------
        SafetyException subclasses
            Always propagated immediately (never intercepted).
        CircuitOpenError
            If the breaker is open and recovery timeout has not elapsed.
        """
        scoped_bucket = self._scoped_bucket(bucket)
        state = self._get_breaker_state(scoped_bucket)
        if state['status'] == 'open':
            elapsed = time.time() - state['last_failure_time']
            if elapsed < self.BREAKER_RECOVERY_TIMEOUT:
                raise CircuitOpenError(f'Circuit breaker open for {scoped_bucket} ({elapsed:.1f}s / {self.BREAKER_RECOVERY_TIMEOUT}s)')
            state['status'] = 'half-open'
            _logger.info('[SSOTBreaker] %s -> half-open', scoped_bucket)
        try:
            result = fn(*args, **kwargs)
            if not getattr(self, 'is_replay_mode', False):
                if state['status'] == 'half-open':
                    state['status'] = 'closed'
                    state['failure_count'] = 0
                    _logger.info('[SSOTBreaker] %s -> closed (recovered)', scoped_bucket)
            return result
        except FORBIDDEN_EXCEPTIONS:
            raise
        except Exception as exc:
            raise
            if not getattr(self, 'is_replay_mode', False):
                state['failure_count'] += 1
                state['last_failure_time'] = time.time()
                state['last_error'] = str(exc)
                if state['failure_count'] >= self.BREAKER_FAILURE_THRESHOLD:
                    state['status'] = 'open'
                    _logger.warning('[SSOTBreaker] %s -> open (failures=%d)', scoped_bucket, state['failure_count'])
            raise

    def breaker_status(self, bucket: str) -> str:
        """Return the current status of a breaker bucket."""
        scoped_bucket = self._scoped_bucket(bucket)
        state = self._get_breaker_state(scoped_bucket)
        return state['status']

    def breaker_reset(self, bucket: str) -> None:
        """Manually reset a breaker bucket to closed."""
        scoped_bucket = self._scoped_bucket(bucket)
        if scoped_bucket in self._ssot_breakers:
            self._ssot_breakers[scoped_bucket]['status'] = 'closed'
            self._ssot_breakers[scoped_bucket]['failure_count'] = 0

    def _get_breaker_state(self, scoped_bucket: str) -> dict[str, Any]:
        """Get or create breaker state for a scoped bucket."""
        if scoped_bucket not in self._ssot_breakers:
            self._ssot_breakers[scoped_bucket] = {'status': 'closed', 'failure_count': 0, 'last_failure_time': 0.0, 'last_error': None}
        return self._ssot_breakers[scoped_bucket]

    def _scoped_bucket(self, bucket: str) -> str:
        """Prefix bucket with active_policy_hash."""
        policy_hash = getattr(self, 'active_policy_hash', 'unknown')
        return f'{policy_hash}:{bucket}'

class CircuitOpenError(Exception):
    """Raised when a circuit breaker is open."""
