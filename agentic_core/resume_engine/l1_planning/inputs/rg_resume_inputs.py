# RG Resume Inputs for L1 planning
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ResumeInput:
    """Resume input data structure"""
    resume_id: str = ""
    target_role: str = ""
    experience_data: Dict[str, Any] = None
    skills_data: Dict[str, Any] = None
    preferences: Dict[str, Any] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.experience_data is None:
            self.experience_data = {}
        if self.skills_data is None:
            self.skills_data = {}
        if self.preferences is None:
            self.preferences = {}
        if self.metadata is None:
            self.metadata = {}

class RGResumeInputs:
    """Resume inputs processor for planning"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    def validate_inputs(self, inputs: ResumeInput) -> Dict[str, Any]:
        """Validate resume inputs"""
        return {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "metadata": {"validated_at": "now"}
        }

    def enrich_inputs(self, inputs: ResumeInput, market_data: Dict[str, Any] = None) -> ResumeInput:
        """Enrich inputs with market data"""
        inputs.metadata["enriched"] = True
        inputs.metadata["market_data"] = market_data or {}
        return inputs

    def create_input_template(self, role_category: str) -> ResumeInput:
        """Create input template for role category"""
        return ResumeInput(
            resume_id=f"template_{role_category}",
            target_role=f"{role_category}_professional",
            experience_data={"years": 5, "level": "mid"},
            skills_data={"technical": [], "soft": []},
            preferences={"format": "modern", "length": "one_page"},
            metadata={"template_category": role_category}
        )
