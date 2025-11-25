"""L1 Draft Planning - Pure reasoning only."""

from dataclasses import dataclass
from typing import Any, List

@dataclass
class DraftPlan:
    """Pure draft planning data structure."""
    sections: List[str]
    tone: str
    focus_areas: List[str]
    reasoning: str

def plan_drafting(strategy_result: Any, job: Any, resume: Any) -> DraftPlan:
    """Pure draft planning function - no execution, no I/O."""
    return DraftPlan(
        sections=["summary", "experience", "skills"],
        tone="professional",
        focus_areas=["technical_skills", "leadership"],
        reasoning="Align resume with job requirements"
    )
