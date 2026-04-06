"""
Brief Assembly Agent — apps_exec/reasoning

Agent for assembling executive briefs from synthesized content.
Aligned with apps_lic agent patterns with lifecycle trace integration.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
from apps_exec.services.brief_assembler_service import BriefAssemblerService

_log = logging.getLogger(__name__)


class BriefAssemblyAgent:
    """Agent for assembling executive briefs."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self._assembler_service = BriefAssemblerService(config)

        emit_replay_key("brief_assembly", "agent_init")
        emit_determinism_digest("brief_assembly", "agent_init")
        _emit_applies_guardrail("p0", "brief_assembly_agent", "agent_init")
        _emit_snapshots_state("p0", "brief_assembly_agent", "agent_state")

    async def assemble_brief(
        self,
        content_sections: list[dict[str, Any]],
        persona_id: str,
        target_word_count: int = 600,
    ) -> dict[str, Any]:
        """Assemble an executive brief."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "BriefAssemblyAgent.assemble_brief"
        )
        _emit_orchestrates_workflow("p3", "brief_assembly_agent", "assembly_workflow")
        _emit_dispatches_agent("p3", "brief_assembly_agent", "assembly_dispatch")
        _emit_records_telemetry_event("p4", "brief_assembly_agent", "assembly_start")

        brief = self._assembler_service.assemble_brief(
            content_sections, persona_id, target_word_count
        )

        _log.info("Assembled brief %s (%d words)", brief.get("brief_id"), brief.get("word_count"))
        _emit_records_telemetry_event("p4", "brief_assembly_agent", "assembly_complete")

        return {
            "success": True,
            "trace_id": _trace_id,
            "brief": brief,
        }

    @staticmethod
    def _make_trace_id(persona_id: str) -> str:
        raw = f"brief:{persona_id}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
