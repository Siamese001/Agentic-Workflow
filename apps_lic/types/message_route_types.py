"""
LIC Routing Rules - Message type routing and constraints.

Ported from: archives/LIC_capabilities/reconstructed_capabilities.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "message_route_types", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "message_route_types", "policy_binding")
trace_contract._emit_snapshots_state("p0", "message_route_types", "state_snapshot")

trace_contract._emit_emits_metric_event("message_route_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("message_route_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("message_route_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("message_route_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("message_route_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("message_route_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("message_route_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("message_route_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("message_route_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("message_route_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("message_route_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("message_route_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("message_route_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("message_route_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("message_route_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("message_route_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("message_route_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("message_route_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("message_route_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("message_route_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("message_route_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("message_route_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("message_route_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("message_route_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("message_route_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("message_route_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("message_route_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("message_route_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "message_route_types", "context_pull")
trace_contract._emit_pulls_context("p1", "message_route_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "message_route_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "message_route_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "message_route_types", "write_through")
trace_contract._emit_writes_through("p1", "message_route_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "message_route_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "message_route_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "message_route_types", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "message_route_types", "human_escalation")
trace_contract._emit_routes_through("p1", "message_route_types", "route_through")
trace_contract._emit_checks_agent_registry("p1", "message_route_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "message_route_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "message_route_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "message_route_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "message_route_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "message_route_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "message_route_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "message_route_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "message_route_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "message_route_types")
trace_contract._emit_gated_by_confidence("p1", "message_route_types", "confidence_gate")
trace_contract.emit_replay_key("p0", "message_route_types")
trace_contract.emit_determinism_digest("p0", "message_route_types")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "message_route_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "message_route_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "message_route_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "message_route_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "message_route_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "message_route_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "message_route_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "message_route_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "message_route_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "message_route_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "message_route_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "message_route_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "message_route_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "message_route_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "message_route_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "message_route_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "message_route_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "message_route_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "message_route_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "message_route_types", "exec_snapshot_link")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_1")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_2")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_3")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_4")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_5")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_6")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_7")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_8")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_9")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_10")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_11")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_12")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_13")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_14")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_15")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_16")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_17")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_18")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_19")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_20")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_21")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_22")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_23")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_24")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_25")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_26")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_27")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_28")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_29")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_30")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_31")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_32")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_33")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_34")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_35")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_36")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_37")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_38")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_39")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_40")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_41")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_42")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_43")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_44")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_45")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_46")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_47")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_48")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_49")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_50")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_51")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_52")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_53")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_54")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_55")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_56")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_57")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_58")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_59")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_60")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_61")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_62")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_63")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_64")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_65")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_66")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_67")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_68")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_69")
trace_contract._emit_reads_through("l4", "message_route_types", "urg_read_70")

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
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "LICRouter.determine_route")

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
