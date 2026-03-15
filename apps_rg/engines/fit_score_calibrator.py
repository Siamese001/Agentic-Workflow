"""
Fit Score Calibrator - Alignment scoring
Refactored from calibrate_fit_score.py
"""

from __future__ import annotations

import logging
from typing import Any

from apps_rg.engines.base_rg_engine import BaseRGEngine
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

Logger = logging.getLogger(__name__)


class FitScoreCalibrator(BaseRGEngine):
    """
    Calibrates candidate-to-JD fit scores.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="REFINE.FIT_SCORE")

    async def execute(self, candidate_data: dict[str, Any], jd_requirements: dict[str, Any]) -> float:
        """
        Calculate calibrated fit score.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "FitScoreCalibrator.execute")

        self._mcp_audit("fit_score_calculation")
        score = 0.0
        max_score = 0.0
        candidate_skills = set(candidate_data.get("skills", []))
        required_skills = set(jd_requirements.get("required_skills", []))
        if required_skills:
            skill_match = len(candidate_skills & required_skills) / len(required_skills)
            score += skill_match * 0.4
            max_score += 0.4
        candidate_years = candidate_data.get("years_experience", 0)
        required_years = jd_requirements.get("min_years", 0)
        if required_years > 0:
            exp_match = min(candidate_years / required_years, 1.0)
            score += exp_match * 0.3
            max_score += 0.3
        if candidate_data.get("industry") == jd_requirements.get("industry"):
            score += 0.3
            max_score += 0.3
        final_score = score / max_score if max_score > 0 else 0.0
        self.record_pass(f"Fit score calculated: {final_score:.2f}")
        return final_score
