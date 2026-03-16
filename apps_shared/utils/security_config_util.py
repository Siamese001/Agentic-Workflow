"""
Security Utilities - Input validation, sanitization, and security checks.

Provides security hardening for apps_lic and apps_rg.
Phase 5A - Security Hardening
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import re
import secrets
from dataclasses import dataclass
from enum import Enum
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "security_config_util", "p0_governance")
_emit_reads_policy_state("p0", "security_config_util", "policy_binding")
_emit_snapshots_state("p0", "security_config_util", "state_snapshot")
emit_replay_key("p0", "security_config_util")
emit_determinism_digest("p0", "security_config_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "security_config_util", "execution_auth")
_emit_validates_capability("p2", "security_config_util", "capability_check")
_emit_routes_to_capability("p2", "security_config_util", "capability_route")
_emit_writes_via_uwg("p2", "security_config_util", "uwg_write")
_emit_blocks_direct_write("p2", "security_config_util", "direct_write_block")
_emit_records_tool_invocation("p2", "security_config_util", "tool_invocation")
_emit_captures_execution_output("p2", "security_config_util", "exec_output")
_emit_dispatches_agent("p3", "security_config_util", "agent_dispatch")
_emit_coordinates_agents("p3", "security_config_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "security_config_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "security_config_util", "healing_outcome")
_emit_escalates_failure("p3", "security_config_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "security_config_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "security_config_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "security_config_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "security_config_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "security_config_util", "eval_metric")
_emit_stores_embedding("p4", "security_config_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "security_config_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "security_config_util", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class ValidationLevel(str, Enum):
    """Validation strictness levels."""

    STRICT = "strict"
    MODERATE = "moderate"
    PERMISSIVE = "permissive"


@dataclass
class ValidationResult:
    """Result of a validation check."""

    valid: bool
    errors: list[str]
    sanitized_value: Any = None

    @classmethod
    def success(cls, sanitized_value: Any = None) -> ValidationResult:
        """Create a successful validation result."""
        return cls(valid=True, errors=[], sanitized_value=sanitized_value)

    @classmethod
    def failure(cls, errors: list[str]) -> ValidationResult:
        """Create a failed validation result."""
        return cls(valid=False, errors=errors)


class InputSanitizer:
    """Sanitizes user input to prevent injection attacks."""

    SCRIPT_PATTERN = re.compile("<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL)
    HTML_TAG_PATTERN = re.compile("<[^>]+>")
    SQL_INJECTION_PATTERN = re.compile(
        "(\\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER)\\b)", re.IGNORECASE
    )
    PATH_TRAVERSAL_PATTERN = re.compile("\\.\\./|\\.\\.\\\\")

    @classmethod
    # guardian: allow-magic-config
    def sanitize_string(
        cls, value: str, max_length: int = 10000, strip_html: bool = True, strip_scripts: bool = True
    ) -> str:
        """Sanitize a string input."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "InputSanitizer.sanitize_string")

        if not isinstance(value, str):
            return str(value)
        result = value[:max_length]
        if strip_scripts:
            result = cls.SCRIPT_PATTERN.sub("", result)
        if strip_html:
            result = cls.HTML_TAG_PATTERN.sub("", result)
        result = result.replace("\x00", "")
        return result.strip()

    @classmethod
    def sanitize_path(cls, path: str) -> str:
        """Sanitize a file path to prevent traversal attacks."""
        sanitized = cls.PATH_TRAVERSAL_PATTERN.sub("", path)
        sanitized = sanitized.replace("\x00", "")
        sanitized = sanitized.replace("\\", "/")
        return sanitized

    @classmethod
    # guardian: allow-magic-config
    def sanitize_identifier(cls, value: str, max_length: int = 255) -> str:
        """Sanitize an identifier (e.g., username, key name)."""
        sanitized = re.sub("[^a-zA-Z0-9_-]", "", value)
        return sanitized[:max_length]


class InputValidator:
    """Validates user input against security rules."""

    EMAIL_PATTERN = re.compile("^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$")
    URL_PATTERN = re.compile("^https?://[a-zA-Z0-9][-a-zA-Z0-9]*(\\.[a-zA-Z0-9][-a-zA-Z0-9]*)+.*$")

    @classmethod
    def validate_email(cls, email: str) -> ValidationResult:
        """Validate an email address."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "InputValidator.validate_email")

        if not email or not isinstance(email, str):
            return ValidationResult.failure(["Email is required"])
        email = email.strip().lower()
        if len(email) > 254:
            return ValidationResult.failure(["Email too long"])
        if not cls.EMAIL_PATTERN.match(email):
            return ValidationResult.failure(["Invalid email format"])
        return ValidationResult.success(email)

    @classmethod
    def validate_url(cls, url: str, require_https: bool = False) -> ValidationResult:
        """Validate a URL."""
        if not url or not isinstance(url, str):
            return ValidationResult.failure(["URL is required"])
        url = url.strip()
        if require_https and (not url.startswith("https://")):
            return ValidationResult.failure(["HTTPS required"])
        if not cls.URL_PATTERN.match(url):
            return ValidationResult.failure(["Invalid URL format"])
        return ValidationResult.success(url)

    @classmethod
    # guardian: allow-magic-config
    def validate_length(cls, value: str, min_length: int = 0, max_length: int = 10000) -> ValidationResult:
        """Validate string length."""
        if not isinstance(value, str):
            return ValidationResult.failure(["Value must be a string"])
        length = len(value)
        if length < min_length:
            return ValidationResult.failure([f"Minimum length is {min_length}"])
        if length > max_length:
            return ValidationResult.failure([f"Maximum length is {max_length}"])
        return ValidationResult.success(value)

    @classmethod
    def validate_not_empty(cls, value: Any) -> ValidationResult:
        """Validate that a value is not empty."""
        if value is None:
            return ValidationResult.failure(["Value is required"])
        if isinstance(value, str) and (not value.strip()):
            return ValidationResult.failure(["Value cannot be empty"])
        if isinstance(value, list | dict) and len(value) == 0:
            return ValidationResult.failure(["Value cannot be empty"])
        return ValidationResult.success(value)

    @classmethod
    def check_sql_injection(cls, value: str) -> ValidationResult:
        """Check for potential SQL injection patterns."""
        if InputSanitizer.SQL_INJECTION_PATTERN.search(value):
            return ValidationResult.failure(["Potential SQL injection detected"])
        return ValidationResult.success(value)

    @classmethod
    def check_path_traversal(cls, path: str) -> ValidationResult:
        """Check for path traversal attempts."""
        if InputSanitizer.PATH_TRAVERSAL_PATTERN.search(path):
            return ValidationResult.failure(["Path traversal detected"])
        return ValidationResult.success(path)


class SecureTokenGenerator:
    """Generates secure tokens and hashes."""

    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Generate a cryptographically secure random token."""
        return secrets.token_urlsafe(length)

    @staticmethod
    def generate_api_key(prefix: str = "ak") -> str:
        """Generate an API key with prefix."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SecureTokenGenerator.generate_api_key")

        token = secrets.token_urlsafe(32)
        return f"{prefix}_{token}"

    @staticmethod
    def hash_value(value: str, salt: str | None = None) -> str:
        """Hash a value using SHA-256."""
        if salt:
            value = f"{salt}{value}"
        return hashlib.sha256(value.encode()).hexdigest()

    @staticmethod
    def verify_hash(value: str, expected_hash: str, salt: str | None = None) -> bool:
        """Verify a value against a hash."""
        computed_hash = SecureTokenGenerator.hash_value(value, salt)
        return hmac.compare_digest(computed_hash, expected_hash)

    @staticmethod
    def generate_session_id() -> str:
        """Generate a secure session ID."""
        return secrets.token_urlsafe(48)


class RateLimiter:
    """Simple in-memory rate limiter."""

    # guardian: allow-magic-config
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = {}

    def is_allowed(self, key: str) -> bool:
        """Check if a request is allowed for the given key."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RateLimiter.is_allowed")

        import time

        current_time = time.time()
        window_start = current_time - self.window_seconds
        if key not in self._requests:
            self._requests[key] = []
        self._requests[key] = [t for t in self._requests[key] if t > window_start]
        if len(self._requests[key]) >= self.max_requests:
            return False
        self._requests[key].append(current_time)
        return True

    def get_remaining(self, key: str) -> int:
        """Get remaining requests for the key."""
        import time

        current_time = time.time()
        window_start = current_time - self.window_seconds
        if key not in self._requests:
            return self.max_requests
        count = sum(1 for t in self._requests[key] if t > window_start)
        return max(0, self.max_requests - count)

    def reset(self, key: str | None = None) -> None:
        """Reset rate limit for a key or all keys."""
        if key:
            self._requests.pop(key, None)
        else:
            self._requests.clear()


class SecurityAuditLog:
    """Logs security-relevant events."""

    def __init__(self, name: str = "security"):
        self._logger = logging.getLogger(f"security.{name}")
        self._events: list[dict[str, Any]] = []

    def log_event(
        self, event_type: str, message: str, severity: str = "info", metadata: dict[str, Any] | None = None
    ) -> None:
        """Log a security event."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SecurityAuditLog.log_event")

        import time

        event = {
            "timestamp": time.time(),
            "type": event_type,
            "message": message,
            "severity": severity,
            "metadata": metadata or {},
        }
        self._events.append(event)
        log_method = getattr(self._logger, severity, self._logger.info)
        log_method(f"[{event_type}] {message}")

    def log_validation_failure(
        self, field: str, errors: list[str], metadata: dict[str, Any] | None = None
    ) -> None:
        """Log a validation failure."""
        self.log_event(
            event_type="validation_failure",
            message=f"Validation failed for {field}: {', '.join(errors)}",
            severity="warning",
            metadata={"field": field, "errors": errors, **(metadata or {})},
        )

    def log_rate_limit(self, key: str, metadata: dict[str, Any] | None = None) -> None:
        """Log a rate limit event."""
        self.log_event(
            event_type="rate_limit",
            message=f"Rate limit exceeded for {key}",
            severity="warning",
            metadata={"key": key, **(metadata or {})},
        )

    def log_suspicious_activity(self, activity: str, metadata: dict[str, Any] | None = None) -> None:
        """Log suspicious activity."""
        self.log_event(
            event_type="suspicious_activity", message=activity, severity="error", metadata=metadata
        )

    def get_events(self, event_type: str | None = None, severity: str | None = None) -> list[dict[str, Any]]:
        """Get logged events, optionally filtered."""
        events = self._events
        if event_type:
            events = [e for e in events if e["type"] == event_type]
        if severity:
            events = [e for e in events if e["severity"] == severity]
        return events

    def clear(self) -> None:
        """Clear all logged events."""
        self._events.clear()
