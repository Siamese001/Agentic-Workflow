# RG Resume Planner for L1 planning
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class ResumePlan:
    """Resume plan structure"""
    plan_id: str = ""
    target_role: str = ""
    sections: List[str] = None
    content_strategy: Dict[str, Any] = None
    timeline: Dict[str, Any] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.sections is None:
            self.sections = []
        if self.content_strategy is None:
            self.content_strategy = {}
        if self.timeline is None:
            self.timeline = {}
        if self.metadata is None:
            self.metadata = {}

class RGResumePlanner:
    """Resume planner engine"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    def create_resume_plan(self, target_role: str, experience_data: Dict[str, Any]) -> ResumePlan:
        """Create comprehensive resume plan"""
        return ResumePlan(
            plan_id=f"plan_{target_role}_{len(experience_data)}",
            target_role=target_role,
            sections=["summary", "experience", "skills", "education"],
            content_strategy={
                "focus": "achievements",
                "tone": "professional",
                "keywords": self._extract_keywords(target_role)
            },
            timeline={"research": "2_days", "drafting": "3_days", "review": "2_days"},
            metadata={"experience_level": experience_data.get("level", "unknown")}
        )

    def _extract_keywords(self, target_role: str) -> List[str]:
        """Extract relevant keywords for target role"""
        keyword_map = {
            "software_engineer": ["python", "javascript", "react", "node.js"],
            "data_scientist": ["python", "machine learning", "statistics", "sql"],
            "product_manager": ["strategy", "analytics", "leadership", "agile"]
        }
        return keyword_map.get(target_role.lower(), ["professional", "skilled", "experienced"])

    def update_plan(self, plan: ResumePlan, updates: Dict[str, Any]) -> ResumePlan:
        """Update existing plan"""
        if "sections" in updates:
            plan.sections.extend(updates["sections"])
        if "content_strategy" in updates:
            plan.content_strategy.update(updates["content_strategy"])
        plan.metadata["updated"] = True
        return plan

    def estimate_completion_time(self, plan: ResumePlan) -> Dict[str, Any]:
        """Estimate plan completion time"""
        base_time = len(plan.sections) * 2  # 2 days per section
        return {
            "estimated_days": base_time,
            "complexity": "medium" if base_time <= 10 else "high",
            "confidence": 0.8
        }
