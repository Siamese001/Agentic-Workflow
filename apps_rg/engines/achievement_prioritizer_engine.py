"""
Achievement Prioritizer Engine - Impact sorting
Refactored from prioritize_achievements.py
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

_emit_applies_guardrail("p0", "achievement_prioritizer_engine", "p0_governance")
_emit_reads_policy_state("p0", "achievement_prioritizer_engine", "policy_binding")
_emit_snapshots_state("p0", "achievement_prioritizer_engine", "state_snapshot")
emit_replay_key("p0", "achievement_prioritizer_engine")
emit_determinism_digest("p0", "achievement_prioritizer_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)


class AchievementPrioritizerEngine(BaseRGEngine):
    """
    Prioritizes achievements by impact and relevance.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="REFINE.ACHIEVEMENT_PRIORITIZER")

    async def execute(self, achievements: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Sort achievements by impact score.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "AchievementPrioritizerEngine.execute")

        self._mcp_audit("achievement_prioritization")
        scored = []
        for achievement in achievements:
            score = self._calculate_impact(achievement)
            scored.append((achievement, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        prioritized = [item for item, _ in scored]
        self.record_pass(f"Prioritized {len(prioritized)} achievements")
        return prioritized

    def _calculate_impact(self, achievement: dict[str, Any]) -> float:
        """Calculate impact score for achievement."""
        score = 0.0
        if achievement.get("quantified_metrics"):
            score += 0.5
        text = achievement.get("bullet_text", "").lower()
        if any(word in text for word in ["led", "managed", "directed"]):
            score += 0.3
        if any(word in text for word in ["team", "organization", "department"]):
            score += 0.2
        return score
