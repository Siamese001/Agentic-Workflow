"""Side-Effect Guard - Enforce Verification Before Any Side Effects

[PHASE 8] Ensures all side-effect operations require verified context.
"""
from __future__ import annotations
import logging
from .signature_verifier import VerificationContext
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
logger = logging.getLogger(__name__)

class UnverifiedSideEffectError(RuntimeError):
    """Raised when side-effect is attempted without verification."""
    pass

class SideEffectGuard:
    """Guard that enforces verification before side effects."""

    def __init__(self):
        self._active_context: VerificationContext | None = None
        self._guard_enabled = True

    def set_context(self, context: VerificationContext) -> None:
        """Set the active verification context."""
        if not context.is_verified:
            raise UnverifiedSideEffectError('ATTEMPT_TO_SET_UNVERIFIED_CONTEXT: Context must be verified')
        self._active_context = context
        logger.debug(f'SideEffectGuard: Set verified context for signer {context.signer_id}')

    def clear_context(self) -> None:
        """Clear the active verification context."""
        self._active_context = None
        logger.debug('SideEffectGuard: Cleared verification context')

    def require_verified(self, operation: str='side-effect') -> VerificationContext:
        """
        Require verified context before proceeding.

        Raises UnverifiedSideEffectError if no verified context is active.
        """
        if not self._guard_enabled:
            logger.warning(f'SideEffectGuard: Guard disabled, allowing {operation}')
            from .signature_verifier import VerificationContext
            return VerificationContext(is_verified=True, signature_hash='disabled', signer_id='disabled', packet_hash='disabled')
        if self._active_context is None:
            raise UnverifiedSideEffectError(f'UNVERIFIED_OPERATION_DENIED: {operation} attempted without verified context')
        if not self._active_context.is_verified:
            raise UnverifiedSideEffectError(f'UNVERIFIED_CONTEXT_DENIED: {operation} attempted with unverified context')
        logger.debug(f'SideEffectGuard: Allowed {operation} for signer {self._active_context.signer_id}')
        return self._active_context

    def disable(self) -> None:
        """Disable the guard (for testing only)."""
        self._guard_enabled = False
        logger.warning('SideEffectGuard: DISABLED - side effects allowed without verification')

    def enable(self) -> None:
        """Enable the guard."""
        self._guard_enabled = True
        logger.info('SideEffectGuard: ENABLED - verification required for side effects')

    @property
    def has_context(self) -> bool:
        """Check if a verified context is currently active."""
        return self._active_context is not None and self._active_context.is_verified
_global_guard: SideEffectGuard | None = None

def get_side_effect_guard() -> SideEffectGuard:
    """Get the global side-effect guard instance."""
    global _global_guard
    if _global_guard is None:
        _global_guard = SideEffectGuard()
    return _global_guard

def require_verified(operation: str='side-effect') -> VerificationContext:
    """
    Require verified context before proceeding with side effect.

    Convenience function that raises UnverifiedSideEffectError if
    no verified context is active.
    """
    return get_side_effect_guard().require_verified(operation)

def set_verification_context(context: VerificationContext) -> None:
    """Set the global verification context."""
    get_side_effect_guard().set_context(context)

def clear_verification_context() -> None:
    """Clear the global verification context."""
    get_side_effect_guard().clear_context()

def requires_verification(operation_name: str | None=None):
    """Decorator to require verification before function execution."""

    def decorator(func):

        def wrapper(*args, **kwargs):
            op_name = operation_name or f'{func.__module__}.{func.__name__}'
            require_verified(op_name)
            return func(*args, **kwargs)
        return wrapper
    return decorator
logger.info('SideEffectGuard: Initialized with verification enforcement')
