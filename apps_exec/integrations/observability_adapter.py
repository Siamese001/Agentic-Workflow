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

from apps_exec.types import BriefSection, ExecBriefRequest, ExecBriefResult

_log = logging.getLogger(__name__)


class ObservabilityAdapter:
    """Adapter for observability integration."""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self._metrics: list[dict] = []

    def emit_brief_start(self, request: ExecBriefRequest) -> dict[str, Any]:
        """Emit brief generation start event."""
        event = {
            "event_type": "brief_start",
            "trace_id": request.trace_id,
            "audience": request.audience,
            "tone": request.tone,
            "emphasis_areas": request.emphasis_areas,
            "dry_run": request.dry_run,
            "timestamp": self._timestamp(),
        }
        self._metrics.append(event)
        return event

    def emit_brief_complete(self, result: ExecBriefResult) -> dict[str, Any]:
        """Emit brief generation completion event."""
        event = {
            "event_type": "brief_complete",
            "trace_id": result.trace_id,
            "audience": result.audience,
            "tone": result.tone,
            "status": result.status,
            "quality_score": result.quality_score,
            "gate_passed": result.passed_gate,
            "sections_count": len(result.sections),
            "capabilities_count": len(result.capabilities_extracted),
            "violations": len(result.gate_violations),
            "timestamp": self._timestamp(),
        }
        self._metrics.append(event)
        return event

    def emit_section_generated(self, section: BriefSection) -> dict[str, Any]:
        """Emit section generation event."""
        metric = {
            "event_type": "section_generated",
            "section_id": section.section_id,
            "heading": section.heading,
            "word_count": section.word_count,
            "is_deterministic": section.is_deterministic,
            "evidence_count": len(section.evidence_anchors),
            "timestamp": self._timestamp(),
        }
        self._metrics.append(metric)
        return metric

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

_emit_records_telemetry_event("p4", 'apps_exec.integrations.observability_adapter', "module_loaded")
