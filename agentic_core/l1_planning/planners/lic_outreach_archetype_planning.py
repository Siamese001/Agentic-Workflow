# lic_outreach_archetype_planning - Outreach archetype planning
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from .lic_outreach_dataclasses import OutreachMission, ArchetypeContext, ArchetypeType

@dataclass
class RecipientProfile:
    """Recipient profile data structure"""
    name: str = ""
    role: str = ""
    organization: str = ""
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}

class OutreachArchetypePlanner:
    """Outreach archetype planning engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
    
    def plan_archetype(self, mission: OutreachMission, recipient: RecipientProfile) -> ArchetypeContext:
        """Plan outreach archetype based on mission and recipient"""
        # Simple archetype selection logic
        if recipient.role.lower() in ["ceo", "executive", "director"]:
            archetype = ARCHETYPE_REGISTRY.get("formal", ArchetypeType("formal", "Formal communication"))
        elif recipient.role.lower() in ["friend", "colleague"]:
            archetype = ARCHETYPE_REGISTRY.get("casual", ArchetypeType("casual", "Casual communication"))
        else:
            archetype = ARCHETYPE_REGISTRY.get("professional", ArchetypeType("professional", "Professional communication"))
        
        return ArchetypeContext(
            archetype=archetype,
            metadata={
                "recipient": recipient.name,
                "role": recipient.role,
                "mission": mission.target
            }
        )
    
    def create_outreach_mission(self, target: str, purpose: str, context: Dict[str, Any] = None) -> OutreachMission:
        """Create an outreach mission"""
        return OutreachMission(
            target=target,
            purpose=purpose,
            context=ArchetypeContext(metadata=context or {})
        )
    
    def generate_recipient_profile(self, name: str, role: str, organization: str = "", context: Dict[str, Any] = None) -> RecipientProfile:
        """Generate a recipient profile"""
        return RecipientProfile(
            name=name,
            role=role,
            organization=organization,
            context=context or {}
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
