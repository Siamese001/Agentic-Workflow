"""
Ranking Refiner Engine - Adjusts rankings based on JD
Refactored from RefineResumeRanking.py
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

_emit_applies_guardrail("p0", "ranking_refiner_engine", "p0_governance")
_emit_reads_policy_state("p0", "ranking_refiner_engine", "policy_binding")
_emit_snapshots_state("p0", "ranking_refiner_engine", "state_snapshot")
emit_replay_key("p0", "ranking_refiner_engine")
emit_determinism_digest("p0", "ranking_refiner_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)


class RankingRefinerEngine(BaseRGEngine):
    """
    Refines section rankings based on JD analysis.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="REFINE.RANKING_REFINER")

    async def execute(self, initial_ranking: list[str], jd_analysis: dict[str, Any]) -> list[str]:
        """
        Refine section ranking based on JD priorities.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RankingRefinerEngine.execute")

        self._mcp_audit("ranking_refinement")
        refined_ranking = initial_ranking.copy()
        if jd_analysis.get("technical_heavy"):
            if "skills" in refined_ranking:
                refined_ranking.remove("skills")
                refined_ranking.insert(0, "skills")
        if jd_analysis.get("leadership_heavy"):
            if "summary" in refined_ranking:
                refined_ranking.remove("summary")
                refined_ranking.insert(0, "summary")
        self.record_pass("Ranking refined based on JD analysis")
        return refined_ranking
