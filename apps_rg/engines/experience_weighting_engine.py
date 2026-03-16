"""
Experience Weighting Engine - Experience relevance weighting
Refactored from weight_experience_match.py
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

_emit_applies_guardrail("p0", "experience_weighting_engine", "p0_governance")
_emit_reads_policy_state("p0", "experience_weighting_engine", "policy_binding")
_emit_snapshots_state("p0", "experience_weighting_engine", "state_snapshot")
emit_replay_key("p0", "experience_weighting_engine")
emit_determinism_digest("p0", "experience_weighting_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)


class ExperienceWeightingEngine(BaseRGEngine):
    """
    Weights experience sections by relevance to target role.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="QUALITY.EXPERIENCE_WEIGHTING")

    async def execute(self, experiences: list[dict[str, Any]], target_role: str) -> list[dict[str, Any]]:
        """
        Calculate relevance weights for experience sections.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ExperienceWeightingEngine.execute")

        self._mcp_audit("experience_weighting")
        weighted_experiences = []
        for exp in experiences:
            weight = self._calculate_relevance(exp, target_role)
            exp["relevance_weight"] = weight
            weighted_experiences.append(exp)
        weighted_experiences.sort(key=lambda x: x["relevance_weight"], reverse=True)
        self.record_pass(f"Weighted {len(weighted_experiences)} experiences")
        return weighted_experiences

    def _calculate_relevance(self, experience: dict[str, Any], target_role: str) -> float:
        """Calculate relevance score."""
        score = 0.5
        title = experience.get("title", "").lower()
        target_lower = target_role.lower()
        if target_lower in title:
            score += 0.5
        related_keywords = ["senior", "lead", "principal", "staff"]
        if any(kw in title for kw in related_keywords):
            score += 0.2
        return min(score, 1.0)
