"""L1 QA Planning - Pure reasoning only."""

from dataclasses import dataclass
from typing import Any, List

@dataclass
class QAPlan:
    """Pure QA planning data structure."""
    focus_areas: List[str]
    quality_criteria: List[str]
    reasoning: str

def plan_qa(draft: Any, job: Any, resume: Any) -> QAPlan:
    """Pure QA planning function - no execution, no I/O."""
    return QAPlan(
        focus_areas=["accuracy", "relevance", "completeness"],
        quality_criteria=["job_alignment", "skill_match", "experience_clarity"],
        reasoning="Ensure draft meets job requirements and quality standards"
    )
