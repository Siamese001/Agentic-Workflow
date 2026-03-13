"""
LIC Routing Rules - Message type routing and constraints.

Ported from: archives/LIC_capabilities/reconstructed_capabilities.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

LIMIT: int = 300


class MessageRoute(Enum):
    """Message Route types for LinkedIn outreach."""

    CONNECTION_REQ = "CONNECTION_REQ"
    SHORT_NEW = "SHORT_NEW"
    LONG_NEW = "LONG_NEW"
    FOLLOW_UP = "FOLLOW_UP"
    INMAIL = "INMAIL"


class RecipientArchetype(Enum):
    """Recipient Archetype classifications."""

    C_LEVEL = "C_LEVEL"
    EXECUTIVE = "EXECUTIVE"
    SENIOR_TA = "SENIOR_TA"
    RECRUITER = "RECRUITER"
    HIRING_MANAGER = "HIRING_MANAGER"


class SignatureFormat(Enum):
    """Signature format types."""

    STANDARD = "standard"
    SIMPLIFIED = "simplified"
    PROFESSIONAL = "professional"
    WARM = "warm"


class CTAFormat(Enum):
    """Call-to-action format types."""

    MICRO = "micro"
    STANDARD = "standard"
    EXPANDED = "expanded"


@dataclass
class RouteConditions:
    """Conditions for Route selection."""

    connection_status: str | None = None
    prior_message_count: int | None = None
    prior_message_count_gt: int | None = None
    prior_message_count_gte: int | None = None


@dataclass
class RouteConstraints:
    """Constraints for a message Route."""

    char_limit: int | None = None
    word_range: tuple[int, int] | None = None
    signature_format: SignatureFormat = SignatureFormat.STANDARD
    subject_line_enabled: bool = False
    attachments_enabled: bool = False
    cta_format: CTAFormat = CTAFormat.STANDARD
    cta_max_words: int | None = None
    greeting_format: str = "Hi {first_name},"


@dataclass
class RouteConfig:
    """Complete configuration for a message Route."""

    Route: MessageRoute
    conditions: RouteConditions
    constraints: RouteConstraints


# Route configurations
ROUTE_CONFIGS: dict[MessageRoute, RouteConfig] = {
    MessageRoute.CONNECTION_REQ: RouteConfig(
        Route=MessageRoute.CONNECTION_REQ,
        conditions=RouteConditions(
            connection_status="not_connected",
            prior_message_count=0,
        ),
        # guardian: allow-magic-config
        constraints=RouteConstraints(
            char_limit=LIMIT,
            word_range=None,
            signature_format=SignatureFormat.SIMPLIFIED,
            subject_line_enabled=False,
            attachments_enabled=False,
            cta_format=CTAFormat.MICRO,
            cta_max_words=5,
            greeting_format="Hi {first_name},",
        ),
    ),
    MessageRoute.SHORT_NEW: RouteConfig(
        Route=MessageRoute.SHORT_NEW,
        conditions=RouteConditions(
            connection_status="not_connected",
            prior_message_count=0,
        ),
        constraints=RouteConstraints(
            char_limit=None,
            word_range=(140, 190),
            signature_format=SignatureFormat.STANDARD,
            subject_line_enabled=False,
            attachments_enabled=False,
            cta_format=CTAFormat.STANDARD,
            greeting_format="Hi {first_name},",
        ),
    ),
    MessageRoute.LONG_NEW: RouteConfig(
        Route=MessageRoute.LONG_NEW,
        conditions=RouteConditions(
            connection_status="not_connected",
            prior_message_count=0,
        ),
        constraints=RouteConstraints(
            char_limit=None,
            word_range=(190, 250),
            signature_format=SignatureFormat.STANDARD,
            subject_line_enabled=True,
            attachments_enabled=True,
            cta_format=CTAFormat.EXPANDED,
            greeting_format="Hi {first_name},",
        ),
    ),
    MessageRoute.FOLLOW_UP: RouteConfig(
        Route=MessageRoute.FOLLOW_UP,
        conditions=RouteConditions(
            prior_message_count_gt=0,
        ),
        constraints=RouteConstraints(
            char_limit=None,
            word_range=(120, 170),
            signature_format=SignatureFormat.WARM,
            subject_line_enabled=False,
            attachments_enabled=False,
            cta_format=CTAFormat.STANDARD,
            greeting_format="Hi {first_name},",
        ),
    ),
    MessageRoute.INMAIL: RouteConfig(
        Route=MessageRoute.INMAIL,
        conditions=RouteConditions(
            connection_status="not_connected",
            prior_message_count_gte=0,
        ),
        constraints=RouteConstraints(
            char_limit=None,
            word_range=(180, 240),
            signature_format=SignatureFormat.PROFESSIONAL,
            subject_line_enabled=True,
            attachments_enabled=True,
            cta_format=CTAFormat.EXPANDED,
            greeting_format="Hi {first_name},",
        ),
    ),
}


@dataclass
class ArchetoneConfig:
    """Tone configuration for an Archetype."""

    message_tone: str
    verb_preference: list[str]
    jargon_level: str
    formality: str
    focus: str


# Archetype tone mappings
ARCHETYPE_TONES: dict[RecipientArchetype, ArchetoneConfig] = {
    RecipientArchetype.C_LEVEL: ArchetoneConfig(
        message_tone="strategic",
        verb_preference=["discuss", "align", "explore", "advance"],
        jargon_level="strategic",
        formality="very high",
        focus="ANALYST_LEVEL_PITCH",
    ),
    RecipientArchetype.EXECUTIVE: ArchetoneConfig(
        message_tone="professional",
        verb_preference=["collaborate", "discuss", "connect", "share"],
        jargon_level="business",
        formality="high",
        focus="OPERATIONAL_PITCH",
    ),
    RecipientArchetype.SENIOR_TA: ArchetoneConfig(
        message_tone="technical_peer",
        verb_preference=["build", "implement", "architect", "optimize"],
        jargon_level="layman",
        formality="moderate",
        focus="EXECUTIVE_CANDIDATE_PITCH",
    ),
    RecipientArchetype.RECRUITER: ArchetoneConfig(
        message_tone="warm_professional",
        verb_preference=["match", "connect", "support", "assist"],
        jargon_level="layman_with_metrics",
        formality="moderate",
        focus="SKILL_TO_ROLE_MAPPING",
    ),
    RecipientArchetype.HIRING_MANAGER: ArchetoneConfig(
        message_tone="professional",
        verb_preference=["discuss", "explore", "demonstrate", "share"],
        jargon_level="business",
        formality="high",
        focus="VALUE_PROPOSITION",
    ),
}


@dataclass
class TemperatureConfig:
    """Temperature configuration for LLM generation."""

    base_temperature: float
    escalation_step: float = 0.15
    max_temperature: float = 0.95
    max_creative_retries: int = 3


# Adaptive temperature by Archetype
ARCHETYPE_TEMPERATURES: dict[RecipientArchetype, float] = {
    RecipientArchetype.C_LEVEL: 0.45,
    RecipientArchetype.EXECUTIVE: 0.5,
    RecipientArchetype.SENIOR_TA: 0.6,
    RecipientArchetype.RECRUITER: 0.65,
    RecipientArchetype.HIRING_MANAGER: 0.55,
}


@dataclass
class ToolCallBudget:
    """Tool call budget configuration."""

    minimum: int = 0
    maximum: int = 20
    guidance: dict[str, str] = field(default_factory=dict)


# Tool call budget by Route
TOOL_CALL_BUDGETS: dict[MessageRoute, str] = {
    MessageRoute.CONNECTION_REQ: "0-8",
    MessageRoute.SHORT_NEW: "3-6",
    MessageRoute.LONG_NEW: "8-12",
    MessageRoute.FOLLOW_UP: "2-4",
    MessageRoute.INMAIL: "8-12",
}


class LICRouter:
    """router for determining message Route and constraints."""

    def __init__(self) -> None:
        """Initialize the router."""
        self._route_configs = ROUTE_CONFIGS
        self._archetype_tones = ARCHETYPE_TONES
        self._archetype_temps = ARCHETYPE_TEMPERATURES

    def determine_route(
        self,
        connection_status: str,
        prior_message_count: int,
        route_override: MessageRoute | None = None,
    ) -> MessageRoute:
        """
        Determine the appropriate message Route.

        Args:
            connection_status: Current connection status
            prior_message_count: Number of prior messages
            route_override: Optional Route override

        Returns:
            Determined MessageRoute
        """
        if route_override is not None:
            return route_override

        # Follow-up takes priority if there are prior messages
        if prior_message_count > 0:
            return MessageRoute.FOLLOW_UP

        # Not connected - determine based on context
        if connection_status == "not_connected":
            # Default to SHORT_NEW for new connections
            return MessageRoute.SHORT_NEW

        return MessageRoute.SHORT_NEW

    def get_route_config(self, Route: MessageRoute) -> RouteConfig:
        """Get configuration for a Route."""
        return self._route_configs[Route]

    def get_constraints(self, Route: MessageRoute) -> RouteConstraints:
        """Get constraints for a Route."""
        return self._route_configs[Route].constraints

    def get_archetype_tone(self, Archetype: RecipientArchetype) -> ArchetoneConfig:
        """Get tone configuration for an Archetype."""
        return self._archetype_tones.get(
            Archetype,
            self._archetype_tones[RecipientArchetype.EXECUTIVE],
        )

    def get_temperature(self, Archetype: RecipientArchetype) -> float:
        """Get foundation temperature for an Archetype."""
        return self._archetype_temps.get(Archetype, 0.55)

    def get_tool_budget(self, Route: MessageRoute) -> str:
        """Get tool call budget for a Route."""
        return TOOL_CALL_BUDGETS.get(Route, "3-6")

    def validate_message_length(
        self,
        text: str,
        Route: MessageRoute,
    ) -> dict[str, object]:
        """
        Validate message length against Route constraints.

        Args:
            text: Message text
            Route: Message Route

        Returns:
            Validation result dictionary
        """
        constraints = self.get_constraints(Route)
        result: dict[str, object] = {
            "is_valid": True,
            "violations": [],
            "word_count": len(text.split()),
            "char_count": len(text),
        }

        # Check character limit
        if constraints.char_limit is not None:
            if len(text) > constraints.char_limit:
                result["is_valid"] = False
                result["violations"].append(
                    f"Character count {len(text)} exceeds limit {constraints.char_limit}",
                )

        # Check word range
        if constraints.word_range is not None:
            word_count = len(text.split())
            min_words, max_words = constraints.word_range
            if word_count < min_words:
                result["is_valid"] = False
                result["violations"].append(f"Word count {word_count} below minimum {min_words}")
            elif word_count > max_words:
                result["is_valid"] = False
                result["violations"].append(f"Word count {word_count} exceeds maximum {max_words}")

        return result


def create_router() -> LICRouter:
    """builder function to create a router."""
    return LICRouter()


def get_route_config(Route: MessageRoute) -> RouteConfig:
    """Get configuration for a Route."""
    return ROUTE_CONFIGS[Route]


def get_archetype_tone(Archetype: RecipientArchetype) -> ArchetoneConfig:
    """Get tone configuration for an Archetype."""
    return ARCHETYPE_TONES.get(
        Archetype,
        ARCHETYPE_TONES[RecipientArchetype.EXECUTIVE],
    )
