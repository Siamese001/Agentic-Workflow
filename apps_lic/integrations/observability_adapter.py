"""
Observability Adapter — Integration with observability plane.

SVP Standards:
- Explicit metric emission
- Full trace context
- No silent failures
"""

from __future__ import annotations

from agentic_core.runtime.contracts.runtime_telemetry_decorators import (
    traces_execute,
)

import logging
from typing import Any

from apps_lic.types import CampaignRequest, CampaignResult, DraftPackage, ValidationResult

_log = logging.getLogger(__name__)


class ObservabilityAdapter:
    """Adapter for observability integration."""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self._metrics: list[dict] = []

    @traces_execute(layer="L6_OBSERVABILITY")
    def emit_campaign_start(self, request: CampaignRequest) -> dict[str, Any]:
        """Emit campaign start event."""
        event = {
            "event_type": "campaign_start",
            "trace_id": request.trace_id,
            "campaign_id": request.campaign_id,
            "target_audience": request.config.target_audience,
            "max_recipients": request.config.max_recipients,
            "dry_run": request.dry_run,
            "timestamp": self._timestamp(),
        }
        self._metrics.append(event)
        return event

    def emit_campaign_complete(self, result: CampaignResult) -> dict[str, Any]:
        """Emit campaign completion event."""
        event = {
            "event_type": "campaign_complete",
            "trace_id": result.trace_id,
            "campaign_id": result.campaign_id,
            "status": result.status,
            "drafts_count": len(result.drafts),
            "overall_score": result.overall_score,
            "gate_passed": result.passed_gate,
            "violations": len(result.gate_violations),
            "timestamp": self._timestamp(),
        }
        self._metrics.append(event)
        return event

    def emit_draft_created(self, draft_package: DraftPackage) -> dict[str, Any]:
        """Emit draft creation event."""
        event = {
            "event_type": "draft_created",
            "draft_length": len(draft_package.draft),
            "artifacts_count": len(draft_package.artifacts),
            "total_latency_ms": draft_package.total_latency_ms,
            "trace_id": draft_package.trace_id,
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
            "latency_ms": result.latency_ms,
            "timestamp": self._timestamp(),
        }
        self._metrics.append(event)
        return event

    def get_metrics(self) -> list[dict]:
        """Get all emitted metrics."""
        return self._metrics.copy()

    def _timestamp(self) -> str:
        """Generate ISO timestamp."""
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat()


# ----------------------------------------------------------------------
# OTEL coverage — module-load emit per check_apps_otel_coverage.py.
# Phase A of W-OTEL waves: structural wiring at import time.
# Phase B (per-method spans on execute() paths) is tracked separately.
# Pattern matches lifecycle_trace_contract.py and apps_research/engines.
# ----------------------------------------------------------------------
from agentic_core.runtime.contracts.lifecycle_trace_contract import (  # noqa: E402
    _emit_records_telemetry_event,
)

_emit_records_telemetry_event("p4", 'apps_lic.integrations.observability_adapter', "module_loaded")
