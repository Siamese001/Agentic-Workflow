"""
Knowledge Synthesis Agent — apps_research/reasoning

Agent for synthesizing research findings.
Aligned with apps_lic agent patterns with lifecycle trace integration.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
from apps_research.services.synthesis_engine_service import SynthesisEngineService

_log = logging.getLogger(__name__)


class KnowledgeSynthesisAgent:
    """Agent for synthesizing knowledge from insights."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self._synthesis_service = SynthesisEngineService(config)

        emit_replay_key("knowledge_synthesis", "agent_init")
        emit_determinism_digest("knowledge_synthesis", "agent_init")
        _emit_applies_guardrail("p0", "knowledge_synthesis_agent", "agent_init")
        _emit_snapshots_state("p0", "knowledge_synthesis_agent", "agent_state")

    async def synthesize(
        self,
        insights: list[dict[str, Any]],
        synthesis_mode: str = "thematic",
        target_audience: str = "technical",
    ) -> dict[str, Any]:
        """Synthesize insights into findings."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "KnowledgeSynthesisAgent.synthesize"
        )
        _emit_orchestrates_workflow("p3", "knowledge_synthesis_agent", "synthesis_workflow")
        _emit_dispatches_agent("p3", "knowledge_synthesis_agent", "synthesis_dispatch")
        _emit_records_telemetry_event("p4", "knowledge_synthesis_agent", "synthesis_start")

        synthesis = self._synthesis_service.synthesize_findings(
            insights, synthesis_mode, target_audience
        )

        _log.info(
            "Synthesized %d insights into %d themes",
            synthesis.get("insight_count", 0),
            synthesis.get("theme_count", 0),
        )
        _emit_records_telemetry_event(
            "p4", "knowledge_synthesis_agent", f"synthesis_complete:{synthesis.get('theme_count', 0)}"
        )

        return {
            "success": True,
            "trace_id": _trace_id,
            "synthesis": synthesis,
        }

    @staticmethod
    def _make_trace_id(insight_count: int) -> str:
        raw = f"synthesis:{insight_count}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
