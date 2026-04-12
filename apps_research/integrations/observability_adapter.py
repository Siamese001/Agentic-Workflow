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

from apps_research.types import ResearchRequest, ResearchResult, ResearchSection

_log = logging.getLogger(__name__)


class ObservabilityAdapter:
    """Adapter for observability integration."""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self._metrics: list[dict] = []

    def emit_research_start(self, request: ResearchRequest) -> dict[str, Any]:
        """Emit research generation start event."""
        event = {
            "event_type": "research_start",
            "trace_id": request.trace_id,
            "topic": request.topic,
            "mode": request.mode,
            "audience_style": request.audience_style,
            "dry_run": request.dry_run,
            "timestamp": self._timestamp(),
        }
        self._metrics.append(event)
        return event

    def emit_research_complete(self, result: ResearchResult) -> dict[str, Any]:
        """Emit research generation completion event."""
        event = {
            "event_type": "research_complete",
            "trace_id": result.trace_id,
            "topic": result.topic,
            "mode": result.mode,
            "status": result.status,
            "quality_score": result.quality_score,
            "gate_passed": result.passed_gate,
            "sections_count": len(result.sections),
            "sources_count": len(result.source_register),
            "violations": len(result.gate_violations),
            "timestamp": self._timestamp(),
        }
        self._metrics.append(event)
        return event

    def emit_section_generated(self, section: ResearchSection) -> dict[str, Any]:
        """Emit section generation event."""
        metric = {
            "event_type": "section_generated",
            "section_id": section.section_id,
            "heading": section.heading,
            "word_count": section.word_count,
            "is_deterministic": section.is_deterministic,
            "claim_type": section.claim_type,
            "source_count": len(section.sources),
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
