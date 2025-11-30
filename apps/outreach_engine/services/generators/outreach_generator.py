"""
Message Generator Service
LEVEL 5 - Service for generating dynamic outreach message content
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import logging
import random

@dataclass
class GeneratedMessage:
    """Generated outreach message with metadata"""
    content: Dict[str, str]
    generation_metadata: Dict[str, Any]
    quality_metrics: Dict[str, float]
    variations: List[Dict[str, str]]

class MessageGenerator:
    """Service for generating dynamic outreach message content"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Message generation templates
        self.message_templates = {
            "email": {
                "subject_templates": [
                    "Professional Opportunity | {topic}",
                    "Collaboration Discussion: {topic}",
                    "Connection Request: {topic}",
                    "{topic} | Discussion",
                    "Following up: {topic}"
                ],
                "opening_templates": [
                    "Hi {recipient_name},",
                    "Hello {recipient_name},",
                    "Dear {recipient_name},",
                    "Greetings {recipient_name},"
                ],
                "body_templates": [
                    "I hope this message finds you well. I came across your profile as {recipient_role} at {recipient_company} and was impressed by {achievement}. With my background in {sender_expertise}, I believe there could be valuable opportunities to collaborate on {topic}.",
                    "I'm reaching out as a fellow {industry} professional. I've been following the innovative work at {recipient_company}, particularly your contributions in {recipient_role}. Given my experience in {sender_expertise}, I'd love to explore how we might work together on {topic}.",
                    "As a {sender_role} with expertise in {sender_expertise}, I've been following the impressive work being done in the {industry} space. Your experience as {recipient_role} at {recipient_company} caught my attention, and I believe there could be synergy in discussing {topic}."
                ],
                "cta_templates": [
                    "Would you be open to a brief call next week to explore potential opportunities?",
                    "I'd appreciate the opportunity to connect and discuss this further. Are you available for a 15-minute call?",
                    "Would you be interested in scheduling a conversation to discuss how we might collaborate?",
                    "I'd welcome the chance to speak with you about this opportunity. What does your availability look like?"
                ],
                "closing_templates": [
                    "Best regards,\n{sender_name}",
                    "Best,\n{sender_name}",
                    "Sincerely,\n{sender_name}",
                    "Looking forward to connecting,\n{sender_name}"
                ]
            },
            "linkedin": {
                "subject_templates": [
                    "Professional Connection",
                    "Discussion Request",
                    "Collaboration Opportunity"
                ],
                "opening_templates": [
                    "Hi {recipient_name},",
                    "Hello {recipient_name},"
                ],
                "body_templates": [
                    "I came across your profile as {recipient_role} at {recipient_company} and was impressed by your work in the {industry} space. With my background in {sender_expertise}, I believe there could be valuable opportunities for collaboration.",
                    "As a fellow professional in the {industry} industry, I've been following the innovative work at {recipient_company}. Your experience as {recipient_role} aligns well with my expertise in {sender_expertise}, and I'd love to connect.",
                    "I noticed we share an interest in {shared_interest}. Given your role as {recipient_role} and my background in {sender_expertise}, I believe there could be valuable synergies to explore."
                ],
                "cta_templates": [
                    "I'd welcome the opportunity to connect and discuss this further.",
                    "I'd love to connect and learn more about your work.",
                    "Looking forward to connecting and exploring potential collaborations."
                ],
                "closing_templates": [
                    "Best,\n{sender_name}",
                    "Thanks,\n{sender_name}",
                    "Looking forward to connecting,\n{sender_name}"
                ]
            },
            "cold_call": {
                "subject_templates": [
                    "Quick Question",
                    "Brief Introduction",
                    "Potential Opportunity"
                ],
                "opening_templates": [
                    "Hi {recipient_name},",
                    "Hello {recipient_name},"
                ],
                "body_templates": [
                    "I'm calling from {sender_company}. I came across your work as {recipient_role} at {recipient_company} and was impressed by your contributions to the {industry} space. With my expertise in {sender_expertise}, I believe there could be immediate opportunities for collaboration.",
                    "My name is {sender_name} and I'm a {sender_role} specializing in {sender_expertise}. I've been following the innovative work at {recipient_company}, and given your role as {recipient_role}, I wanted to reach out directly to discuss potential synergies."
                ],
                "cta_templates": [
                    "Do you have 15 minutes this week for a quick conversation?",
                    "Would you be available for a brief call to discuss this opportunity?",
                    "I'd appreciate 10 minutes of your time to explore how we might work together."
                ],
                "closing_templates": [
                    "Thanks,\n{sender_name}",
                    "Best,\n{sender_name}"
                ]
            }
        }

        # Content variation strategies
        self.variation_strategies = {
            "tone_variation": ["formal", "professional", "friendly", "enthusiastic"],
            "length_variation": ["brief", "medium", "detailed"],
            "focus_variation": ["value_proposition", "relationship", "opportunity", "collaboration"]
        }

        # Quality metrics weights
        self.quality_weights = {
            "personalization": 0.3,
            "clarity": 0.25,
            "engagement": 0.2,
            "professionalism": 0.15,
            "actionability": 0.1
        }

    async def generate_message(
        self,
        recipient_profile: Dict[str, Any],
        sender_profile: Dict[str, Any],
        outreach_type: str,
        context: Dict[str, Any] = None,
        preferences: Dict[str, Any] = None,
        variations: int = 1
    ) -> GeneratedMessage:
        """
        Generate outreach message with variations
        
        Args:
            recipient_profile: Information about the recipient
            sender_profile: Information about the sender
            outreach_type: Type of outreach message
            context: Additional context for personalization
            preferences: User preferences for tone and style
            variations: Number of variations to generate
            
        Returns:
            Generated message with metadata and variations
        """
        try:
            self.logger.info(f"Generating {outreach_type} message with {variations} variations")

            # Generate primary message
            primary_message = await self._generate_single_message(
                recipient_profile, sender_profile, outreach_type, context, preferences
            )

            # Generate variations if requested
            message_variations = []
            if variations > 1:
                for i in range(variations - 1):
                    variation = await self._generate_variation(
                        recipient_profile, sender_profile, outreach_type, context, preferences, i
                    )
                    message_variations.append(variation)

            # Calculate quality metrics
            quality_metrics = await self._calculate_quality_metrics(
                primary_message, recipient_profile, sender_profile
            )

            # Generate metadata
            generation_metadata = await self._generate_generation_metadata(
                recipient_profile, sender_profile, outreach_type, context, preferences
            )

            return GeneratedMessage(
                content=primary_message,
                generation_metadata=generation_metadata,
                quality_metrics=quality_metrics,
                variations=message_variations
            )

        except Exception as e:
            self.logger.error(f"Error generating message: {e}")
            raise e

    async def _generate_single_message(
        self,
        recipient_profile: Dict[str, Any],
        sender_profile: Dict[str, Any],
        outreach_type: str,
        context: Dict[str, Any] = None,
        preferences: Dict[str, Any] = None
    ) -> Dict[str, str]:
        """Generate a single outreach message"""

        # Get templates for outreach type
        templates = self.message_templates.get(outreach_type, self.message_templates["email"])

        # Generate subject
        subject = await self._generate_subject(recipient_profile, sender_profile, context, templates)

        # Generate opening
        opening = await self._generate_opening(recipient_profile, sender_profile, templates)

        # Generate body
        body = await self._generate_body(recipient_profile, sender_profile, context, templates)

        # Generate call to action
        call_to_action = await self._generate_call_to_action(
            recipient_profile, sender_profile, outreach_type, context, templates
        )

        # Generate closing
        closing = await self._generate_closing(sender_profile, preferences, templates)

        # Assemble full message
        full_body = f"{opening}\n\n{body}\n\n{call_to_action}\n\n{closing}"

        return {
            "subject": subject,
            "body": full_body.strip(),
            "call_to_action": call_to_action,
            "opening": opening,
            "closing": closing
        }

    async def _generate_subject(
        self,
        recipient_profile: Dict[str, Any],
        sender_profile: Dict[str, Any],
        context: Dict[str, Any] = None,
        templates: Dict[str, List[str]] = None
    ) -> str:
        """Generate subject line"""
        if not templates:
            templates = self.message_templates["email"]

        # Determine topic for subject
        topic = "Professional Connection"
        if context and context.get("purpose"):
            purpose = context["purpose"].lower()
            if "collaboration" in purpose:
                topic = "Collaboration"
            elif "partnership" in purpose:
                topic = "Partnership"
            elif "opportunity" in purpose:
                topic = "Opportunity"
            elif "networking" in purpose:
                topic = "Networking"

        # Select and customize template
        subject_template = random.choice(templates["subject_templates"])
        subject = subject_template.format(topic=topic)

        # Add personalization if space allows
        recipient_company = recipient_profile.get("company", "")
        if recipient_company and len(subject) < 70:
            subject += f" | {recipient_company}"

        return subject

    async def _generate_opening(
        self,
        recipient_profile: Dict[str, Any],
        sender_profile: Dict[str, Any],
        templates: Dict[str, List[str]] = None
    ) -> str:
        """Generate message opening"""
        if not templates:
            templates = self.message_templates["email"]

        recipient_name = recipient_profile.get("name", "there")
        opening_template = random.choice(templates["opening_templates"])

        return opening_template.format(recipient_name=recipient_name)

    async def _generate_body(
        self,
        recipient_profile: Dict[str, Any],
        sender_profile: Dict[str, Any],
        context: Dict[str, Any] = None,
        templates: Dict[str, List[str]] = None
    ) -> str:
        """Generate message body"""
        if not templates:
            templates = self.message_templates["email"]

        # Prepare template variables
        template_vars = {
            "recipient_name": recipient_profile.get("name", "there"),
            "recipient_role": recipient_profile.get("role", "professional"),
            "recipient_company": recipient_profile.get("company", "your company"),
            "industry": recipient_profile.get("industry", "your industry"),
            "sender_name": sender_profile.get("name", "there"),
            "sender_role": sender_profile.get("role", "professional"),
            "sender_company": sender_profile.get("company", "my company"),
            "achievement": "your impressive work",
            "topic": "collaboration opportunities"
        }

        # Add expertise information
        sender_expertise = sender_profile.get("expertise", [])
        if sender_expertise:
            template_vars["sender_expertise"] = ", ".join(sender_expertise[:3])
        else:
            template_vars["sender_expertise"] = "your field"

        # Add shared interests if available
        if context and context.get("shared_interests"):
            template_vars["shared_interest"] = context["shared_interests"][0]
        else:
            template_vars["shared_interest"] = "our industry"

        # Select and customize template
        body_template = random.choice(templates["body_templates"])
        body = body_template.format(**template_vars)

        # Add context-specific content
        if context and context.get("mutual_connections"):
            connections = context["mutual_connections"][:2]
            if len(connections) == 1:
                body += f" I noticed we're both connected with {connections[0]}."
            else:
                body += f" I noticed we're both connected with {connections[0]} and {connections[1]}."

        return body.strip()

    async def _generate_call_to_action(
        self,
        recipient_profile: Dict[str, Any],
        sender_profile: Dict[str, Any],
        outreach_type: str,
        context: Dict[str, Any] = None,
        templates: Dict[str, List[str]] = None
    ) -> str:
        """Generate call to action"""
        if not templates:
            templates = self.message_templates["email"]

        # Adjust urgency based on context
        urgency = context.get("urgency", "medium") if context else "medium"

        if outreach_type == "email":
            if urgency == "high":
                return "Would you be available for a brief call this week to discuss this opportunity?"
            elif urgency == "urgent":
                return "I'd appreciate the opportunity to speak with you as soon as possible. Are you available for a quick call today or tomorrow?"
            else:
                cta_template = random.choice(templates["cta_templates"])
                return cta_template
        else:
            cta_template = random.choice(templates["cta_templates"])
            return cta_template

    async def _generate_closing(
        self,
        sender_profile: Dict[str, Any],
        preferences: Dict[str, Any] = None,
        templates: Dict[str, List[str]] = None
    ) -> str:
        """Generate message closing"""
        if not templates:
            templates = self.message_templates["email"]

        sender_name = sender_profile.get("name", "there")
        tone = preferences.get("tone", "professional") if preferences else "professional"

        # Select closing based on tone
        if tone == "formal":
            closing_template = "Sincerely,\n{sender_name}"
        elif tone == "casual":
            closing_template = "Thanks,\n{sender_name}"
        else:
            closing_template = random.choice(templates["closing_templates"])

        return closing_template.format(sender_name=sender_name)

    async def _generate_variation(
        self,
        recipient_profile: Dict[str, Any],
        sender_profile: Dict[str, Any],
        outreach_type: str,
        context: Dict[str, Any] = None,
        preferences: Dict[str, Any] = None,
        variation_index: int = 0
    ) -> Dict[str, str]:
        """Generate a variation of the message"""

        # Modify preferences for variation
        variation_preferences = preferences.copy() if preferences else {}

        # Cycle through variation strategies
        strategies = list(self.variation_strategies.keys())
        strategy = strategies[variation_index % len(strategies)]

        if strategy == "tone_variation":
            tones = self.variation_strategies["tone_variation"]
            current_tone = variation_preferences.get("tone", "professional")
            new_tone = tones[(tones.index(current_tone) + 1) % len(tones)] if current_tone in tones else tones[0]
            variation_preferences["tone"] = new_tone

        elif strategy == "length_variation":
            lengths = self.variation_strategies["length_variation"]
            variation_preferences["length"] = lengths[variation_index % len(lengths)]

        elif strategy == "focus_variation":
            # Modify context for different focus
            if not context:
                context = {}

            focuses = self.variation_strategies["focus_variation"]
            focus = focuses[variation_index % len(focuses)]

            if focus == "value_proposition":
                context["purpose"] = "exploring value-driven collaboration"
            elif focus == "relationship":
                context["purpose"] = "building professional relationship"
            elif focus == "opportunity":
                context["purpose"] = "discussing potential opportunities"
            elif focus == "collaboration":
                context["purpose"] = "exploring collaboration possibilities"

        # Generate variation with modified preferences
        return await self._generate_single_message(
            recipient_profile, sender_profile, outreach_type, context, variation_preferences
        )

    async def _calculate_quality_metrics(
        self,
        message: Dict[str, str],
        recipient_profile: Dict[str, Any],
        sender_profile: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate quality metrics for generated message"""

        metrics = {}

        # Personalization score
        metrics["personalization"] = await self._calculate_personalization_score(
            message, recipient_profile
        )

        # Clarity score
        metrics["clarity"] = await self._calculate_clarity_score(message)

        # Engagement score
        metrics["engagement"] = await self._calculate_engagement_score(message)

        # Professionalism score
        metrics["professionalism"] = await self._calculate_professionalism_score(message)

        # Actionability score
        metrics["actionability"] = await self._calculate_actionability_score(message)

        # Overall quality score
        metrics["overall"] = sum(
            score * self.quality_weights[metric]
            for metric, score in metrics.items()
            if metric != "overall"
        )

        return metrics

    async def _calculate_personalization_score(
        self,
        message: Dict[str, str],
        recipient_profile: Dict[str, Any]
    ) -> float:
        """Calculate personalization score"""
        score = 0.0
        content = message.get("body", "").lower()

        # Check for recipient name
        recipient_name = recipient_profile.get("name", "").lower()
        if recipient_name and recipient_name in content:
            score += 0.3

        # Check for recipient company
        recipient_company = recipient_profile.get("company", "").lower()
        if recipient_company and recipient_company in content:
            score += 0.3

        # Check for recipient role
        recipient_role = recipient_profile.get("role", "").lower()
        if recipient_role and recipient_role in content:
            score += 0.2

        # Check for mutual connections
        if "connected with" in content:
            score += 0.1

        # Check for shared interests
        if "share" in content and "interest" in content:
            score += 0.1

        return min(score, 1.0)

    async def _calculate_clarity_score(self, message: Dict[str, str]) -> float:
        """Calculate clarity score"""
        content = message.get("body", "")

        # Check sentence length
        sentences = content.split(".")
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0

        # Optimal sentence length is 15-20 words
        if 10 <= avg_sentence_length <= 25:
            length_score = 0.8
        elif 5 <= avg_sentence_length <= 35:
            length_score = 0.6
        else:
            length_score = 0.4

        # Check for clear structure
        has_opening = bool(message.get("opening"))
        has_body = bool(message.get("body"))
        has_closing = bool(message.get("closing"))

        structure_score = 0.2 if has_opening else 0
        structure_score += 0.4 if has_body else 0
        structure_score += 0.2 if has_closing else 0
        structure_score += 0.2 if message.get("call_to_action") else 0

        return (length_score + structure_score) / 2

    async def _calculate_engagement_score(self, message: Dict[str, str]) -> float:
        """Calculate engagement score"""
        content = message.get("body", "").lower()

        score = 0.5  # Base score

        # Check for questions
        if "?" in content:
            score += 0.2

        # Check for engagement words
        engagement_words = ["opportunity", "collaborate", "discuss", "explore", "connect"]
        for word in engagement_words:
            if word in content:
                score += 0.1

        # Check subject line engagement
        subject = message.get("subject", "").lower()
        if any(word in subject for word in ["opportunity", "collaboration", "discussion"]):
            score += 0.1

        return min(score, 1.0)

    async def _calculate_professionalism_score(self, message: Dict[str, str]) -> float:
        """Calculate professionalism score"""
        content = message.get("body", "").lower()

        score = 0.7  # Base score

        # Check for professional language
        professional_words = ["opportunity", "collaboration", "expertise", "experience", "professional"]
        for word in professional_words:
            if word in content:
                score += 0.05

        # Check for unprofessional language
        unprofessional_words = ["awesome", "cool", "dude", "hey"]
        for word in unprofessional_words:
            if word in content:
                score -= 0.1

        return max(min(score, 1.0), 0.0)

    async def _calculate_actionability_score(self, message: Dict[str, str]) -> float:
        """Calculate actionability score"""
        content = message.get("call_to_action", "").lower()

        score = 0.3  # Base score

        # Check for action words
        action_words = ["call", "schedule", "connect", "discuss", "meet", "reply"]
        for word in action_words:
            if word in content:
                score += 0.2

        # Check for time specificity
        if any(time_word in content for time_word in ["week", "minutes", "available", "schedule"]):
            score += 0.2

        return min(score, 1.0)

    async def _generate_generation_metadata(
        self,
        recipient_profile: Dict[str, Any],
        sender_profile: Dict[str, Any],
        outreach_type: str,
        context: Dict[str, Any] = None,
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate metadata for message generation"""
        return {
            "generation_timestamp": datetime.utcnow().isoformat(),
            "outreach_type": outreach_type,
            "recipient_industry": recipient_profile.get("industry", "unknown"),
            "sender_expertise": sender_profile.get("expertise", []),
            "context_available": bool(context),
            "preferences_applied": preferences or {},
            "template_count": len(self.message_templates.get(outreach_type, {})),
            "generation_strategy": "template_based_with_personalization"
        }

__all__ = ["MessageGenerator", "GeneratedMessage"]
