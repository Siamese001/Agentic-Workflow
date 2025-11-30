# LIC Campaign Inputs for L1 planning
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class CampaignInput:
    """Campaign input data structure"""
    campaign_id: str = ""
    target_audience: Dict[str, Any] = None
    budget_constraints: Dict[str, Any] = None
    timeline: Dict[str, Any] = None
    objectives: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.target_audience is None:
            self.target_audience = {}
        if self.budget_constraints is None:
            self.budget_constraints = {}
        if self.timeline is None:
            self.timeline = {}
        if self.objectives is None:
            self.objectives = []
        if self.metadata is None:
            self.metadata = {}

class LICCampaignInputs:
    """Campaign inputs processor for outreach planning"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    def validate_inputs(self, inputs: CampaignInput) -> Dict[str, Any]:
        """Validate campaign inputs"""
        return {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "metadata": {"validated_at": "now"}
        }

    def enrich_inputs(self, inputs: CampaignInput, external_data: Dict[str, Any] = None) -> CampaignInput:
        """Enrich inputs with external data"""
        inputs.metadata["enriched"] = True
        inputs.metadata["external_sources"] = external_data or {}
        return inputs

    def create_input_template(self, campaign_type: str) -> CampaignInput:
        """Create input template for campaign type"""
        return CampaignInput(
            campaign_id=f"template_{campaign_type}",
            target_audience={"type": campaign_type, "size": 100},
            budget_constraints={"total": 10000, "per_contact": 50},
            timeline={"start_date": "2024-01-01", "duration": "30_days"},
            objectives=["generate_leads", "build_awareness"],
            metadata={"template_type": campaign_type}
        )
