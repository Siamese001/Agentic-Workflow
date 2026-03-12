"""
LIC Archetype Templates - Generation templates for different recipient types.

Ported from: archives/LIC_capabilities/reconstructed_capabilities.py
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class RecipientArchetype(Enum):
    """Recipient Archetype classifications."""

    C_LEVEL = "C_LEVEL"
    EXECUTIVE = "EXECUTIVE"
    SENIOR_TA = "SENIOR_TA"
    RECRUITER = "RECRUITER"


@dataclass
class SubjectLineBrief:
    """Brief for subject line generation."""

    word_count: tuple[int, int]
    tone: str
    forbidden_phrases: list[str] = field(default_factory=list)


@dataclass
class MessageBodyBrief:
    """Brief for message body generation."""

    word_count: tuple[int, int]
    jargon_level: str
    focus: str


@dataclass
class CTABrief:
    """Brief for call-to-action generation."""

    word_count: tuple[int, int]
    tone: str
    strategy: str | None = None


@dataclass
class CreativeBrief:
    """Complete creative brief for message generation."""

    subject_line: SubjectLineBrief
    message_body: MessageBodyBrief
    cta: CTABrief


@dataclass
class ArchetypeTemplate:
    """Complete template for an Archetype."""

    Archetype: RecipientArchetype
    system_instructions: str
    tone: str
    approach: str
    avoid: str
    creative_brief: CreativeBrief


# Archetype generation templates
ARCHETYPE_TEMPLATES: dict[RecipientArchetype, ArchetypeTemplate] = {
    RecipientArchetype.C_LEVEL: ArchetypeTemplate(
        Archetype=RecipientArchetype.C_LEVEL,
        system_instructions=(
            "You are crafting an executive-level message that demonstrates "
            "thought leadership and strategic alignment."
        ),
        tone=("Strategic, confident, focused on business impact and organizational transformation."),
        approach=(
            "Lead with macro trends, demonstrate understanding of strategic "
            "challenges, position yourself as a peer with complementary expertise."
        ),
        avoid=("Tactical details, overt sales language, assumptions about their specific pain points."),
        creative_brief=CreativeBrief(
            subject_line=SubjectLineBrief(
                word_count=(4, 7),
                tone="peer",
                forbidden_phrases=[":", "!", "?"],
            ),
            message_body=MessageBodyBrief(
                word_count=(190, 230),
                jargon_level="strategic",
                focus="ANALYST_LEVEL_PITCH",
            ),
            cta=CTABrief(
                word_count=(15, 20),
                tone="formal_neutral",
                strategy="RELATIONAL_EXPLORATORY",
            ),
        ),
    ),
    RecipientArchetype.EXECUTIVE: ArchetypeTemplate(
        Archetype=RecipientArchetype.EXECUTIVE,
        system_instructions=(
            "You are crafting a professional message that emphasizes collaboration and mutual value."
        ),
        tone=("Professional, collaborative, focused on team objectives and operational excellence."),
        approach=(
            "Reference their role and responsibilities, demonstrate understanding "
            "of their team's challenges, offer concrete value."
        ),
        avoid=("Overly formal language, standard value propositions, excessive deference."),
        creative_brief=CreativeBrief(
            subject_line=SubjectLineBrief(
                word_count=(5, 8),
                tone="direct",
            ),
            message_body=MessageBodyBrief(
                word_count=(160, 220),
                jargon_level="business",
                focus="OPERATIONAL_PITCH",
            ),
            cta=CTABrief(
                word_count=(15, 20),
                tone="collaborative",
                strategy="STRATEGIC_ALIGNMENT_EXPLORATION",
            ),
        ),
    ),
    RecipientArchetype.SENIOR_TA: ArchetypeTemplate(
        Archetype=RecipientArchetype.SENIOR_TA,
        system_instructions=(
            "You are crafting a technical message for a senior technical "
            "authority (architect, principal engineer, tech lead)."
        ),
        tone=(
            "Technical peer, respectful but confident, focused on architectural "
            "decisions and technical excellence."
        ),
        approach=(
            "Reference specific technologies or patterns, demonstrate technical "
            "credibility, respect their authority on technical direction."
        ),
        avoid=(
            "Marketing language, oversimplification of technical concepts, "
            "challenging their technical decisions."
        ),
        creative_brief=CreativeBrief(
            subject_line=SubjectLineBrief(
                word_count=(6, 9),
                tone="practical",
            ),
            message_body=MessageBodyBrief(
                word_count=(150, 190),
                jargon_level="layman",
                focus="EXECUTIVE_CANDIDATE_PITCH",
            ),
            cta=CTABrief(
                word_count=(10, 15),
                tone="professional_neutral",
            ),
        ),
    ),
    RecipientArchetype.RECRUITER: ArchetypeTemplate(
        Archetype=RecipientArchetype.RECRUITER,
        system_instructions=(
            "You are crafting a job-focused message that centers on role fit and candidate qualifications."
        ),
        tone=("Warm, professional, focused on alignment between candidate skills and role requirements."),
        approach=(
            "Lead with relevant experience, highlight specific skills that match "
            "job description, emphasize career growth potential."
        ),
        avoid=("standard qualifications, vague interest statements, over-selling unrelated experience."),
        creative_brief=CreativeBrief(
            subject_line=SubjectLineBrief(
                word_count=(6, 9),
                tone="respectful",
            ),
            message_body=MessageBodyBrief(
                word_count=(140, 170),
                jargon_level="layman_with_metrics",
                focus="SKILL_TO_ROLE_MAPPING",
            ),
            cta=CTABrief(
                word_count=(10, 15),
                tone="professional_neutral",
            ),
        ),
    ),
}


@dataclass
class SignatureTemplate:
    """Template for message signature."""

    template: str
    use_for: list[str]
    line_count: int


# Signature format templates
SIGNATURE_TEMPLATES: dict[str, SignatureTemplate] = {
    "standard": SignatureTemplate(
        template="Best regards,\n{first_name} {last_name}\n{title}\n{linkedin_url}",
        use_for=["INMAIL", "LONG_NEW"],
        line_count=4,
    ),
    "simplified": SignatureTemplate(
        template="Regards,\n{first_name}",
        use_for=["CONNECTION_REQ"],
        line_count=2,
    ),
    "professional": SignatureTemplate(
        template="Sincerely,\n{first_name} {last_name}\n{title}",
        use_for=["EXECUTIVE", "C_LEVEL recipients"],
        line_count=3,
    ),
    "warm": SignatureTemplate(
        template="Thanks,\n{first_name}",
        use_for=["FOLLOW_UP", "RECRUITER recipients"],
        line_count=2,
    ),
}


@dataclass
class GreetingTemplate:
    """Template for message greeting."""

    template: str
    note: str


# Greeting templates by Route
GREETING_TEMPLATES: dict[str, GreetingTemplate] = {
    "CONNECTION_REQ": GreetingTemplate(
        template="Hi {first_name},",
        note="Simple, direct greeting",
    ),
    "INMAIL": GreetingTemplate(
        template="Hi {first_name},",
        note="Professional but warm",
    ),
    "SHORT_NEW": GreetingTemplate(
        template="Hi {first_name},",
        note="Standard greeting",
    ),
    "LONG_NEW": GreetingTemplate(
        template="Hi {first_name},",
        note="Can be adjusted based on recipient_type",
    ),
    "FOLLOW_UP": GreetingTemplate(
        template="Hi {first_name},",
        note="Assumes prior connection",
    ),
}

# Forbidden greeting patterns
FORBIDDEN_GREETINGS: list[str] = [
    "Dear {first_name}",
    "Hey {first_name}",
    "Greetings",
]


class ArchetypeTemplateManager:
    """coordinator for Archetype templates."""

    def __init__(self) -> None:
        """Initialize the template coordinator."""
        self._templates = ARCHETYPE_TEMPLATES
        self._signatures = SIGNATURE_TEMPLATES
        self._greetings = GREETING_TEMPLATES

    def get_template(self, Archetype: RecipientArchetype) -> ArchetypeTemplate:
        """Get template for an Archetype."""
        return self._templates.get(
            Archetype,
            self._templates[RecipientArchetype.EXECUTIVE],
        )

    def get_system_instructions(self, Archetype: RecipientArchetype) -> str:
        """Get system instructions for an Archetype."""
        template = self.get_template(Archetype)
        return template.system_instructions

    def get_creative_brief(self, Archetype: RecipientArchetype) -> CreativeBrief:
        """Get creative brief for an Archetype."""
        template = self.get_template(Archetype)
        return template.creative_brief

    def get_word_count_range(self, Archetype: RecipientArchetype) -> tuple[int, int]:
        """Get word count range for an Archetype."""
        template = self.get_template(Archetype)
        return template.creative_brief.message_body.word_count

    def get_signature_template(self, format_name: str) -> SignatureTemplate:
        """Get signature template by format name."""
        return self._signatures.get(
            format_name,
            self._signatures["standard"],
        )

    def get_greeting_template(self, Route: str) -> GreetingTemplate:
        """Get greeting template by Route."""
        return self._greetings.get(
            Route,
            self._greetings["SHORT_NEW"],
        )

    def format_signature(
        self,
        format_name: str,
        first_name: str,
        last_name: str = "",
        title: str = "",
        linkedin_url: str = "",
    ) -> str:
        """Format a signature with provided values."""
        template = self.get_signature_template(format_name)
        return template.template.format(
            first_name=first_name,
            last_name=last_name,
            title=title,
            linkedin_url=linkedin_url,
        )

    def format_greeting(self, Route: str, first_name: str) -> str:
        """Format a greeting with provided values."""
        template = self.get_greeting_template(Route)
        return template.template.format(first_name=first_name)

    def validate_greeting(self, greeting: str) -> dict[str, object]:
        """Validate a greeting against forbidden patterns."""
        result: dict[str, object] = {
            "is_valid": True,
            "violations": [],
        }

        for forbidden in FORBIDDEN_GREETINGS:
            pattern_base = forbidden.replace("{first_name}", "")
            if pattern_base.strip() in greeting:
                result["is_valid"] = False
                result["violations"].append(f"Forbidden pattern: {forbidden}")

        # Check for comma after name
        if "," not in greeting:
            result["violations"].append("Missing comma after name")

        return result


def create_template_manager() -> ArchetypeTemplateManager:
    """builder function to create a template coordinator."""
    return ArchetypeTemplateManager()


def get_archetype_template(Archetype: RecipientArchetype) -> ArchetypeTemplate:
    """Get template for an Archetype."""
    return ARCHETYPE_TEMPLATES.get(
        Archetype,
        ARCHETYPE_TEMPLATES[RecipientArchetype.EXECUTIVE],
    )


def get_signature_template(format_name: str) -> SignatureTemplate:
    """Get signature template by format name."""
    return SIGNATURE_TEMPLATES.get(
        format_name,
        SIGNATURE_TEMPLATES["standard"],
    )
