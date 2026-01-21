from __future__ import annotations

"""Secure Logging Utility - Prevents sensitive data leakage in logs.

This module provides a secure logging wrapper that sanitizes log messages
to prevent PII, secrets, or sensitive user data from being written to logs.
"""

import json
import logging
import re
from pathlib import Path

# Patterns for sensitive data detection
SENSITIVE_PATTERNS = [
    # Email addresses
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    # Phone numbers (US format)
    r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
    # Social Security Numbers
    r"\b\d{3}-\d{2}-\d{4}\b",
    # Credit card numbers
    r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
    # API keys (common patterns)
    r'(?:api[_-]?key|apikey|api[_-]?secret|secret[_-]?key|token)[\s:=]+["\']?[A-Za-z0-9+/]{20,}["\']?',
    # Passwords
    r'(?:password|passwd|pwd)[\s:=]+["\']?[^\s"\']{6,}["\']?',
    # URLs with potential sensitive data
    r"https?://[^\s]*\?(?:[^\s]*[&=])*(?:token|key|secret|password)=[^\s&]*",
    # JSON fields with common sensitive keys
    r'"(?:password|secret|token|api_key|credit_card|ssn|phone|email)"\s*:\s*"[^"]*"',
]

# Sanitization patterns
SANITIZATION_PATTERNS = [
    # User context data
    (r'user[_-]?data["\']?\s*[:=]\s*{[^}]*}', "user_data={REDACTED}"),
    (r'context["\']?\s*[:=]\s*{[^}]*}', "context={REDACTED}"),
    (r'raw_output["\']?\s*[:=]\s*["\']?[^"\'\n]*["\']?', "raw_output={REDACTED}"),
    (r'content["\']?\s*[:=]\s*["\']?[^"\'\n]*["\']?', "content={REDACTED}"),
    # Large JSON objects
    (r"\{[^{}]{200,}\}", "{DATA_REDACTED}"),
    # Long string values (potential data)
    (r'["\'][^"\']{100,}["\']', '"REDACTED"'),
]


class SecureLogger:
    """Secure logging wrapper that sanitizes sensitive information."""

    def __init__(self, name: str, level: int = logging.INFO):
        """Initialize the secure Logger.

        Args:
            name: Logger name
            level: Logging level
        """
        self.Logger = logging.getLogger(name)
        self.Logger.setLevel(level)

        # Configure handler if not already configured
        if not self.Logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.Logger.addHandler(handler)

    def _sanitize_message(self, message: str) -> str:
        """Sanitize a log message to remove sensitive data.

        Args:
            message: Original log message

        Returns:
            Sanitized message safe for logging
        """
        sanitized = message

        # Apply sensitive data patterns
        for pattern in SENSITIVE_PATTERNS:
            sanitized = re.sub(pattern, "{REDACTED}", sanitized, flags=re.IGNORECASE)

        # Apply sanitization patterns
        for pattern, replacement in SANITIZATION_PATTERNS:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

        return sanitized

    def _sanitize_args(self, *args) -> tuple:
        """Sanitize log arguments.

        Args:
            *args: Log arguments

        Returns:
            Sanitized arguments tuple
        """
        sanitized_args = []
        for arg in args:
            if isinstance(arg, str):
                sanitized_args.append(self._sanitize_message(arg))
            elif isinstance(arg, dict | list):
                # Convert to JSON and sanitize
                json_str = json.dumps(arg, default=str)
                self._sanitize_message(json_str)
                sanitized_args.append("<sanitized_data>")
            else:
                sanitized_args.append(str(arg))

        return tuple(sanitized_args)

    def debug(self, message: str, *args, **kwargs):
        """Log debug message with sanitization."""
        sanitized_message = self._sanitize_message(message)
        sanitized_args = self._sanitize_args(*args)
        self.Logger.debug(sanitized_message, *sanitized_args, **kwargs)

    def info(self, message: str, *args, **kwargs):
        """Log info message with sanitization."""
        sanitized_message = self._sanitize_message(message)
        sanitized_args = self._sanitize_args(*args)
        self.Logger.info(sanitized_message, *sanitized_args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        """Log warning message with sanitization."""
        sanitized_message = self._sanitize_message(message)
        sanitized_args = self._sanitize_args(*args)
        self.Logger.warning(sanitized_message, *sanitized_args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        """Log error message with sanitization."""
        sanitized_message = self._sanitize_message(message)
        sanitized_args = self._sanitize_args(*args)
        self.Logger.error(sanitized_message, *sanitized_args, **kwargs)

    def critical(self, message: str, *args, **kwargs):
        """Log critical message with sanitization."""
        sanitized_message = self._sanitize_message(message)
        sanitized_args = self._sanitize_args(*args)
        self.Logger.critical(sanitized_message, *sanitized_args, **kwargs)

    def exception(self, message: str, *args, **kwargs):
        """Log exception with sanitization."""
        sanitized_message = self._sanitize_message(message)
        sanitized_args = self._sanitize_args(*args)
        self.Logger.exception(sanitized_message, *sanitized_args, **kwargs)


class SecureLoggerAdapter:
    """Adapter to wrap existing loggers with security."""

    def __init__(self, Logger: logging.Logger):
        """Initialize the adapter.

        Args:
            Logger: Existing Logger to wrap
        """
        self.Logger = Logger

    def _sanitize(self, message: str) -> str:
        """Quick sanitize for common patterns."""
        # Quick redaction for obvious sensitive data
        if any(
            keyword in message.lower() for keyword in ["password", "secret", "token", "api_key"]
        ):
            return f"{message[:50]}... [REDACTED]"
        return message

    def debug(self, message: str, *args, **kwargs):
        """Debug with sanitization."""
        self.Logger.debug(self._sanitize(message), *args, **kwargs)

    def info(self, message: str, *args, **kwargs):
        """Info with sanitization."""
        self.Logger.info(self._sanitize(message), *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        """Warning with sanitization."""
        self.Logger.warning(self._sanitize(message), *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        """Error with sanitization."""
        self.Logger.error(self._sanitize(message), *args, **kwargs)

    def critical(self, message: str, *args, **kwargs):
        """Critical with sanitization."""
        self.Logger.critical(self._sanitize(message), *args, **kwargs)


def get_secure_logger(name: str) -> SecureLogger:
    """Get a secure Logger instance.

    Args:
        name: Logger name

    Returns:
        SecureLogger instance
    """
    return SecureLogger(name)


def secure_existing_logger(Logger: logging.Logger) -> SecureLoggerAdapter:
    """Wrap an existing Logger with security.

    Args:
        Logger: Existing Logger to wrap

    Returns:
        SecureLoggerAdapter instance
    """
    return SecureLoggerAdapter(Logger)


# Context manager for temporary secure logging
class SecureLogContext:
    """Context manager for secure logging in a specific block."""

    def __init__(self, logger_name: str):
        """Initialize context.

        Args:
            logger_name: Name of Logger to secure
        """
        self.logger_name = logger_name
        self.original_logger = None
        self.secure_logger = None

    def __enter__(self):
        """Enter secure logging context."""
        self.original_logger = logging.getLogger(self.logger_name)
        self.secure_logger = secure_existing_logger(self.original_logger)
        return self.secure_logger

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit secure logging context."""
        pass


# Audit function to check for potential log leakage
def audit_logs_for_leakage(log_file: Path) -> list[str]:
    """Audit log file for potential sensitive data leakage.

    Args:
        log_file: Path to log file

    Returns:
        List of lines with potential leakage
    """
    issues = []

    try:
        with open(log_file) as f:
            for line_num, line in enumerate(f, 1):
                # Check for sensitive patterns
                for pattern in SENSITIVE_PATTERNS:
                    if re.search(pattern, line):
                        issues.append(f"Line {line_num}: Potential sensitive data detected")
                        break

                # Check for large data dumps
                if len(line) > 1000:
                    issues.append(f"Line {line_num}: Excessively long log entry")

    except Exception as e:
        issues.append(f"Failed to audit log file: {e}")

    return issues
