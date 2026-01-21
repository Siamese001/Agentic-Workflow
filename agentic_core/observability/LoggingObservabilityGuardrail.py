"""
Logging & Observability Guardrail - Consolidated Secure Logging

Merges:
- secure_logger
- audit_logs

Composable Rules:
- secure_logging: Secure log handling
- audit_trails: Audit log management
"""

from __future__ import annotations

import hashlib
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class LogLevel(Enum):
    """Log levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    AUDIT = "audit"


@dataclass
class LogEntry:
    """Secure log entry."""
    level: LogLevel
    message: str
    timestamp: float
    source: str
    correlation_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    sanitized: bool = False


@dataclass
class AuditEntry:
    """Audit trail entry."""
    audit_id: str
    action: str
    actor: str
    target: str
    timestamp: float
    outcome: str  # "success", "failure", "blocked"
    details: dict[str, Any] = field(default_factory=dict)


class LoggingObservabilityGuardrail:
    """
    Consolidated Logging & Observability Guardrail.

    Provides unified logging with:
    - Secure log handling (PII scrubbing)
    - Audit trail management
    - Log correlation
    - Retention policies
    """

    def __init__(self):
        """Initialize logging guardrail."""
        self.enabled_rules: list[str] = [
            "secure_logging",
            "audit_trails",
        ]

        # PII patterns to scrub
        self.pii_patterns = {
            "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
            "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
            "api_key": r"(sk-|api[_-]?key)[a-zA-Z0-9]{20,}",
        }

        # Log storage
        self.logs: list[LogEntry] = []
        self.audit_trail: list[AuditEntry] = []
        self.max_log_size = 10000
        self.max_audit_size = 5000

        # Statistics
        self.logs_written = 0
        self.pii_scrubbed = 0
        self.audits_created = 0

    def log(
        self,
        level: LogLevel,
        message: str,
        source: str,
        correlation_id: str | None = None,
        metadata: dict[str, Any] | None = None
    ) -> LogEntry:
        """
        Create secure log entry.

        Args:
            level: Log level
            message: Log message
            source: Source of log
            correlation_id: Optional correlation ID
            metadata: Optional metadata

        Returns:
            LogEntry
        """
        self.logs_written += 1

        # Sanitize message if secure logging enabled
        sanitized_message = message
        was_sanitized = False

        if "secure_logging" in self.enabled_rules:
            sanitized_message, was_sanitized = self._sanitize_message(message)

        entry = LogEntry(
            level=level,
            message=sanitized_message,
            timestamp=time.time(),
            source=source,
            correlation_id=correlation_id,
            metadata=metadata or {},
            sanitized=was_sanitized
        )

        self.logs.append(entry)

        # Enforce max size
        while len(self.logs) > self.max_log_size:
            self.logs.pop(0)

        return entry

    def audit(
        self,
        action: str,
        actor: str,
        target: str,
        outcome: str,
        details: dict[str, Any] | None = None
    ) -> AuditEntry:
        """
        Create audit trail entry.

        Args:
            action: Action performed
            actor: Who performed action
            target: Target of action
            outcome: Outcome (success/failure/blocked)
            details: Optional details

        Returns:
            AuditEntry
        """
        if "audit_trails" not in self.enabled_rules:
            return AuditEntry(
                audit_id="disabled",
                action=action,
                actor=actor,
                target=target,
                timestamp=time.time(),
                outcome=outcome
            )

        self.audits_created += 1

        # Generate audit ID
        audit_id = f"audit_{self.audits_created}_{hashlib.sha256(f'{action}{actor}{time.time()}'.encode()).hexdigest()[:8]}"

        entry = AuditEntry(
            audit_id=audit_id,
            action=action,
            actor=actor,
            target=target,
            timestamp=time.time(),
            outcome=outcome,
            details=details or {}
        )

        self.audit_trail.append(entry)

        # Enforce max size
        while len(self.audit_trail) > self.max_audit_size:
            self.audit_trail.pop(0)

        return entry

    def _sanitize_message(self, message: str) -> tuple[str, bool]:
        """Sanitize message by scrubbing PII."""
        sanitized = message
        was_sanitized = False

        for pii_type, pattern in self.pii_patterns.items():
            if re.search(pattern, sanitized):
                sanitized = re.sub(pattern, f"[{pii_type.upper()}_REDACTED]", sanitized)
                was_sanitized = True
                self.pii_scrubbed += 1

        return sanitized, was_sanitized

    def get_logs(
        self,
        level: LogLevel | None = None,
        source: str | None = None,
        limit: int = 100
    ) -> list[dict[str, Any]]:
        """
        Get logs with optional filtering.

        Args:
            level: Filter by level
            source: Filter by source
            limit: Maximum entries

        Returns:
            List of log entries
        """
        filtered = self.logs

        if level:
            filtered = [l for l in filtered if l.level == level]

        if source:
            filtered = [l for l in filtered if l.source == source]

        return [
            {
                "level": l.level.value,
                "message": l.message,
                "timestamp": l.timestamp,
                "source": l.source,
                "correlation_id": l.correlation_id,
                "sanitized": l.sanitized
            }
            for l in filtered[-limit:]
        ]

    def get_audit_trail(
        self,
        action: str | None = None,
        actor: str | None = None,
        limit: int = 100
    ) -> list[dict[str, Any]]:
        """
        Get audit trail with optional filtering.

        Args:
            action: Filter by action
            actor: Filter by actor
            limit: Maximum entries

        Returns:
            List of audit entries
        """
        filtered = self.audit_trail

        if action:
            filtered = [a for a in filtered if a.action == action]

        if actor:
            filtered = [a for a in filtered if a.actor == actor]

        return [
            {
                "audit_id": a.audit_id,
                "action": a.action,
                "actor": a.actor,
                "target": a.target,
                "timestamp": a.timestamp,
                "outcome": a.outcome
            }
            for a in filtered[-limit:]
        ]

    def get_statistics(self) -> dict[str, Any]:
        """Get logging statistics."""
        return {
            "logs_written": self.logs_written,
            "pii_scrubbed": self.pii_scrubbed,
            "audits_created": self.audits_created,
            "current_log_size": len(self.logs),
            "current_audit_size": len(self.audit_trail),
            "enabled_rules": self.enabled_rules
        }
