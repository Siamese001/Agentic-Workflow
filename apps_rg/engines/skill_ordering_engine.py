"""
Skill Ordering Engine - Sorts skills by JD match
Refactored from order_skills_by_relevance.py
"""

from __future__ import annotations

import logging
from typing import Any

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

_emit_applies_guardrail("p0", "skill_ordering_engine", "p0_governance")
_emit_reads_policy_state("p0", "skill_ordering_engine", "policy_binding")
_emit_snapshots_state("p0", "skill_ordering_engine", "state_snapshot")
emit_replay_key("p0", "skill_ordering_engine")
emit_determinism_digest("p0", "skill_ordering_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)


class SkillOrderingEngine(BaseRGEngine):
    """
    Orders skills by relevance to job description.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="REFINE.SKILL_ORDERING")

    async def execute(self, candidate_skills: list[str], jd_keywords: list[str]) -> list[str]:
        """
        Order skills by JD relevance.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SkillOrderingEngine.execute")

        self._mcp_audit("skill_ordering_start")
        scored_skills = []
        for skill in candidate_skills:
            score = 1.0 if skill in jd_keywords else 0.0
            scored_skills.append((skill, score))
        scored_skills.sort(key=lambda x: x[1], reverse=True)
        ordered = [skill for skill, _ in scored_skills]
        self.record_pass(f"Ordered {len(ordered)} skills by JD relevance")
        return ordered
