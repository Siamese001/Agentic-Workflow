"""
Insight Extraction Agent — apps_research/reasoning

Agent for extracting insights from research sources.
Aligned with apps_lic agent patterns with lifecycle trace integration.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_agent,
    _emit_orchestrates_workflow,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
    _emit_snapshots_state,
    emit_determinism_digest,
    emit_replay_key,
)

_log = logging.getLogger(__name__)


class InsightExtractionAgent:
    """Agent for extracting insights from sources."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}

        emit_replay_key("insight_extraction", "agent_init")
        emit_determinism_digest("insight_extraction", "agent_init")
        _emit_applies_guardrail("p0", "insight_extraction_agent", "agent_init")
        _emit_snapshots_state("p0", "insight_extraction_agent", "agent_state")

    async def extract_insights(
        self,
        sources: list[dict[str, Any]],
        extraction_mode: str = "key_findings",
    ) -> dict[str, Any]:
        """Extract insights from research sources."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "InsightExtractionAgent.extract_insights"
        )
        _emit_orchestrates_workflow("p3", "insight_extraction_agent", "extraction_workflow")
        _emit_dispatches_agent("p3", "insight_extraction_agent", "extraction_dispatch")
        _emit_records_telemetry_event("p4", "insight_extraction_agent", "extraction_start")

        insights: list[dict[str, Any]] = []

        for i, source in enumerate(sources):
            insight = {
                "insight_id": f"insight_{_trace_id[:8]}_{i}",
                "source_id": source.get("source_id", f"source_{i}"),
                "key_point": f"Key finding from {source.get('title', 'source')}",
                "theme": "general",
                "confidence": source.get("relevance_score", 0.7),
            }
            insights.append(insight)

        _log.info("Extracted %d insights from %d sources", len(insights), len(sources))
        _emit_records_telemetry_event(
            "p4", "insight_extraction_agent", f"extraction_complete:{len(insights)}"
        )

        return {
            "success": True,
            "trace_id": _trace_id,
            "insights_extracted": len(insights),
            "insights": insights,
            "mode": extraction_mode,
        }

    @staticmethod
    def _make_trace_id(sources: list[dict[str, Any]]) -> str:
        raw = f"insights:{len(sources)}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
