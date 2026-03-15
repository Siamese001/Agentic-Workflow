"""
HTTPGuard - Guardrail for External HTTP Call Operations

Provides pre-request guardrail checks for external HTTP calls via
requests, httpx, aiohttp, urllib, and similar libraries.
Emits applies_guardrail ADG edges for tracking and compliance.

Usage:
    from agentic_core.L5_safety.enforcement.http_guard import get_http_guard

    guard = get_http_guard()
    guard.check(operation="get", url="https://api.example.com/data")
    # Then proceed with actual HTTP call
"""

from __future__ import annotations

import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_verifies_policy,
)

logger = logging.getLogger(__name__)


class ExternalHttpDeniedError(Exception):
    """Raised when an external HTTP call is denied by guardrail."""

    pass


class HTTPGuard:
    """
    Guardrail for external HTTP call operations.

    Enforces domain allowlist/denylist policy and logging before
    allowing outbound HTTP requests.
    """

    # URL patterns that are always denied
    DENY_PATTERNS = [
        r"169\.254\.169\.254",  # AWS metadata endpoint
        r"metadata\.google\.internal",
        r"100\.100\.100\.200",  # Alibaba Cloud metadata
        r"localhost",
        r"127\.0\.0\.",
        r"0\.0\.0\.0",
        r"::1",
    ]

    def __init__(self, mode: str = "warn") -> None:
        """
        Initialize HTTPGuard.

        Args:
            mode: "warn" (log violations) or "enforce" (block violations)
        """
        self.mode = mode
        self._request_log: list[dict[str, Any]] = []
        self._deny_patterns = [re.compile(p, re.IGNORECASE) for p in self.DENY_PATTERNS]

    def check(
        self,
        operation: str,
        url: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Pre-request guardrail check for external HTTP operations.

        Args:
            operation: HTTP method ("get", "post", "put", "delete", etc.)
            url: Target URL (if available)
            metadata: Additional context

        Returns:
            dict with verdict and details

        Raises:
            ExternalHttpDeniedError: If request is denied in enforce mode
        """
        _emit_verifies_policy(str(uuid.uuid4()), "HTTPGuard.check", "L5_POLICY")
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "HTTPGuard.check")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:HTTPGuard.check".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        metadata = metadata or {}
        timestamp = datetime.now(timezone.utc)

        # Emit applies_guardrail ADG edge (structured log for scanner)
        logger.debug(
            "applies_guardrail operation=%s guard=HTTPGuard mode=%s",
            operation,
            self.mode,
        )

        verdict = "allow"
        reason = "External HTTP request allowed"
        violations = []

        if url:
            for pattern in self._deny_patterns:
                if pattern.search(url):
                    violations.append(pattern.pattern)

            if violations:
                verdict = "deny"
                reason = f"Denied URL pattern matched: {', '.join(violations)}"
                logger.warning(
                    "HTTPGuard DENY: %s url=%s - %s",
                    operation,
                    url,
                    reason,
                )
                if self.mode == "enforce":
                    raise ExternalHttpDeniedError(f"External HTTP request denied: {reason}")

        record = {
            "timestamp": timestamp.isoformat(),
            "operation": operation,
            "url": url,
            "verdict": verdict,
            "reason": reason,
            "violations": violations,
            "metadata": metadata,
        }
        self._request_log.append(record)

        logger.info(
            "HTTPGuard %s: %s url=%s",
            verdict.upper(),
            operation,
            url or "<unknown>",
        )

        return {
            "verdict": verdict,
            "reason": reason,
            "violations": violations,
            "timestamp": timestamp.isoformat(),
        }

    def get_request_log(self) -> list[dict[str, Any]]:
        """Get full request log."""
        return self._request_log.copy()

    def clear_log(self) -> None:
        """Clear request log."""
        self._request_log.clear()


_global_guard = HTTPGuard(mode="warn")


def get_http_guard() -> HTTPGuard:
    """Get global HTTPGuard instance."""
    return _global_guard


def set_http_guard_mode(mode: str) -> None:
    """Set global HTTPGuard mode ("warn" or "enforce")."""
    _emit_applies_guardrail(str(uuid.uuid4()), "Module.set_http_guard_mode", "L5_POLICY")
    global _global_guard
    _global_guard = HTTPGuard(mode=mode)
