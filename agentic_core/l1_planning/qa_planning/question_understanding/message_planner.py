"""
Message Planner Module
LEVEL 5 - Message planning and content strategy for agentic communications
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class MessagePlan:
    """Represents a message plan with content and delivery strategy"""
    plan_id: str
    message_type: str
    content_strategy: Dict[str, Any]
    delivery_timing: Dict[str, Any]
    personalization_points: List[str]

class MessagePlanner:
    """Handles message planning and content strategy"""

    def __init__(self):
        self.message_types = [
            "professional_outreach",
            "follow_up_communication",
            "information_request",
            "status_update"
        ]

    async def create_message_plan(
        self,
        recipient_profile: Dict[str, Any],
        message_objective: str,
        context: Dict[str, Any]
    ) -> MessagePlan:
        """Create a message plan with content and delivery strategy"""
        try:
            plan_id = f"message_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

            # Determine message type based on objective
            message_type = self._determine_message_type(message_objective)

            # Create content strategy
            content_strategy = self._create_content_strategy(
                recipient_profile, message_objective
            )

            # Plan delivery timing
            delivery_timing = self._plan_delivery_timing(recipient_profile)

            # Identify personalization points
            personalization_points = self._identify_personalization_points(
                recipient_profile
            )

            return MessagePlan(
                plan_id=plan_id,
                message_type=message_type,
                content_strategy=content_strategy,
                delivery_timing=delivery_timing,
                personalization_points=personalization_points
            )

        except Exception as e:
            raise Exception(f"Message planning failed: {str(e)}")

    def _determine_message_type(self, objective: str) -> str:
        """Determine message type based on objective"""
        objective_lower = objective.lower()
        if "outreach" in objective_lower or "contact" in objective_lower:
            return "professional_outreach"
        elif "follow" in objective_lower or "update" in objective_lower:
            return "follow_up_communication"
        elif "information" in objective_lower or "request" in objective_lower:
            return "information_request"
        else:
            return "status_update"

    def _create_content_strategy(
        self, recipient_profile: Dict[str, Any], objective: str
    ) -> Dict[str, Any]:
        """Create content strategy for the message"""
        return {
            "tone": "professional",
            "length": "medium",
            "key_points": [
                f"Address {recipient_profile.get('name', 'recipient')}",
                f"Objective: {objective}",
                "Call to action included"
            ],
            "personalization_level": "high"
        }

    def _plan_delivery_timing(
        self, recipient_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Plan optimal delivery timing"""
        return {
            "preferred_time": "business_hours",
            "timezone": recipient_profile.get("timezone", "UTC"),
            "urgency": "normal",
            "follow_up_days": 3
        }

    def _identify_personalization_points(
        self, recipient_profile: Dict[str, Any]
    ) -> List[str]:
        """Identify points for message personalization"""
        points = []
        if recipient_profile.get("name"):
            points.append("name_inclusion")
        if recipient_profile.get("company"):
            points.append("company_reference")
        if recipient_profile.get("skills"):
            points.append("skill_alignment")
        if recipient_profile.get("experience"):
            points.append("experience_matching")

        return points

__all__ = ["MessagePlanner", "MessagePlan"]
