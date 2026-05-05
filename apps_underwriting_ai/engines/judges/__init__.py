"""apps_underwriting_ai judges package.

Contains the rationale quality judge for underwriting AI decisions.
IS_STUB = False since plan apps-underwriting-ai-d3-rationale-judge-f2c8d5 W2.
"""

from apps_underwriting_ai.engines.judges.rationale_quality_judge import (
    IS_STUB as rationale_quality_judge_is_stub,
    RationaleQualityJudge,
)

__all__ = [
    "RationaleQualityJudge",
    "rationale_quality_judge_is_stub",
]
