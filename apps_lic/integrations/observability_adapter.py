"""
Observability Adapter — Integration with observability plane.

SVP Standards:
- Explicit metric emission
- Full trace context
- No silent failures
"""

from __future__ import annotations

import logging
from typing import Any

from apps_lic.types import DraftPackage, ValidationResult

_log = logging.getLogger(__name__)


class ObservabilityAdapter:
    """Adapter for observability integration."""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self._metrics: list[dict] = []

    def emit_draft_created(self, draft_package: DraftPackage) -> dict[str, Any]:
        """Emit draft creation event."""
        event = {
            "event_type": "draft_created",
            "draft_length": len(draft_package.draft),
            "artifacts_count": len(draft_package.artifacts),
            "total_latency_ms": draft_package.total_latency_ms,
            "timestamp": self._timestamp(),
        }
        self._metrics.append(event)
        return event

    def emit_validation_complete(self, result: ValidationResult) -> dict[str, Any]:
        """Emit validation completion event."""
        event = {
            "event_type": "validation_complete",
            "passed": result.passed,
            "attempts": result.attempts,
            "reasons_count": len(result.reasons),
            "timestamp": self._timestamp(),
        }
        self._metrics.append(event)
        return event

    def emit_campaign_complete(
        self, draft_package: DraftPackage, validation: ValidationResult
    ) -> dict[str, Any]:
        """Emit campaign completion event."""
        event = {
            "event_type": "campaign_complete",
            "validation_passed": validation.passed,
            "draft_length": len(draft_package.draft),
            "artifacts_count": len(draft_package.artifacts),
            "timestamp": self._timestamp(),
        }
        self._metrics.append(event)
        return event

    def get_metrics(self) -> list[dict]:
        """Get all emitted metrics."""
        return self._metrics.copy()

    def _timestamp(self) -> str:
        """Generate ISO timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"
