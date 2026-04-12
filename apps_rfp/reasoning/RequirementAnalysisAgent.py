"""
Requirement Analysis Agent — apps_rfp/reasoning

Agent for analyzing RFP requirements.
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
    _emit_reads_policy_state,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
    _emit_snapshots_state,
    emit_determinism_digest,
    emit_replay_key,
)
from apps_rfp.services.requirement_parser_service import RequirementParserService

_log = logging.getLogger(__name__)


class RequirementAnalysisAgent:
    """Agent for analyzing RFP requirements."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self._parser_service = RequirementParserService(config)

        emit_replay_key("req_analysis", "agent_init")
        emit_determinism_digest("req_analysis", "agent_init")
        _emit_applies_guardrail("p0", "req_analysis_agent", "agent_init")
        _emit_reads_policy_state("p0", "req_analysis_agent", "policy_binding")
        _emit_snapshots_state("p0", "req_analysis_agent", "agent_state")

    async def analyze_requirements(
        self,
        rfp_content: str,
        document_type: str = "rfp",
    ) -> dict[str, Any]:
        """Analyze requirements from RFP content."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L3_ORCHESTRATION,
            "RequirementAnalysisAgent.analyze_requirements",
        )
        _emit_orchestrates_workflow("p3", "req_analysis_agent", "analysis_workflow")
        _emit_dispatches_agent("p3", "req_analysis_agent", "analysis_dispatch")
        _emit_records_telemetry_event("p4", "req_analysis_agent", "analysis_start")

        requirements = self._parser_service.parse_document(rfp_content, document_type)
        summary = self._parser_service.get_requirement_summary()

        _log.info("Analyzed %d requirements from RFP", len(requirements))
        _emit_records_telemetry_event(
            "p4",
            "req_analysis_agent",
            f"analysis_complete:{len(requirements)}",
        )

        return {
            "success": True,
            "trace_id": _trace_id,
            "requirements_parsed": len(requirements),
            "requirements": requirements,
            "summary": summary,
        }

    @staticmethod
    def _make_trace_id(content: str) -> str:
        raw = f"req:{content[:100]}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
