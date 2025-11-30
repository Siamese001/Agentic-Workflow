# RG Resume Strategy for L1 planning
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class ResumeStrategy:
    """Resume strategy definition"""
    strategy_id: str = ""
    target_role: str = ""
    optimization_focus: List[str] = None
    formatting_style: str = ""
    content_priorities: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.optimization_focus is None:
            self.optimization_focus = []
        if self.content_priorities is None:
            self.content_priorities = []
        if self.metadata is None:
            self.metadata = {}

class RGResumeStrategy:
    """Resume strategy planner"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    def create_strategy(self, target_role: str, experience_level: str) -> ResumeStrategy:
        """Create resume strategy based on target role"""
        return ResumeStrategy(
            strategy_id=f"strategy_{target_role}_{experience_level}",
            target_role=target_role,
            optimization_focus=["ats_compatibility", "keyword_optimization"],
            formatting_style="professional_clean",
            content_priorities=["technical_skills", "achievements", "impact"],
            metadata={"experience_level": experience_level}
        )

    def optimize_strategy(self, strategy: ResumeStrategy, feedback_data: Dict[str, Any]) -> ResumeStrategy:
        """Optimize strategy based on feedback"""
        strategy.optimization_focus.append("industry_specific_keywords")
        strategy.metadata["optimized"] = True
        return strategy

    def get_section_recommendations(self, target_role: str) -> List[str]:
        """Get section recommendations for target role"""
        return [
            "Professional Summary",
            "Technical Skills",
            "Work Experience",
            "Education",
            "Certifications"
        ]
