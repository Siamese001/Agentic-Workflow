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

    # Patterns for dangerous content
    SCRIPT_PATTERN = re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL)
    HTML_TAG_PATTERN = re.compile(r"<[^>]+>")
    SQL_INJECTION_PATTERN = re.compile(
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER)\b)",
        re.IGNORECASE,
    )
    PATH_TRAVERSAL_PATTERN = re.compile(r"\.\./|\.\.\\")

    @classmethod
    def sanitize_string(
        cls,
        value: str,
        max_length: int = 10000,
        strip_html: bool = True,
        strip_scripts: bool = True,
    ) -> str:
        """Sanitize a string input."""
        if not isinstance(value, str):
            return str(value)

        # Truncate to max length
        result = value[:max_length]

        # Strip script tags
        if strip_scripts:
            result = cls.SCRIPT_PATTERN.sub("", result)

        # Strip HTML tags
        if strip_html:
            result = cls.HTML_TAG_PATTERN.sub("", result)

        # Strip null bytes
        result = result.replace("\x00", "")

        return result.strip()

    @classmethod
    def sanitize_path(cls, path: str) -> str:
        """Sanitize a file path to prevent traversal attacks."""
        # Remove path traversal sequences
        sanitized = cls.PATH_TRAVERSAL_PATTERN.sub("", path)

        # Remove null bytes
        sanitized = sanitized.replace("\x00", "")

        # Normalize separators
        sanitized = sanitized.replace("\\", "/")

        return sanitized

    @classmethod
    def sanitize_identifier(cls, value: str, max_length: int = 255) -> str:
        """Sanitize an identifier (e.g., username, key name)."""
        # Only allow alphanumeric, underscore, hyphen
        sanitized = re.sub(r"[^a-zA-Z0-9_-]", "", value)
        return sanitized[:max_length]


class InputValidator:
    """Validates user input against security rules."""

    EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    URL_PATTERN = re.compile(r"^https?://[a-zA-Z0-9][-a-zA-Z0-9]*(\.[a-zA-Z0-9][-a-zA-Z0-9]*)+.*$")

    @classmethod
    def validate_email(cls, email: str) -> ValidationResult:
        """Validate an email address."""
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

        if require_https and not url.startswith("https://"):
            return ValidationResult.failure(["HTTPS required"])

        if not cls.URL_PATTERN.match(url):
            return ValidationResult.failure(["Invalid URL format"])

        return ValidationResult.success(url)

    @classmethod
    def validate_length(
        cls,
        value: str,
        min_length: int = 0,
        max_length: int = 10000,
    ) -> ValidationResult:
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

        if isinstance(value, str) and not value.strip():
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

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = {}

    def is_allowed(self, key: str) -> bool:
        """Check if a request is allowed for the given key."""
        import time

        current_time = time.time()
        window_start = current_time - self.window_seconds

        if key not in self._requests:
            self._requests[key] = []

        # Remove old requests outside the window
        self._requests[key] = [t for t in self._requests[key] if t > window_start]

        # Check if under limit
        if len(self._requests[key]) >= self.max_requests:
            return False

        # Record this request
        self._requests[key].append(current_time)
        return True

    def get_remaining(self, key: str) -> int:
        """Get remaining requests for the key."""
        import time

        current_time = time.time()
        window_start = current_time - self.window_seconds

        if key not in self._requests:
            return self.max_requests

        # Count requests in window
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
        self,
        event_type: str,
        message: str,
        severity: str = "info",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Log a security event."""
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
        self,
        field: str,
        errors: list[str],
        metadata: dict[str, Any] | None = None,
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

    def log_suspicious_activity(
        self,
        activity: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Log suspicious activity."""
        self.log_event(
            event_type="suspicious_activity",
            message=activity,
            severity="error",
            metadata=metadata,
        )

    def get_events(
        self,
        event_type: str | None = None,
        severity: str | None = None,
    ) -> list[dict[str, Any]]:
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
