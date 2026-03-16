"""
Resume Planning Engine - L1 Planner
Refactored from resume_planner.py
Now delegates to logic_nodes for deterministic logic extraction.
"""

from __future__ import annotations

import logging
from typing import Any

from apps_rg.types.resume_section_node import ResumeSectionNode

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from apps_rg.engines.base_rg_engine import BaseRGEngine

_emit_applies_guardrail("p0", "resume_planning_engine", "p0_governance")
_emit_reads_policy_state("p0", "resume_planning_engine", "policy_binding")
_emit_snapshots_state("p0", "resume_planning_engine", "state_snapshot")
emit_replay_key("p0", "resume_planning_engine")
emit_determinism_digest("p0", "resume_planning_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)


class ResumePlanningEngine(BaseRGEngine):
    """
    L1 Planning - Role/Industry focus determination.

    Now delegates role/industry extraction to ResumeSectionNode logic node
    to comply with Blueprint Depth-2 Structure requirements.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="ORCHESTRATION.PLANNING")
        self.section_node = ResumeSectionNode(config=self.config.get("section_config", {}))

    async def execute(self, job_description: str, candidate_profile: dict[str, Any]) -> dict[str, Any]:
        """
        Create initial resume generation plan using delegated logic nodes.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ResumePlanningEngine.execute")

        self._mcp_audit("planning_start")
        section_analysis = self.section_node(job_description, candidate_profile)
        plan = {
            "target_role": section_analysis.role_result.role,
            "target_industry": section_analysis.industry_result.industry,
            "role_confidence": section_analysis.role_result.confidence,
            "industry_confidence": section_analysis.industry_result.confidence,
            "seniority_level": section_analysis.role_result.seniority_level,
            "required_sections": section_analysis.section_analysis.required_sections,
            "optional_sections": section_analysis.section_analysis.optional_sections,
            "emphasis_areas": section_analysis.section_analysis.emphasis_areas,
            "section_weights": section_analysis.section_analysis.section_weights,
            "k_nodes_required": ["K.1", "K.2", "K.3", "K.4", "K.5", "K.6", "K.7", "K.8", "K.9"],
        }
        if "leadership" in job_description.lower():
            plan["emphasis_areas"].append("K.9")
        if "technical" in job_description.lower() or "engineer" in job_description.lower():
            plan["emphasis_areas"].extend(["K.6", "K.7"])
        self.record_pass("Resume plan created using logic nodes", data=plan)
        return plan
