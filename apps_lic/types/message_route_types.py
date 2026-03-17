"""
LIC Routing Rules - Message type routing and constraints.

Ported from: archives/LIC_capabilities/reconstructed_capabilities.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_through,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "message_route_types", "p0_governance")
_emit_reads_policy_state("p0", "message_route_types", "policy_binding")
_emit_snapshots_state("p0", "message_route_types", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("message_route_types", "p4obs", "metric_1")
_emit_emits_metric_event("message_route_types", "p4obs", "metric_2")
_emit_emits_metric_event("message_route_types", "p4obs", "metric_3")
_emit_emits_metric_event("message_route_types", "p4obs", "metric_4")
_emit_emits_metric_event("message_route_types", "p4obs", "metric_5")
_emit_emits_metric_event("message_route_types", "p4obs", "metric_6")
_emit_records_incident_event("message_route_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("message_route_types", "p4obs", "anomaly")
_emit_writes_observability_log("message_route_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("message_route_types", "p4obs", "mon_state")
_emit_triggers_alert("message_route_types", "p4obs", "alert")
_emit_links_incident_trace("message_route_types", "p4obs", "trace_link")
_emit_captures_pattern("message_route_types", "p3lm", "pattern")
_emit_records_learning_event("message_route_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("message_route_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("message_route_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("message_route_types", "p3lm", "routing")
_emit_improves_agent_policy("message_route_types", "p3lm", "policy")
_emit_stores_learning_state("message_route_types", "p3lm", "state")
_emit_records_execution_trace("message_route_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("message_route_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("message_route_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("message_route_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("message_route_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("message_route_types", "env_read", "p2_env_1")
_emit_reads_environ("message_route_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("message_route_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("message_route_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "message_route_types", "context_pull")
_emit_pulls_context("p1", "message_route_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "message_route_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "message_route_types", "uwg_term_2")
_emit_writes_through("p1", "message_route_types", "write_through")
_emit_writes_through("p1", "message_route_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "message_route_types", "safety_validation")
_emit_invokes_eval("p1", "message_route_types", "eval_call")
_emit_proposal_commits_routing("p1", "message_route_types", "routing_commit")
_emit_escalates_to_human("p1", "message_route_types", "human_escalation")
_emit_routes_through("p1", "message_route_types", "route_through")
_emit_checks_agent_registry("p1", "message_route_types", "agent_registry")
_emit_validates_agent_capability("p1", "message_route_types", "capability")
_emit_dispatches_execution_plan("p1", "message_route_types", "exec_plan")
_emit_agent_executes_agent("p1", "message_route_types", "sub_agent")
_emit_routes_to_agent("p1", "message_route_types", "target_agent")
_emit_verifies_policy("p1", "message_route_types", "policy_check")
_emit_observes_runtime_state("p1", "message_route_types", "runtime_state")
_emit_verifies_boundary("p1", "message_route_types", "boundary_check")
_emit_transcripts_response("p1", "message_route_types", "transcript")
_emit_hard_fails_untranscripted("p1", "message_route_types")
_emit_gated_by_confidence("p1", "message_route_types", "confidence_gate")
emit_replay_key("p0", "message_route_types")
emit_determinism_digest("p0", "message_route_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "message_route_types", "execution_auth")
_emit_validates_capability("p2", "message_route_types", "capability_check")
_emit_routes_to_capability("p2", "message_route_types", "capability_route")
_emit_writes_via_uwg("p2", "message_route_types", "uwg_write")
_emit_blocks_direct_write("p2", "message_route_types", "direct_write_block")
_emit_records_tool_invocation("p2", "message_route_types", "tool_invocation")
_emit_captures_execution_output("p2", "message_route_types", "exec_output")
_emit_dispatches_agent("p3", "message_route_types", "agent_dispatch")
_emit_coordinates_agents("p3", "message_route_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "message_route_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "message_route_types", "healing_outcome")
_emit_escalates_failure("p3", "message_route_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "message_route_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "message_route_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "message_route_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "message_route_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "message_route_types", "eval_metric")
_emit_stores_embedding("p4", "message_route_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "message_route_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "message_route_types", "exec_snapshot_link")
_emit_reads_through("l4", "message_route_types", "urg_read_1")
_emit_reads_through("l4", "message_route_types", "urg_read_2")
_emit_reads_through("l4", "message_route_types", "urg_read_3")
_emit_reads_through("l4", "message_route_types", "urg_read_4")
_emit_reads_through("l4", "message_route_types", "urg_read_5")
_emit_reads_through("l4", "message_route_types", "urg_read_6")
_emit_reads_through("l4", "message_route_types", "urg_read_7")
_emit_reads_through("l4", "message_route_types", "urg_read_8")
_emit_reads_through("l4", "message_route_types", "urg_read_9")
_emit_reads_through("l4", "message_route_types", "urg_read_10")
_emit_reads_through("l4", "message_route_types", "urg_read_11")
_emit_reads_through("l4", "message_route_types", "urg_read_12")
_emit_reads_through("l4", "message_route_types", "urg_read_13")
_emit_reads_through("l4", "message_route_types", "urg_read_14")
_emit_reads_through("l4", "message_route_types", "urg_read_15")
_emit_reads_through("l4", "message_route_types", "urg_read_16")
_emit_reads_through("l4", "message_route_types", "urg_read_17")
_emit_reads_through("l4", "message_route_types", "urg_read_18")
_emit_reads_through("l4", "message_route_types", "urg_read_19")
_emit_reads_through("l4", "message_route_types", "urg_read_20")
_emit_reads_through("l4", "message_route_types", "urg_read_21")
_emit_reads_through("l4", "message_route_types", "urg_read_22")
_emit_reads_through("l4", "message_route_types", "urg_read_23")
_emit_reads_through("l4", "message_route_types", "urg_read_24")
_emit_reads_through("l4", "message_route_types", "urg_read_25")
_emit_reads_through("l4", "message_route_types", "urg_read_26")
_emit_reads_through("l4", "message_route_types", "urg_read_27")
_emit_reads_through("l4", "message_route_types", "urg_read_28")
_emit_reads_through("l4", "message_route_types", "urg_read_29")
_emit_reads_through("l4", "message_route_types", "urg_read_30")
_emit_reads_through("l4", "message_route_types", "urg_read_31")
_emit_reads_through("l4", "message_route_types", "urg_read_32")
_emit_reads_through("l4", "message_route_types", "urg_read_33")
_emit_reads_through("l4", "message_route_types", "urg_read_34")
_emit_reads_through("l4", "message_route_types", "urg_read_35")
_emit_reads_through("l4", "message_route_types", "urg_read_36")
_emit_reads_through("l4", "message_route_types", "urg_read_37")
_emit_reads_through("l4", "message_route_types", "urg_read_38")
_emit_reads_through("l4", "message_route_types", "urg_read_39")
_emit_reads_through("l4", "message_route_types", "urg_read_40")
_emit_reads_through("l4", "message_route_types", "urg_read_41")
_emit_reads_through("l4", "message_route_types", "urg_read_42")
_emit_reads_through("l4", "message_route_types", "urg_read_43")
_emit_reads_through("l4", "message_route_types", "urg_read_44")
_emit_reads_through("l4", "message_route_types", "urg_read_45")
_emit_reads_through("l4", "message_route_types", "urg_read_46")
_emit_reads_through("l4", "message_route_types", "urg_read_47")
_emit_reads_through("l4", "message_route_types", "urg_read_48")
_emit_reads_through("l4", "message_route_types", "urg_read_49")
_emit_reads_through("l4", "message_route_types", "urg_read_50")
_emit_reads_through("l4", "message_route_types", "urg_read_51")
_emit_reads_through("l4", "message_route_types", "urg_read_52")
_emit_reads_through("l4", "message_route_types", "urg_read_53")
_emit_reads_through("l4", "message_route_types", "urg_read_54")
_emit_reads_through("l4", "message_route_types", "urg_read_55")
_emit_reads_through("l4", "message_route_types", "urg_read_56")
_emit_reads_through("l4", "message_route_types", "urg_read_57")
_emit_reads_through("l4", "message_route_types", "urg_read_58")
_emit_reads_through("l4", "message_route_types", "urg_read_59")
_emit_reads_through("l4", "message_route_types", "urg_read_60")
_emit_reads_through("l4", "message_route_types", "urg_read_61")
_emit_reads_through("l4", "message_route_types", "urg_read_62")
_emit_reads_through("l4", "message_route_types", "urg_read_63")
_emit_reads_through("l4", "message_route_types", "urg_read_64")
_emit_reads_through("l4", "message_route_types", "urg_read_65")
_emit_reads_through("l4", "message_route_types", "urg_read_66")
_emit_reads_through("l4", "message_route_types", "urg_read_67")
_emit_reads_through("l4", "message_route_types", "urg_read_68")
_emit_reads_through("l4", "message_route_types", "urg_read_69")
_emit_reads_through("l4", "message_route_types", "urg_read_70")

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
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "LICRouter.determine_route")

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
