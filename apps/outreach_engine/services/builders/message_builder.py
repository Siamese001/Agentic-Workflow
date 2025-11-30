"""
Message Builder Service
LEVEL 5 - Service for building and optimizing outreach message content
"""

from typing import Dict, Any
from dataclasses import dataclass
from datetime import datetime
import logging
import re

@dataclass
class MessageComponent:
    """Represents a component of an outreach message"""
    component_type: str
    content: str
    metadata: Dict[str, Any]
    optimization_score: float = 0.0

    def __post_init__(self):
        if self.optimization_score == 0.0:
            self.optimization_score = self._calculate_base_score()

class MessageBuilder:
    """Service for building and optimizing outreach message components"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Message component configurations
        self.component_configs = {
            "subject_line": {
                "max_length": 100,
                "min_length": 10,
                "optimization_factors": ["engagement", "personalization", "clarity"],
                "weight": 0.2
            },
            "opening": {
                "max_length": 150,
                "min_length": 20,
                "optimization_factors": ["personalization", "tone", "engagement"],
                "weight": 0.25
            },
            "body": {
                "max_length": 800,
                "min_length": 100,
                "optimization_factors": ["relevance", "clarity", "value_proposition"],
                "weight": 0.35
            },
            "call_to_action": {
                "max_length": 200,
                "min_length": 30,
                "optimization_factors": ["actionability", "clarity", "urgency"],
                "weight": 0.15
            },
            "closing": {
                "max_length": 100,
                "min_length": 10,
                "optimization_factors": ["professionalism", "tone"],
                "weight": 0.05
            }
        }

        # Optimization patterns and rules
        self.engagement_patterns = {
            "questions": [r"\?", r"Would you", r"Are you", r"Can we"],
            "personalization": [r"\b(you|your)\b", r"\b(recipient|company)\b"],
            "value_words": ["benefit", "advantage", "improve", "enhance", "save", "increase"],
            "action_words": ["schedule", "call", "meet", "discuss", "connect", "reply"]
        }

        # Tone indicators
        self.tone_indicators = {
            "formal": ["regards", "sincerely", "respectfully", "formal"],
            "professional": ["best", "thanks", "appreciate", "opportunity"],
            "casual": ["hi", "hey", "cool", "awesome"],
            "friendly": ["great", "wonderful", "pleasure", "looking forward"]
        }

    async def build_message_components(
        self,
        recipient_profile: Dict[str, Any],
        sender_profile: Dict[str, Any],
        outreach_type: str,
        context: Dict[str, Any] = None,
        preferences: Dict[str, Any] = None
    ) -> Dict[str, MessageComponent]:
        """
        Build all message components
        
        Args:
            recipient_profile: Information about the recipient
            sender_profile: Information about the sender
            outreach_type: Type of outreach message
            context: Additional context for personalization
            preferences: User preferences for tone and style
            
        Returns:
            Dictionary of message components
        """
        try:
            self.logger.info(f"Building message components for {outreach_type}")

            components = {}

            # Build each component
            for component_type in self.component_configs.keys():
                component = await self._build_component(
                    component_type, recipient_profile, sender_profile, outreach_type, context, preferences
                )
                components[component_type] = component

            # Optimize components together
            optimized_components = await self._optimize_components(components, preferences)

            return optimized_components

        except Exception as e:
            self.logger.error(f"Error building message components: {e}")
            raise e

    async def _build_component(
        self,
        component_type: str,
        recipient_profile: Dict[str, Any],
        sender_profile: Dict[str, Any],
        outreach_type: str,
        context: Dict[str, Any] = None,
        preferences: Dict[str, Any] = None
    ) -> MessageComponent:
        """Build a specific message component"""

        if component_type == "subject_line":
            content = await self._build_subject_line(recipient_profile, sender_profile, outreach_type, context)
        elif component_type == "opening":
            content = await self._build_opening(recipient_profile, sender_profile, context)
        elif component_type == "body":
            content = await self._build_body(recipient_profile, sender_profile, outreach_type, context)
        elif component_type == "call_to_action":
            content = await self._build_call_to_action(recipient_profile, sender_profile, outreach_type, context)
        elif component_type == "closing":
            content = await self._build_closing(sender_profile, preferences)
        else:
            content = "Default content"

        # Generate metadata
        metadata = await self._generate_component_metadata(component_type, content, recipient_profile, sender_profile)

        return MessageComponent(
            component_type=component_type,
            content=content,
            metadata=metadata
        )

    async def _build_subject_line(
        self,
        recipient_profile: Dict[str, Any],
        sender_profile: Dict[str, Any],
        outreach_type: str,
        context: Dict[str, Any] = None
    ) -> str:
        """Build subject line component"""
        subject_parts = []

        # Add personalization
        recipient_name = recipient_profile.get("name", "")
        if recipient_name and outreach_type in ["follow_up", "networking"]:
            subject_parts.append(f"Following up with {recipient_name}")

        # Add purpose/topic
        if context and context.get("purpose"):
            purpose = context["purpose"]
            if "collaboration" in purpose.lower():
                subject_parts.append("Collaboration Opportunity")
            elif "partnership" in purpose.lower():
                subject_parts.append("Partnership Discussion")
            elif "opportunity" in purpose.lower():
                subject_parts.append("Professional Opportunity")
            else:
                subject_parts.append("Professional Connection")
        else:
            subject_parts.append("Professional Connection")

        # Add engagement element
        if outreach_type == "email":
            subject_parts.append("Discussion")
        elif outreach_type == "linkedin":
            subject_parts.append("Connection")

        # Combine and optimize
        subject = " | ".join(subject_parts)

        # Ensure length constraints
        config = self.component_configs["subject_line"]
        if len(subject) > config["max_length"]:
            subject = subject[:config["max_length"] - 3] + "..."
        elif len(subject) < config["min_length"]:
            subject += " | Discussion"

        return subject

    async def _build_opening(
        self,
        recipient_profile: Dict[str, Any],
        sender_profile: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> str:
        """Build opening component"""
        opening_parts = []

        # Greeting
        recipient_name = recipient_profile.get("name", "there")
        relationship = context.get("relationship", "stranger") if context else "stranger"

        if relationship == "stranger":
            greeting = f"Hi {recipient_name},"
        elif relationship in ["colleague", "former_colleague"]:
            greeting = f"Hi {recipient_name},"
        elif relationship in ["friend", "mentor", "mentee"]:
            greeting = f"Hi {recipient_name},"
        else:
            greeting = f"Hi {recipient_name},"

        opening_parts.append(greeting)

        # Context statement
        if context and context.get("mutual_connections"):
            connections = context["mutual_connections"][:2]
            if len(connections) == 1:
                opening_parts.append(f"I noticed we're both connected with {connections[0]}")
            else:
                opening_parts.append(f"I noticed we're both connected with {connections[0]} and {connections[1]}")
        else:
            recipient_company = recipient_profile.get("company", "")
            recipient_role = recipient_profile.get("role", "")

            if recipient_company and recipient_role:
                opening_parts.append(f"I came across your profile as {recipient_role} at {recipient_company}")
            elif recipient_role:
                opening_parts.append(f"I came across your profile as a {recipient_role}")

        return " ".join(opening_parts)

    async def _build_body(
        self,
        recipient_profile: Dict[str, Any],
        sender_profile: Dict[str, Any],
        outreach_type: str,
        context: Dict[str, Any] = None
    ) -> str:
        """Build body component"""
        body_parts = []

        # Sender background and expertise
        sender_role = sender_profile.get("role", "")
        sender_company = sender_profile.get("company", "")
        sender_expertise = sender_profile.get("expertise", [])

        if sender_role and sender_company:
            body_parts.append(f"As a {sender_role} at {sender_company}")

        if sender_expertise:
            expertise_text = ", ".join(sender_expertise[:3])
            body_parts.append(f"with expertise in {expertise_text}")

        # Connection to recipient
        recipient_industry = recipient_profile.get("industry", "")
        if recipient_industry:
            body_parts.append(f"I've been following the innovative work in the {recipient_industry} space")

        # Value proposition
        if context and context.get("purpose"):
            purpose = context["purpose"]
            body_parts.append(f"I believe there could be valuable opportunities to {purpose}")

        # Specific interest in recipient
        recipient_achievements = recipient_profile.get("background", {}).get("achievements", [])
        if recipient_achievements:
            body_parts.append("I was particularly impressed by your achievements")

        # Combine into coherent paragraph
        body = ". ".join(body_parts) + "."

        return body

    async def _build_call_to_action(
        self,
        recipient_profile: Dict[str, Any],
        sender_profile: Dict[str, Any],
        outreach_type: str,
        context: Dict[str, Any] = None
    ) -> str:
        """Build call to action component"""
        urgency = context.get("urgency", "medium") if context else "medium"

        if outreach_type == "email":
            if urgency == "high":
                return "Would you be available for a brief call this week to discuss this opportunity?"
            elif urgency == "urgent":
                return "I'd appreciate the opportunity to speak with you as soon as possible. Are you available for a quick call today or tomorrow?"
            else:
                return "Would you be open to a brief call next week to explore potential opportunities?"

        elif outreach_type == "linkedin":
            return "I'd welcome the opportunity to connect and discuss this further."

        elif outreach_type == "cold_call":
            return "Do you have 15 minutes this week for a quick conversation about this?"

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
        """Build closing component"""
        sender_name = sender_profile.get("name", "there")
        tone = preferences.get("tone", "professional") if preferences else "professional"

        if tone == "formal":
            return f"Best regards,\n{sender_name}"
        elif tone == "casual":
            return f"Thanks,\n{sender_name}"
        elif tone == "friendly":
            return f"Looking forward to connecting,\n{sender_name}"
        else:
            return f"Best,\n{sender_name}"

    async def _optimize_components(
        self,
        components: Dict[str, MessageComponent],
        preferences: Dict[str, Any] = None
    ) -> Dict[str, MessageComponent]:
        """Optimize all components for consistency and effectiveness"""

        # Calculate optimization scores
        for component_type, component in components.items():
            component.optimization_score = await self._calculate_optimization_score(component, preferences)

        # Optimize for length and consistency
        optimized_components = await self._optimize_length_and_consistency(components)

        # Optimize for tone
        if preferences and preferences.get("tone"):
            optimized_components = await self._optimize_for_tone(optimized_components, preferences["tone"])

        return optimized_components

    async def _calculate_optimization_score(
        self,
        component: MessageComponent,
        preferences: Dict[str, Any] = None
    ) -> float:
        """Calculate optimization score for a component"""
        config = self.component_configs[component.component_type]
        factors = config["optimization_factors"]

        scores = []

        for factor in factors:
            if factor == "engagement":
                score = await self._calculate_engagement_score(component.content)
            elif factor == "personalization":
                score = await self._calculate_personalization_score(component.content)
            elif factor == "clarity":
                score = await self._calculate_clarity_score(component.content)
            elif factor == "actionability":
                score = await self._calculate_actionability_score(component.content)
            elif factor == "value_proposition":
                score = await self._calculate_value_score(component.content)
            elif factor == "tone":
                score = await self._calculate_tone_score(component.content, preferences)
            else:
                score = 0.5  # Default score

            scores.append(score)

        return sum(scores) / len(scores) if scores else 0.0

    async def _calculate_engagement_score(self, content: str) -> float:
        """Calculate engagement score based on content patterns"""
        score = 0.5  # Base score

        # Check for questions
        for pattern in self.engagement_patterns["questions"]:
            if re.search(pattern, content, re.IGNORECASE):
                score += 0.1

        # Check for value words
        for word in self.engagement_patterns["value_words"]:
            if word.lower() in content.lower():
                score += 0.05

        return min(score, 1.0)

    async def _calculate_personalization_score(self, content: str) -> float:
        """Calculate personalization score"""
        score = 0.3  # Base score

        # Check for personal pronouns
        for pattern in self.engagement_patterns["personalization"]:
            if re.search(pattern, content, re.IGNORECASE):
                score += 0.2

        return min(score, 1.0)

    async def _calculate_clarity_score(self, content: str) -> float:
        """Calculate clarity score"""
        # Simple clarity calculation based on sentence structure
        sentences = content.split(".")
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0

        # Optimal sentence length is 15-20 words
        if 10 <= avg_sentence_length <= 25:
            return 0.9
        elif 5 <= avg_sentence_length <= 35:
            return 0.7
        else:
            return 0.5

    async def _calculate_actionability_score(self, content: str) -> float:
        """Calculate actionability score"""
        score = 0.3  # Base score

        for word in self.engagement_patterns["action_words"]:
            if word.lower() in content.lower():
                score += 0.2

        return min(score, 1.0)

    async def _calculate_value_score(self, content: str) -> float:
        """Calculate value proposition score"""
        score = 0.4  # Base score

        value_indicators = ["benefit", "advantage", "improve", "enhance", "save", "increase", "opportunity"]
        for indicator in value_indicators:
            if indicator.lower() in content.lower():
                score += 0.1

        return min(score, 1.0)

    async def _calculate_tone_score(self, content: str, preferences: Dict[str, Any] = None) -> float:
        """Calculate tone consistency score"""
        if not preferences or "tone" not in preferences:
            return 0.7  # Default score

        target_tone = preferences["tone"]
        tone_words = self.tone_indicators.get(target_tone, [])

        score = 0.5  # Base score
        for word in tone_words:
            if word.lower() in content.lower():
                score += 0.1

        return min(score, 1.0)

    async def _optimize_length_and_consistency(
        self,
        components: Dict[str, MessageComponent]
    ) -> Dict[str, MessageComponent]:
        """Optimize components for length and consistency"""
        optimized = {}

        for component_type, component in components.items():
            config = self.component_configs[component_type]
            content = component.content

            # Optimize length
            if len(content) > config["max_length"]:
                content = content[:config["max_length"] - 3] + "..."
            elif len(content) < config["min_length"]:
                # Add filler content if too short
                content += " Please let me know if you'd like to discuss this further."

            # Create optimized component
            optimized_component = MessageComponent(
                component_type=component.component_type,
                content=content,
                metadata=component.metadata,
                optimization_score=component.optimization_score
            )

            optimized[component_type] = optimized_component

        return optimized

    async def _optimize_for_tone(
        self,
        components: Dict[str, MessageComponent],
        target_tone: str
    ) -> Dict[str, MessageComponent]:
        """Optimize components for target tone"""
        optimized = {}

        for component_type, component in components.items():
            content = component.content

            # Apply tone adjustments
            if target_tone == "formal" and component_type == "opening":
                content = content.replace("Hi", "Dear")
            elif target_tone == "casual" and component_type == "opening":
                content = content.replace("Hi", "Hey")

            # Create optimized component
            optimized_component = MessageComponent(
                component_type=component.component_type,
                content=content,
                metadata=component.metadata,
                optimization_score=component.optimization_score
            )

            optimized[component_type] = optimized_component

        return optimized

    async def _generate_component_metadata(
        self,
        component_type: str,
        content: str,
        recipient_profile: Dict[str, Any],
        sender_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate metadata for a component"""
        return {
            "word_count": len(content.split()),
            "character_count": len(content),
            "component_type": component_type,
            "build_timestamp": datetime.utcnow().isoformat(),
            "recipient_references": await self._count_recipient_references(content, recipient_profile),
            "sender_references": await self._count_sender_references(content, sender_profile)
        }

    async def _count_recipient_references(self, content: str, recipient_profile: Dict[str, Any]) -> int:
        """Count references to recipient in content"""
        count = 0
        content_lower = content.lower()

        for field in ["name", "company", "role"]:
            value = recipient_profile.get(field, "")
            if value and value.lower() in content_lower:
                count += 1

        return count

    async def _count_sender_references(self, content: str, sender_profile: Dict[str, Any]) -> int:
        """Count references to sender in content"""
        count = 0
        content_lower = content.lower()

        for field in ["name", "company", "role"]:
            value = sender_profile.get(field, "")
            if value and value.lower() in content_lower:
                count += 1

        return count

    def _calculate_base_score(self) -> float:
        """Calculate base optimization score"""
        return 0.7  # Default base score

__all__ = ["MessageBuilder", "MessageComponent"]
