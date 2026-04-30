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

from apps_rg.types import ResumeRequest, ResumeResult, ResumeSection

_log = logging.getLogger(__name__)


class ObservabilityAdapter:
    """Adapter for observability integration."""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self._metrics: list[dict] = []

    def emit_resume_start(self, request: ResumeRequest) -> dict[str, Any]:
        """Emit resume generation start event."""
        event = {
            "event_type": "resume_start",
            "trace_id": request.trace_id,
            "candidate_name": request.candidate_name,
            "target_role": request.target_role,
            "target_industry": request.target_industry,
            "experience_level": request.experience_level,
            "dry_run": request.dry_run,
            "timestamp": self._timestamp(),
        }
        self._metrics.append(event)
        return event

    def emit_resume_complete(self, result: ResumeResult) -> dict[str, Any]:
        """Emit resume generation completion event."""
        event = {
            "event_type": "resume_complete",
            "trace_id": result.trace_id,
            "candidate_name": result.candidate_name,
            "target_role": result.target_role,
            "status": result.status,
            "ats_score": result.ats_score,
            "quality_score": result.quality_score,
            "gate_passed": result.passed_gate,
            "sections_count": len(result.sections),
            "skill_matches": len(result.skill_matches),
            "violations": len(result.gate_violations),
            "timestamp": self._timestamp(),
        }
        self._metrics.append(event)
        return event

    def emit_section_generated(self, section: ResumeSection) -> dict[str, Any]:
        """Emit section generation event."""
        metric = {
            "event_type": "section_generated",
            "section_id": section.section_id,
            "section_type": section.section_type,
            "word_count": section.word_count,
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

_emit_records_telemetry_event("p4", 'apps_rg.integrations.observability_adapter', "module_loaded")
