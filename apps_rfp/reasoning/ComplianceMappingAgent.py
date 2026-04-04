"""
Compliance Mapping Agent — apps_rfp/reasoning

Agent for mapping compliance requirements.
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
from apps_rfp.services.compliance_checker_service import ComplianceCheckerService

_log = logging.getLogger(__name__)


class ComplianceMappingAgent:
    """Agent for mapping compliance requirements to proposal sections."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}
        self._compliance_service = ComplianceCheckerService(config)

        emit_replay_key("compliance_mapping", "agent_init")
        emit_determinism_digest("compliance_mapping", "agent_init")
        _emit_applies_guardrail("p0", "compliance_mapping_agent", "agent_init")
        _emit_snapshots_state("p0", "compliance_mapping_agent", "agent_state")

    async def map_compliance(
        self,
        requirements: list[dict[str, Any]],
        proposal_sections: list[dict[str, Any]],
        strict_mode: bool = False,
    ) -> dict[str, Any]:
        """Map and check compliance of proposal against requirements."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "ComplianceMappingAgent.map_compliance"
        )
        _emit_orchestrates_workflow("p3", "compliance_mapping_agent", "mapping_workflow")
        _emit_dispatches_agent("p3", "compliance_mapping_agent", "mapping_dispatch")
        _emit_records_telemetry_event("p4", "compliance_mapping_agent", "mapping_start")

        result = self._compliance_service.check_compliance(
            requirements, proposal_sections, strict_mode
        )

        _log.info(
            "Compliance check: %.1f%% compliant (%d/%d)",
            result.get("compliance_rate", 0) * 100,
            result.get("compliant_count", 0),
            result.get("total_requirements", 0),
        )
        _emit_records_telemetry_event(
            "p4", "compliance_mapping_agent", f"mapping_complete:{result.get('compliance_rate', 0):.2f}"
        )

        return {
            "success": True,
            "trace_id": _trace_id,
            "compliance": result,
        }

    @staticmethod
    def _make_trace_id(req_count: int, section_count: int) -> str:
        raw = f"compliance:{req_count}:{section_count}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
