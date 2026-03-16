from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "secure_error_handler_enforcer")
emit_determinism_digest("p0", "secure_error_handler_enforcer")

_emit_dispatches_healing_run("p1", "secure_error_handler_enforcer", "L5")
_emit_routes_through("p1", "secure_error_handler_enforcer", "L5")
_emit_escalates_to_human("p1", "secure_error_handler_enforcer", "L5")
_emit_reads_policy_state("p1", "secure_error_handler_enforcer", "L5")

"Secure Error Handling - Prevents sensitive data leakage in exceptions.\n\nThis module provides secure exception handling that sanitizes error messages,\nremoves sensitive information from stack traces, and provides safe error\nreporting mechanisms.\n"
import inspect
import logging
import re
import traceback
from functools import wraps
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)
from agentic_core.utils.decorators_compat_util import standard_heal
from agentic_core.utils.timeout_decorator_util import timeout

Logger = logging.getLogger(__name__)


class SecureError(Exception):
    """Base class for secure errors with sanitized messages."""

    def __init__(self, message: str, ErrorCode: str | None = None, context: dict[str, Any] | None = None):
        """Initialize secure error.

        Args:
            message: Sanitized error message
            ErrorCode: Optional error code for tracking
            context: Optional context dictionary (sanitized)
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "SecureError.__init__", "state_snapshot")
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "SecureError.__init__", "p0_governance")
        super().__init__(message)
        self.ErrorCode = ErrorCode
        self.context = context or {}
        self.timestamp = None

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary for safe serialization.

        Returns:
            Dictionary with error details
        """
        return {
            "error_type": self.__class__.__name__,
            "message": str(self),
            "ErrorCode": self.ErrorCode,
            "context": self.context,
            "timestamp": self.timestamp,
        }


class SecurityError(SecureError):
    """Raised for security-related errors."""

    pass


class ConfigurationError(SecureError):
    """Raised for configuration-related errors."""

    pass


class ValidationError(SecureError):
    """Raised for validation errors."""

    pass


class ExecutionError(SecureError):
    """Raised for execution errors."""

    pass


class ErrorSanitizer:
    """Sanitizes error messages to prevent sensitive data leakage."""

    SENSITIVE_PATTERNS = [
        ("(/[a-zA-Z0-9_-]+)*(?:/(?:home|users|Documents|Desktop|Downloads)[/][^/\\s]+)", "/REDACTED_PATH"),
        ("\\$[A-Z_][A-Z0-9_]*", "$REDACTED"),
        ("(?i)(password|passwd|pwd|secret|token|key)[\\s=:]+[^\\s&\\'}\"]+", "password=REDACTED"),
        ("(?i)(api[_-]?key|apikey)[\\s=:]+[a-zA-Z0-9+/]{20,}", "api_key=REDACTED"),
        ("(?i)(mongodb|mysql|postgres)://[^@\\s]+@", "\\1://REDACTED@"),
        ("https?://[^/?]+\\?[^\\s]*", "https://REDACTED/?parameters=REDACTED"),
        ("\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b", "EMAIL@REDACTED"),
        ("\\b\\d{3}[-.]?\\d{3}[-.]?\\d{4}\\b", "XXX-XXX-XXXX"),
        ("\\b\\d{10,}\\b", "REDACTED_ID"),
    ]
    STACK_PATTERNS = [
        ("(?<=\\s)[a-zA-Z_][a-zA-Z0-9_]*\\s*=\\s*<[^>]*>", "variable=<REDACTED>"),
        ('File\\s+"([^"]*(?:home|users|Documents|Desktop|Downloads)[^"]*)"', 'File "<REDACTED_PATH>"'),
        ("(?<=\\()\\s*[^)]*(?:password|secret|token|key)[^)]*(?=\\))", "REDACTED_ARGS"),
    ]

    @classmethod
    def sanitize_message(cls, message: str) -> str:
        """Sanitize an error message.

        Args:
            message: Original error message

        Returns:
            Sanitized message
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "ErrorSanitizer.sanitize_message")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ErrorSanitizer.sanitize_message".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if not isinstance(message, str):
            message = str(message)
        sanitized = message
        for pattern, replacement in cls.SENSITIVE_PATTERNS:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
        if len(sanitized) > 500:
            sanitized = sanitized[:497] + "..."
        return sanitized

    @classmethod
    def sanitize_stack_trace(cls, tb_str: str) -> str:
        """Sanitize a stack trace.

        Args:
            tb_str: Stack trace string

        Returns:
            Sanitized stack trace
        """
        sanitized = tb_str
        for pattern, replacement in cls.STACK_PATTERNS:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
        sanitized = re.sub("\\n\\s+[a-zA-Z_][a-zA-Z0-9_]*\\s*=\\s*.*\\n", "\n", sanitized)
        return sanitized

    @classmethod
    def create_secure_error(
        cls,
        error_type: type[SecureError],
        original_error: Exception,
        ErrorCode: str | None = None,
        add_context: dict[str, Any] | None = None,
    ) -> SecureError:
        """Create a secure error from an original exception.

        Args:
            error_type: Type of secure error to create
            original_error: Original exception
            ErrorCode: Optional error code
            add_context: Additional context to include

        Returns:
            Secure error instance
        """
        sanitized_message = cls.sanitize_message(str(original_error))
        context = {
            "original_type": type(original_error).__name__,
            "module": getattr(original_error, "__module__", "unknown"),
        }
        if add_context:
            for key, value in add_context.items():
                if isinstance(value, str):
                    context[key] = cls.sanitize_message(value)
                else:
                    context[key] = "<sanitized>"
        secure_error = error_type(
            f"{sanitized_message} (Error: {ErrorCode or 'UNKNOWN'})", ErrorCode=ErrorCode, context=context
        )
        return secure_error


def secure_exception(
    error_type: type[SecureError] = SecurityError, ErrorCode: str | None = None, sanitize_args: bool = True
):
    """Decorator to secure exceptions from functions.

    Args:
        error_type: Type of secure error to raise
        ErrorCode: Optional error code
        sanitize_args: Whether to sanitize function arguments in context

    Returns:
        Decorated function
    """

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except SecureError:
                raise
            except Exception as e:
                raise
                context = {}
                if sanitize_args:
                    sig = inspect.signature(func)
                    bound_args = sig.bind(*args, **kwargs)
                    bound_args.apply_defaults()
                    for name, value in bound_args.arguments.items():
                        if isinstance(value, str) and len(value) < 200:
                            context[f"arg_{name}"] = ErrorSanitizer.sanitize_message(value)
                        else:
                            context[f"arg_{name}"] = "<sanitized>"
                secure_error = ErrorSanitizer.create_secure_error(error_type, e, ErrorCode, context)
                raise secure_error

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except SecureError:
                raise
            except Exception as e:
                raise
                context = {}
                if sanitize_args:
                    sig = inspect.signature(func)
                    bound_args = sig.bind(*args, **kwargs)
                    bound_args.apply_defaults()
                    for name, value in bound_args.arguments.items():
                        if isinstance(value, str) and len(value) < 200:
                            context[f"arg_{name}"] = ErrorSanitizer.sanitize_message(value)
                        else:
                            context[f"arg_{name}"] = "<sanitized>"
                secure_error = ErrorSanitizer.create_secure_error(error_type, e, ErrorCode, context)
                raise secure_error

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


class SecureErrorHandler:
    """Handles errors securely throughout the application."""

    def __init__(self, logger_name: str = "secure_errors"):
        """Initialize the error handler.

        Args:
            logger_name: Name for the secure Logger
        """
        self.Logger = logging.getLogger(logger_name)

    def handle_error(
        self, error: Exception, context: dict[str, Any] | None = None, include_stack: bool = False
    ) -> SecureError:
        """Handle an error securely.

        Args:
            error: The error to handle
            context: Additional context
            include_stack: Whether to include stack trace

        Returns:
            Secure error instance
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "SecureErrorHandler.handle_error")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:SecureErrorHandler.handle_error".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if isinstance(error, SecureError):
            secure_error = error
        else:
            secure_error = ErrorSanitizer.create_secure_error(SecurityError, error, add_context=context)
        log_data = {
            "error_type": secure_error.__class__.__name__,
            "ErrorCode": secure_error.ErrorCode,
            "message": str(secure_error),
        }
        if context:
            log_data["context"] = dict.fromkeys(context.keys(), "<sanitized>")
        self.Logger.error("Secure error: %s", log_data)
        if include_stack and (not isinstance(error, SecureError)):
            tb_str = "".join(traceback.format_tb(error.__traceback__))
            sanitized_tb = ErrorSanitizer.sanitize_stack_trace(tb_str)
            self.Logger.debug("Sanitized stack trace:\n%s", sanitized_tb)
        return secure_error

    def raise_secure(
        self,
        error_type: type[SecureError],
        message: str,
        ErrorCode: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Raise a secure error.

        Args:
            error_type: Type of error to raise
            message: Error message
            ErrorCode: Optional error code
            context: Optional context
        """
        sanitized_message = ErrorSanitizer.sanitize_message(message)
        secure_error = error_type(sanitized_message, ErrorCode, context)
        self.Logger.error("Raising secure error: %s", secure_error.to_dict())
        raise secure_error

    @timeout(300)
    @standard_heal
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
    ) -> dict[str, int]:
        """L5 safety agent - operational only."""
        super().heal_repository()
        if _call_path is None:
            _call_path = set()
        agent_name = "SecureErrorHandler"
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L5 safety - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)


default_error_handler = SecureErrorHandler()


def handle_secure_error(error: Exception, context: dict[str, Any] | None = None) -> SecureError:
    """Handle an error using the default secure error handler.

    Args:
        error: Error to handle
        context: Optional context

    Returns:
        Secure error instance
    """
    return default_error_handler.handle_error(error, context)
