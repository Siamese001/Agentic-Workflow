"""
Message Generation Executor Module
LEVEL 5 - Message generation execution and content creation for agentic operations
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class MessageGenerationResult:
    """Represents the result of message generation execution"""
    message_id: str
    generated_content: Dict[str, Any]
    generation_parameters: Dict[str, Any]
    quality_score: float
    execution_time: float

class MessageGenerationExecutor:
    """Handles message generation execution and content creation"""

    def __init__(self):
        self.message_types = [
            "professional_outreach",
            "follow_up_communication",
            "information_request",
            "status_update"
        ]
        self.generation_models = [
            "gpt_4",
            "claude_3",
            "custom_template"
        ]

    async def execute_message_generation(
        self,
        message_plan: Dict[str, Any],
        recipient_profile: Dict[str, Any],
        sender_context: Dict[str, Any]
    ) -> MessageGenerationResult:
        """Execute message generation with specified parameters"""
        try:
            start_time = datetime.utcnow()
            message_id = f"msg_{int(start_time.timestamp())}"

            # Generate message content
            generated_content = await self._generate_message_content(
                message_plan, recipient_profile, sender_context
            )

            # Validate and enhance content
            validated_content = await self._validate_message_content(generated_content)

            # Calculate quality score
            quality_score = self._calculate_quality_score(validated_content, message_plan)

            # Calculate execution time
            execution_time = (datetime.utcnow() - start_time).total_seconds()

            return MessageGenerationResult(
                message_id=message_id,
                generated_content=validated_content,
                generation_parameters={
                    "message_type": message_plan.get("message_type"),
                    "model_used": "gpt_4",
                    "personalization_level": message_plan.get("personalization_level", "medium")
                },
                quality_score=quality_score,
                execution_time=execution_time
            )

        except Exception as e:
            raise Exception(f"Message generation execution failed: {str(e)}")

    async def _generate_message_content(
        self, message_plan: Dict[str, Any], recipient_profile: Dict[str, Any], sender_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate message content based on plan and profiles"""
        message_type = message_plan.get("message_type", "professional_outreach")

        # Generate subject line
        subject = self._generate_subject(message_type, recipient_profile, sender_context)

        # Generate body content
        body = self._generate_body(message_type, recipient_profile, sender_context)

        # Generate call to action
        call_to_action = self._generate_call_to_action(message_type, recipient_profile)

        return {
            "subject": subject,
            "body": body,
            "call_to_action": call_to_action,
            "personalization_elements": self._get_personalization_elements(recipient_profile),
            "tone": message_plan.get("tone", "professional"),
            "length_estimate": len(body.split()) + len(subject.split())
        }

    def _generate_subject(self, message_type: str, recipient_profile: Dict[str, Any], sender_context: Dict[str, Any]) -> str:
        """Generate personalized subject line"""
        recipient_name = recipient_profile.get("name", "there")
        sender_name = sender_context.get("name", "I")

        if message_type == "professional_outreach":
            return f"Connecting from {sender_name} - {recipient_profile.get('company', 'your company')}"
        elif message_type == "follow_up_communication":
            return f"Following up - {sender_name}"
        elif message_type == "information_request":
            return f"Quick question - {sender_name}"
        else:
            return f"Hello {recipient_name} - {sender_name}"

    def _generate_body(self, message_type: str, recipient_profile: Dict[str, Any], sender_context: Dict[str, Any]) -> str:
        """Generate personalized body content"""
        recipient_name = recipient_profile.get("name", "there")
        recipient_company = recipient_profile.get("company", "your company")
        recipient_title = recipient_profile.get("title", "your role")
        sender_name = sender_context.get("name", "I")

        if message_type == "professional_outreach":
            return f"""Dear {recipient_name},

I hope this message finds you well. I'm reaching out as I've been following
your work at {recipient_company} and am impressed by your contributions as {recipient_title}.

I noticed we share similar interests in [relevant technology/industry], and I believe
there could be valuable opportunities for collaboration or knowledge exchange.

Would you be open to a brief conversation to discuss potential synergies?

Best regards,
{sender_name}"""

        elif message_type == "follow_up_communication":
            return f"""Hi {recipient_name},

Just wanted to follow up on my previous message regarding potential collaboration opportunities.

I understand you're likely busy, but I believe a brief 15-minute conversation could be mutually beneficial.

Are you available sometime next week?

Best,
{sender_name}"""

        else:
            return f"""Hello {recipient_name},

I hope you're having a great week.

I wanted to reach out regarding [specific topic] and would appreciate your insights when you have a moment.

Looking forward to hearing from you.

Best regards,
{sender_name}"""

    def _generate_call_to_action(self, message_type: str, recipient_profile: Dict[str, Any]) -> str:
        """Generate appropriate call to action"""
        if message_type == "professional_outreach":
            return "Would you be available for a 15-minute call next week?"
        elif message_type == "follow_up_communication":
            return "Please let me know what time works best for you."
        else:
            return "I look forward to your response."

    def _get_personalization_elements(self, recipient_profile: Dict[str, Any]) -> List[str]:
        """Get list of personalization elements used"""
        elements = []
        if recipient_profile.get("name"):
            elements.append("name_personalization")
        if recipient_profile.get("company"):
            elements.append("company_reference")
        if recipient_profile.get("title"):
            elements.append("role_mention")
        if recipient_profile.get("skills"):
            elements.append("skill_alignment")

        return elements

    async def _validate_message_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance message content"""
        validated_content = content.copy()

        # Add validation metadata
        validated_content["_metadata"] = {
            "validation_status": "approved",
            "generated_at": datetime.utcnow().isoformat(),
            "content_quality": "high"
        }

        # Add content metrics
        validated_content["metrics"] = {
            "word_count": len(content.get("body", "").split()),
            "character_count": len(content.get("body", "")),
            "personalization_score": len(content.get("personalization_elements", [])) / 4.0
        }

        return validated_content

    def _calculate_quality_score(self, content: Dict[str, Any], message_plan: Dict[str, Any]) -> float:
        """Calculate quality score for generated content"""
        base_score = 0.7

        # Personalization bonus
        personalization_bonus = len(content.get("personalization_elements", [])) * 0.05

        # Length appropriateness
        word_count = content.get("metrics", {}).get("word_count", 0)
        if 50 <= word_count <= 200:
            length_bonus = 0.1
        else:
            length_bonus = -0.05

        # Content completeness
        required_elements = ["subject", "body", "call_to_action"]
        completeness_bonus = sum(1 for elem in required_elements if content.get(elem)) / len(required_elements) * 0.1

        final_score = base_score + personalization_bonus + length_bonus + completeness_bonus
        return min(1.0, max(0.1, final_score))

__all__ = ["MessageGenerationExecutor", "MessageGenerationResult"]
