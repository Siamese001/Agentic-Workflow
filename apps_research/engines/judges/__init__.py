"""apps_research.engines.judges — LLM-as-judge and calibrated heuristic graders."""

from apps_research.engines.judges.citation_quality_judge import (
    CitationQualityJudge,
    grade,
    IS_STUB,
    IS_CALIBRATED,
    GRADER_ID,
)
from apps_research.engines.judges.coverage_depth_judge import (
    CoverageDepthJudge,
)

__all__ = [
    "CitationQualityJudge",
    "CoverageDepthJudge",
    "grade",
    "IS_STUB",
    "IS_CALIBRATED",
    "GRADER_ID",
]
