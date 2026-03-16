"""
Skill Similarity Tool - Skill similarity computation
Refactored from compute_skill_similarity.py
"""

from __future__ import annotations

import logging
from typing import Any

from apps_rg.engines.base_resume_engine import BaseRGEngine

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

_emit_applies_guardrail("p0", "skill_similarity_tool", "p0_governance")
_emit_reads_policy_state("p0", "skill_similarity_tool", "policy_binding")
_emit_snapshots_state("p0", "skill_similarity_tool", "state_snapshot")
emit_replay_key("p0", "skill_similarity_tool")
emit_determinism_digest("p0", "skill_similarity_tool")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)


class SkillSimilarityTool(BaseRGEngine):
    """
    Computes similarity between skill sets.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="TOOLS.SKILL_SIMILARITY")

    async def execute(self, skills_a: list[str], skills_b: list[str]) -> float:
        """
        Calculate Jaccard similarity between skill sets.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SkillSimilarityTool.execute")

        set_a = {s.lower() for s in skills_a}
        set_b = {s.lower() for s in skills_b}
        if not set_a or not set_b:
            return 0.0
        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        similarity = intersection / union if union > 0 else 0.0
        self.record_pass(f"Skill similarity: {similarity:.2f}")
        return similarity
