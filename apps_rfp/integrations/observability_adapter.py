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

from apps_rfp.types import ProposalSection, RfpRequest, RfpResult

_log = logging.getLogger(__name__)


class ObservabilityAdapter:
    """Adapter for observability integration."""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self._metrics: list[dict] = []

    def emit_rfp_start(self, request: RfpRequest) -> dict[str, Any]:
        """Emit RFP generation start event."""
        event = {
            "event_type": "rfp_start",
            "trace_id": request.trace_id,
            "industry": request.industry,
            "architecture_posture": request.architecture_posture,
            "delivery_timeline_weeks": request.delivery_timeline_weeks,
            "dry_run": request.dry_run,
            "timestamp": self._timestamp(),
        }
        self._metrics.append(event)
        return event

    def emit_rfp_complete(self, result: RfpResult) -> dict[str, Any]:
        """Emit RFP generation completion event."""
        event = {
            "event_type": "rfp_complete",
            "trace_id": result.trace_id,
            "industry": result.industry,
            "status": result.status,
            "quality_score": result.quality_score,
            "gate_passed": result.passed_gate,
            "sections_count": len(result.sections),
            "roadmap_phases": len(result.roadmap),
            "risks_count": len(result.risks),
            "violations": len(result.gate_violations),
            "timestamp": self._timestamp(),
        }
        self._metrics.append(event)
        return event

    def emit_section_generated(self, section: ProposalSection) -> dict[str, Any]:
        """Emit section generation event."""
        metric = {
            "event_type": "section_generated",
            "section_id": section.section_id,
            "heading": section.heading,
            "word_count": section.word_count,
            "is_deterministic": section.is_deterministic,
            "assumptions_count": len(section.assumptions),
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
