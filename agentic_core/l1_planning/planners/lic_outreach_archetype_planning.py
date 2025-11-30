# lic_outreach_archetype_planning - Outreach archetype planning
from typing import Dict, Any, Optional

from .lic_outreach_dataclasses import OutreachMission, ArchetypeContext, ArchetypeType, RecipientProfile, ReasoningParams, RagParams, SignalParams

class OutreachArchetypePlanner:
    """Outreach archetype planning engine"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    def plan_archetype(self, mission: OutreachMission, recipient: RecipientProfile) -> ArchetypeContext:
        """Plan outreach archetype based on mission and recipient"""
        # Simple archetype selection logic
        if recipient.title.lower() in ["ceo", "executive", "director"]:
            archetype_type = ArchetypeType.C_LEVEL
        elif recipient.title.lower() in ["friend", "colleague"]:
            archetype_type = ArchetypeType.RECRUITER
        else:
            archetype_type = ArchetypeType.SENIOR_TA

        # Create parameter objects with appropriate values for different archetypes
        if archetype_type == ArchetypeType.C_LEVEL:
            reasoning_params = ReasoningParams(max_reasoning_depth=8, enable_chain_of_thought=True)
            rag_params = RagParams(source_weights={"company": 0.7, "individual": 0.3})
            signal_params = SignalParams(signal_types=["strategic", "financial"])
        else:
            reasoning_params = ReasoningParams(max_reasoning_depth=5, enable_chain_of_thought=True)
            rag_params = RagParams(source_weights={"company": 0.5, "individual": 0.5})
            signal_params = SignalParams(signal_types=["technical"])

        # Create flattened ArchetypeContext with direct parameter access
        return ArchetypeContext(
            archetype=archetype_type.value,  # Use enum value string
            reasoning_mode="balanced",
            metadata={
                "recipient": recipient.name,
                "role": recipient.title,
                "mission": mission.target_role
            },
            reasoning_params=reasoning_params,
            rag_params=rag_params,
            signal_params=signal_params,
            # Keep other parameters as defaults for now
            tone_params={},
            cta_params={},
            constraint_params={},
            temperature_schedule={},
            message_style="professional",
            focus_areas=[],
            tone="balanced",
            priority_weight=1.0
        )

    def build_archetype_context(self, recipient: RecipientProfile, mission: OutreachMission) -> ArchetypeContext:
        """Build archetype context - alias for plan_archetype to match test expectations"""
        return self.plan_archetype(mission, recipient)

    def create_outreach_mission(self, target: str, purpose: str, context: Dict[str, Any] = None) -> OutreachMission:
        """Create an outreach mission"""
        return OutreachMission(
            target=target,
            purpose=purpose,
            context=ArchetypeContext(metadata=context or {})
        )

    def generate_recipient_profile(self, name: str, title: str, company: str = "", context: Dict[str, Any] = None) -> RecipientProfile:
        """Generate a recipient profile"""
        return RecipientProfile(
            name=name,
            title=title,
            company=company,
            research_data=context or {}
        )

# Global planner instance
_global_planner: Optional[OutreachArchetypePlanner] = None

def get_archetype_planner() -> OutreachArchetypePlanner:
    """Get the global archetype planner instance"""
    global _global_planner
    if _global_planner is None:
        _global_planner = OutreachArchetypePlanner()
    return _global_planner

def reset_archetype_planner() -> None:
    """Reset the global archetype planner instance (for testing)"""
    global _global_planner
    _global_planner = None
