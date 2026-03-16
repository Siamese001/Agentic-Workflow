"""
Skill Score Normalizer - Score normalization
Refactored from normalize_skill_scores.py
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

_emit_applies_guardrail("p0", "skill_score_normalizer", "p0_governance")
_emit_reads_policy_state("p0", "skill_score_normalizer", "policy_binding")
_emit_snapshots_state("p0", "skill_score_normalizer", "state_snapshot")
emit_replay_key("p0", "skill_score_normalizer")
emit_determinism_digest("p0", "skill_score_normalizer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)


class SkillScoreNormalizer(BaseRGEngine):
    """
    Normalizes skill match scores across different scales.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="REFINE.SKILL_NORMALIZER")

    async def execute(self, raw_scores: dict[str, float]) -> dict[str, float]:
        """
        Normalize skill scores to 0-1 range.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SkillScoreNormalizer.execute")

        self._mcp_audit("score_normalization")
        if not raw_scores:
            return {}
        values = list(raw_scores.values())
        min_val = min(values)
        max_val = max(values)
        normalized = {}
        if max_val > min_val:
            for skill, score in raw_scores.items():
                normalized[skill] = (score - min_val) / (max_val - min_val)
        else:
            normalized = dict.fromkeys(raw_scores, 1.0)
        self.record_pass(f"Normalized {len(normalized)} skill scores")
        return normalized
