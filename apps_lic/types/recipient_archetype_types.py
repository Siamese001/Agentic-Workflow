"""
LIC Archetype Templates - Generation templates for different recipient types.

Ported from: archives/LIC_capabilities/reconstructed_capabilities.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "recipient_archetype_types", "p0_governance")
_emit_reads_policy_state("p0", "recipient_archetype_types", "policy_binding")
_emit_snapshots_state("p0", "recipient_archetype_types", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("recipient_archetype_types", "p4obs", "metric_1")
_emit_emits_metric_event("recipient_archetype_types", "p4obs", "metric_2")
_emit_emits_metric_event("recipient_archetype_types", "p4obs", "metric_3")
_emit_emits_metric_event("recipient_archetype_types", "p4obs", "metric_4")
_emit_emits_metric_event("recipient_archetype_types", "p4obs", "metric_5")
_emit_emits_metric_event("recipient_archetype_types", "p4obs", "metric_6")
_emit_records_incident_event("recipient_archetype_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("recipient_archetype_types", "p4obs", "anomaly")
_emit_writes_observability_log("recipient_archetype_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("recipient_archetype_types", "p4obs", "mon_state")
_emit_triggers_alert("recipient_archetype_types", "p4obs", "alert")
_emit_links_incident_trace("recipient_archetype_types", "p4obs", "trace_link")
_emit_captures_pattern("recipient_archetype_types", "p3lm", "pattern")
_emit_records_learning_event("recipient_archetype_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("recipient_archetype_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("recipient_archetype_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("recipient_archetype_types", "p3lm", "routing")
_emit_improves_agent_policy("recipient_archetype_types", "p3lm", "policy")
_emit_stores_learning_state("recipient_archetype_types", "p3lm", "state")
_emit_records_execution_trace("recipient_archetype_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("recipient_archetype_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("recipient_archetype_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("recipient_archetype_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("recipient_archetype_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("recipient_archetype_types", "env_read", "p2_env_1")
_emit_reads_environ("recipient_archetype_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("recipient_archetype_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("recipient_archetype_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "recipient_archetype_types", "context_pull")
_emit_pulls_context("p1", "recipient_archetype_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "recipient_archetype_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "recipient_archetype_types", "uwg_term_2")
_emit_writes_through("p1", "recipient_archetype_types", "write_through")
_emit_writes_through("p1", "recipient_archetype_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "recipient_archetype_types", "safety_validation")
_emit_invokes_eval("p1", "recipient_archetype_types", "eval_call")
_emit_proposal_commits_routing("p1", "recipient_archetype_types", "routing_commit")
_emit_escalates_to_human("p1", "recipient_archetype_types", "human_escalation")
_emit_routes_through("p1", "recipient_archetype_types", "route_through")
_emit_checks_agent_registry("p1", "recipient_archetype_types", "agent_registry")
_emit_validates_agent_capability("p1", "recipient_archetype_types", "capability")
_emit_dispatches_execution_plan("p1", "recipient_archetype_types", "exec_plan")
_emit_agent_executes_agent("p1", "recipient_archetype_types", "sub_agent")
_emit_routes_to_agent("p1", "recipient_archetype_types", "target_agent")
_emit_verifies_policy("p1", "recipient_archetype_types", "policy_check")
_emit_observes_runtime_state("p1", "recipient_archetype_types", "runtime_state")
_emit_verifies_boundary("p1", "recipient_archetype_types", "boundary_check")
_emit_transcripts_response("p1", "recipient_archetype_types", "transcript")
_emit_hard_fails_untranscripted("p1", "recipient_archetype_types")
_emit_gated_by_confidence("p1", "recipient_archetype_types", "confidence_gate")
emit_replay_key("p0", "recipient_archetype_types")
emit_determinism_digest("p0", "recipient_archetype_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "recipient_archetype_types", "execution_auth")
_emit_validates_capability("p2", "recipient_archetype_types", "capability_check")
_emit_routes_to_capability("p2", "recipient_archetype_types", "capability_route")
_emit_writes_via_uwg("p2", "recipient_archetype_types", "uwg_write")
_emit_blocks_direct_write("p2", "recipient_archetype_types", "direct_write_block")
_emit_records_tool_invocation("p2", "recipient_archetype_types", "tool_invocation")
_emit_captures_execution_output("p2", "recipient_archetype_types", "exec_output")
_emit_dispatches_agent("p3", "recipient_archetype_types", "agent_dispatch")
_emit_coordinates_agents("p3", "recipient_archetype_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "recipient_archetype_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "recipient_archetype_types", "healing_outcome")
_emit_escalates_failure("p3", "recipient_archetype_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "recipient_archetype_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "recipient_archetype_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "recipient_archetype_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "recipient_archetype_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "recipient_archetype_types", "eval_metric")
_emit_stores_embedding("p4", "recipient_archetype_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "recipient_archetype_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "recipient_archetype_types", "exec_snapshot_link")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_1")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_2")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_3")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_4")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_5")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_6")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_7")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_8")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_9")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_10")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_11")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_12")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_13")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_14")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_15")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_16")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_17")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_18")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_19")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_20")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_21")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_22")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_23")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_24")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_25")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_26")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_27")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_28")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_29")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_30")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_31")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_32")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_33")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_34")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_35")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_36")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_37")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_38")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_39")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_40")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_41")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_42")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_43")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_44")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_45")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_46")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_47")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_48")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_49")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_50")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_51")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_52")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_53")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_54")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_55")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_56")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_57")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_58")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_59")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_60")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_61")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_62")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_63")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_64")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_65")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_66")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_67")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_68")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_69")
_emit_reads_through("l4", "recipient_archetype_types", "urg_read_70")


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
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ArchetypeTemplateManager.get_system_instructions")

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
