"""
Skill Ordering Engine - Sorts skills by JD match
Refactored from order_skills_by_relevance.py
"""

from __future__ import annotations

import logging
from typing import Any

from apps_rg.engines.base_rg_engine import BaseRGEngine
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

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
