"""
Outreach Builder Service
LEVEL 5 - Service for constructing and organizing outreach messages
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import logging

@dataclass
class OutreachSection:
    """Represents a section of an outreach message"""
    section_type: str
    content: str
    priority: int
    word_count: int = 0
    personalization_level: float = 0.0

    def __post_init__(self):
        if self.word_count == 0:
            self.word_count = len(self.content.split())

class OutreachBuilder:
    """Service for building structured outreach messages"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Outreach section templates and configurations
        self.section_templates = {
            "opener": {
                "priority": 1,
                "max_length": 150,
                "personalization_required": True
            },
            "context": {
                "priority": 2,
                "max_length": 300,
                "personalization_required": True
            },
            "value_proposition": {
                "priority": 3,
                "max_length": 400,
                "personalization_required": True
            },
            "call_to_action": {
                "priority": 4,
                "max_length": 200,
                "personalization_required": False
            },
            "closing": {
                "priority": 5,
                "max_length": 100,
                "personalization_required": False
            }
        }

        # Outreach type configurations
        self.outreach_configs = {
            "email": {
                "max_total_length": 2000,
                "required_sections": ["opener", "context", "value_proposition", "call_to_action", "closing"],
                "optional_sections": [],
                "tone": "professional"
            },
            "linkedin": {
                "max_total_length": 1000,
                "required_sections": ["opener", "context", "call_to_action"],
                "optional_sections": ["value_proposition"],
                "tone": "professional"
            },
            "cold_call": {
                "max_total_length": 500,
                "required_sections": ["opener", "context", "call_to_action"],
                "optional_sections": [],
                "tone": "direct"
            },
            "follow_up": {
                "max_total_length": 800,
                "required_sections": ["opener", "context", "call_to_action"],
                "optional_sections": ["value_proposition"],
                "tone": "friendly"
            },
            "networking": {
                "max_total_length": 600,
                "required_sections": ["opener", "context", "call_to_action"],
                "optional_sections": [],
                "tone": "casual"
            }
        }

    async def build_outreach(
        self,
        recipient_profile: Dict[str, Any],
        sender_profile: Dict[str, Any],
        outreach_type: str,
        context: Dict[str, Any] = None,
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Build complete outreach message
        
        Args:
            recipient_profile: Information about the recipient
            sender_profile: Information about the sender
            outreach_type: Type of outreach message
            context: Additional context for personalization
            preferences: User preferences for tone and style
            
        Returns:
            Complete outreach message with metadata
        """
        try:
            self.logger.info(f"Building {outreach_type} outreach message")

            # Get configuration for outreach type
            config = self.outreach_configs.get(outreach_type, self.outreach_configs["email"])

            # Build individual sections
            sections = await self._build_sections(
                recipient_profile, sender_profile, outreach_type, context, preferences
            )

            # Organize and optimize message
            organized_sections = await self._organize_sections(sections, config)

            # Generate final message
            final_message = await self._assemble_message(organized_sections, config)

            # Add metadata
            metadata = await self._generate_metadata(final_message, sections, config)

            return {
                "content": final_message,
                "sections": organized_sections,
                "metadata": metadata,
                "build_timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error building outreach message: {e}")
            raise e

    async def _build_sections(
        self,
        recipient_profile: Dict[str, Any],
        sender_profile: Dict[str, Any],
        outreach_type: str,
        context: Dict[str, Any] = None,
        preferences: Dict[str, Any] = None
    ) -> Dict[str, OutreachSection]:
        """Build individual message sections"""
        sections = {}

        # Build required sections
        config = self.outreach_configs.get(outreach_type, self.outreach_configs["email"])

        for section_type in config["required_sections"]:
            section = await self._build_section(
                section_type, recipient_profile, sender_profile, outreach_type, context, preferences
            )
            sections[section_type] = section

        # Build optional sections if space allows
        for section_type in config["optional_sections"]:
            section = await self._build_section(
                section_type, recipient_profile, sender_profile, outreach_type, context, preferences
            )
            sections[section_type] = section

        return sections

    async def _build_section(
        self,
        section_type: str,
        recipient_profile: Dict[str, Any],
        sender_profile: Dict[str, Any],
        outreach_type: str,
        context: Dict[str, Any] = None,
        preferences: Dict[str, Any] = None
    ) -> OutreachSection:
        """Build a specific message section"""
        template = self.section_templates[section_type]

        if section_type == "opener":
            content = await self._build_opener(recipient_profile, sender_profile, context)
        elif section_type == "context":
            content = await self._build_context(recipient_profile, sender_profile, outreach_type, context)
        elif section_type == "value_proposition":
            content = await self._build_value_proposition(recipient_profile, sender_profile, context)
        elif section_type == "call_to_action":
            content = await self._build_call_to_action(recipient_profile, sender_profile, outreach_type, context)
        elif section_type == "closing":
            content = await self._build_closing(sender_profile, preferences)
        else:
            content = "Default content"

        # Calculate personalization level
        personalization_level = await self._calculate_personalization_level(
            content, recipient_profile, sender_profile
        )

        return OutreachSection(
            section_type=section_type,
            content=content,
            priority=template["priority"],
            personalization_level=personalization_level
        )

    async def _build_opener(
        self,
        recipient_profile: Dict[str, Any],
        sender_profile: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> str:
        """Build message opener section"""
        recipient_name = recipient_profile.get("name", "there")
        relationship = context.get("relationship", "stranger") if context else "stranger"

        if relationship == "stranger":
            opener = f"Hi {recipient_name},"
        elif relationship == "acquaintance":
            opener = f"Hi {recipient_name},"
        elif relationship in ["colleague", "former_colleague"]:
            opener = f"Hi {recipient_name},"
        elif relationship in ["friend", "mentor", "mentee"]:
            opener = f"Hi {recipient_name},"
        else:
            opener = f"Hi {recipient_name},"

        return opener

    async def _build_context(
        self,
        recipient_profile: Dict[str, Any],
        sender_profile: Dict[str, Any],
        outreach_type: str,
        context: Dict[str, Any] = None
    ) -> str:
        """Build context section"""
        context_parts = []

        # Add connection context
        if context and context.get("mutual_connections"):
            connections = context["mutual_connections"][:2]  # Limit to 2 connections
            if len(connections) == 1:
                context_parts.append(f"I noticed we're both connected with {connections[0]}")
            else:
                context_parts.append(f"I noticed we're both connected with {connections[0]} and {connections[1]}")

        # Add recipient background context
        recipient_company = recipient_profile.get("company", "")
        recipient_role = recipient_profile.get("role", "")

        if recipient_company and recipient_role:
            context_parts.append(f"I came across your profile as {recipient_role} at {recipient_company}")
        elif recipient_role:
            context_parts.append(f"I came across your profile as a {recipient_role}")

        # Add shared interests
        if context and context.get("shared_interests"):
            interests = context["shared_interests"][:2]
            if len(interests) == 1:
                context_parts.append(f"I see we share an interest in {interests[0]}")
            else:
                context_parts.append(f"I see we share interests in {interests[0]} and {interests[1]}")

        # Add sender context
        sender_company = sender_profile.get("company", "")
        sender_role = sender_profile.get("role", "")

        if sender_company and sender_role:
            context_parts.append(f"As a {sender_role} at {sender_company}")

        return " ".join(context_parts) + "."

    async def _build_value_proposition(
        self,
        recipient_profile: Dict[str, Any],
        sender_profile: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> str:
        """Build value proposition section"""
        value_parts = []

        # Sender expertise
        sender_expertise = sender_profile.get("expertise", [])
        if sender_expertise:
            expertise_text = ", ".join(sender_expertise[:3])
            value_parts.append(f"With my background in {expertise_text}")

        # Potential collaboration areas
        recipient_industry = recipient_profile.get("industry", "")
        if recipient_industry:
            value_parts.append(f"I believe there could be valuable synergy in the {recipient_industry} space")

        # Specific value offer
        if context and context.get("purpose"):
            purpose = context["purpose"]
            value_parts.append(f"I'd love to discuss {purpose}")

        return " ".join(value_parts) + "."

    async def _build_call_to_action(
        self,
        recipient_profile: Dict[str, Any],
        sender_profile: Dict[str, Any],
        outreach_type: str,
        context: Dict[str, Any] = None
    ) -> str:
        """Build call to action section"""
        if outreach_type == "email":
            return "Would you be open to a brief call next week to explore potential opportunities?"
        elif outreach_type == "linkedin":
            return "I'd welcome the opportunity to connect and discuss this further."
        elif outreach_type == "cold_call":
            return "Do you have 15 minutes this week for a quick conversation?"
        elif outreach_type == "follow_up":
            return "Would you be available to continue our discussion?"
        elif outreach_type == "networking":
            return "I'd love to connect and learn more about your work."
        else:
            return "I'd appreciate the opportunity to discuss this further."

    async def _build_closing(
        self,
        sender_profile: Dict[str, Any],
        preferences: Dict[str, Any] = None
    ) -> str:
        """Build closing section"""
        sender_name = sender_profile.get("name", "there")
        tone = preferences.get("tone", "professional") if preferences else "professional"

        if tone == "formal":
            return f"Best regards,\n{sender_name}"
        elif tone == "casual":
            return f"Thanks,\n{sender_name}"
        else:
            return f"Best,\n{sender_name}"

    async def _calculate_personalization_level(
        self,
        content: str,
        recipient_profile: Dict[str, Any],
        sender_profile: Dict[str, Any]
    ) -> float:
        """Calculate personalization level for content"""
        personalization_indicators = 0
        total_indicators = 0

        # Check for recipient name
        if recipient_profile.get("name", "").lower() in content.lower():
            personalization_indicators += 1
        total_indicators += 1

        # Check for recipient company
        if recipient_profile.get("company", "").lower() in content.lower():
            personalization_indicators += 1
        total_indicators += 1

        # Check for recipient role
        if recipient_profile.get("role", "").lower() in content.lower():
            personalization_indicators += 1
        total_indicators += 1

        # Check for mutual connections
        if "connected with" in content.lower():
            personalization_indicators += 1
        total_indicators += 1

        # Check for shared interests
        if "share an interest" in content.lower() or "share interests" in content.lower():
            personalization_indicators += 1
        total_indicators += 1

        return personalization_indicators / total_indicators if total_indicators > 0 else 0.0

    async def _organize_sections(
        self,
        sections: Dict[str, OutreachSection],
        config: Dict[str, Any]
    ) -> List[OutreachSection]:
        """Organize sections by priority and optimize for length"""
        # Sort sections by priority
        sorted_sections = sorted(sections.values(), key=lambda x: x.priority)

        # Optimize for length constraints
        total_length = sum(len(section.content) for section in sorted_sections)
        max_length = config["max_total_length"]

        if total_length > max_length:
            # Truncate longer sections
            excess_length = total_length - max_length
            for section in sorted_sections:
                if excess_length <= 0:
                    break

                if len(section.content) > 100:  # Only truncate sections with sufficient content
                    truncate_amount = min(excess_length, len(section.content) - 50)
                    section.content = section.content[:-truncate_amount] + "..."
                    excess_length -= truncate_amount

        return sorted_sections

    async def _assemble_message(
        self,
        sections: List[OutreachSection],
        config: Dict[str, Any]
    ) -> Dict[str, str]:
        """Assemble final message from sections"""
        message_parts = []

        for section in sections:
            if section.content.strip():
                message_parts.append(section.content.strip())

        full_body = "\n\n".join(message_parts)

        # Extract subject and call to action
        subject = await self._extract_subject(full_body)
        call_to_action = await self._extract_call_to_action(sections)

        return {
            "subject": subject,
            "body": full_body,
            "call_to_action": call_to_action
        }

    async def _extract_subject(self, body: str) -> str:
        """Extract subject line from message body"""
        # Generate subject based on content
        if "collaboration" in body.lower():
            return "Collaboration Opportunity"
        elif "connect" in body.lower():
            return "Connection Request"
        elif "discuss" in body.lower():
            return "Discussion Request"
        elif "opportunity" in body.lower():
            return "Professional Opportunity"
        else:
            return "Professional Connection"

    async def _extract_call_to_action(self, sections: List[OutreachSection]) -> str:
        """Extract call to action from sections"""
        for section in sections:
            if section.section_type == "call_to_action":
                return section.content

        return "I'd appreciate the opportunity to connect."

    async def _generate_metadata(
        self,
        message: Dict[str, str],
        sections: List[OutreachSection],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate metadata for the outreach message"""
        total_words = sum(section.word_count for section in sections)
        total_chars = sum(len(section.content) for section in sections)

        # Calculate average personalization
        personalization_scores = [section.personalization_level for section in sections]
        avg_personalization = sum(personalization_scores) / len(personalization_scores) if personalization_scores else 0.0

        return {
            "word_count": total_words,
            "character_count": total_chars,
            "section_count": len(sections),
            "personalization_score": avg_personalization,
            "tone": config.get("tone", "professional"),
            "message_type": config.get("message_type", "outreach"),
            "section_types": [section.section_type for section in sections]
        }

__all__ = ["OutreachBuilder", "OutreachSection"]
