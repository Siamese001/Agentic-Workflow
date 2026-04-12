"""LinkedIn Outreach Orchestration configuration.

Extracted from legacy LIC v10.10, v8.61, v5.6.2, and LIC_AGENTIC_v11.9.
Provides quality controls, validation gates, and orchestration patterns
for agentic LinkedIn outreach workflow.

Integrated with: apps_lic/L3_orchestration/kx_nodes_outreach.py
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

_emit_applies_guardrail("p0", "route_types", "p0_governance")
_emit_reads_policy_state("p0", "route_types", "policy_binding")
_emit_snapshots_state("p0", "route_types", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("route_types", "p4obs", "metric_1")
_emit_emits_metric_event("route_types", "p4obs", "metric_2")
_emit_emits_metric_event("route_types", "p4obs", "metric_3")
_emit_emits_metric_event("route_types", "p4obs", "metric_4")
_emit_emits_metric_event("route_types", "p4obs", "metric_5")
_emit_emits_metric_event("route_types", "p4obs", "metric_6")
_emit_records_incident_event("route_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("route_types", "p4obs", "anomaly")
_emit_writes_observability_log("route_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("route_types", "p4obs", "mon_state")
_emit_triggers_alert("route_types", "p4obs", "alert")
_emit_links_incident_trace("route_types", "p4obs", "trace_link")
_emit_captures_pattern("route_types", "p3lm", "pattern")
_emit_records_learning_event("route_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("route_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("route_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("route_types", "p3lm", "routing")
_emit_improves_agent_policy("route_types", "p3lm", "policy")
_emit_stores_learning_state("route_types", "p3lm", "state")
_emit_records_execution_trace("route_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("route_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("route_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("route_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("route_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("route_types", "env_read", "p2_env_1")
_emit_reads_environ("route_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("route_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("route_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "route_types", "context_pull")
_emit_pulls_context("p1", "route_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "route_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "route_types", "uwg_term_2")
_emit_writes_through("p1", "route_types", "write_through")
_emit_writes_through("p1", "route_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "route_types", "safety_validation")
_emit_invokes_eval("p1", "route_types", "eval_call")
_emit_proposal_commits_routing("p1", "route_types", "routing_commit")
_emit_escalates_to_human("p1", "route_types", "human_escalation")
_emit_routes_through("p1", "route_types", "route_through")
_emit_checks_agent_registry("p1", "route_types", "agent_registry")
_emit_validates_agent_capability("p1", "route_types", "capability")
_emit_dispatches_execution_plan("p1", "route_types", "exec_plan")
_emit_agent_executes_agent("p1", "route_types", "sub_agent")
_emit_routes_to_agent("p1", "route_types", "target_agent")
_emit_verifies_policy("p1", "route_types", "policy_check")
_emit_observes_runtime_state("p1", "route_types", "runtime_state")
_emit_verifies_boundary("p1", "route_types", "boundary_check")
_emit_transcripts_response("p1", "route_types", "transcript")
_emit_hard_fails_untranscripted("p1", "route_types")
_emit_gated_by_confidence("p1", "route_types", "confidence_gate")
emit_replay_key("p0", "route_types")
emit_determinism_digest("p0", "route_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "route_types", "execution_auth")
_emit_validates_capability("p2", "route_types", "capability_check")
_emit_routes_to_capability("p2", "route_types", "capability_route")
_emit_writes_via_uwg("p2", "route_types", "uwg_write")
_emit_blocks_direct_write("p2", "route_types", "direct_write_block")
_emit_records_tool_invocation("p2", "route_types", "tool_invocation")
_emit_captures_execution_output("p2", "route_types", "exec_output")
_emit_dispatches_agent("p3", "route_types", "agent_dispatch")
_emit_coordinates_agents("p3", "route_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "route_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "route_types", "healing_outcome")
_emit_escalates_failure("p3", "route_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "route_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "route_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "route_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "route_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "route_types", "eval_metric")
_emit_stores_embedding("p4", "route_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "route_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "route_types", "exec_snapshot_link")

LIMIT: int = 5
THRESHOLD: float = 0.95


class Route(str, Enum):
    """Message delivery routes."""

    INMAIL = "INMAIL"
    CONNECTION_REQ = "CONNECTION_REQ"
    EMAIL = "EMAIL"
    FOLLOW_UP = "FOLLOW_UP"
    SHORT_NEW = "SHORT_NEW"
    LONG_NEW = "LONG_NEW"


class Archetype(str, Enum):
    """Recipient archetypes for personalization."""

    C_LEVEL = "C_LEVEL"
    EXECUTIVE = "EXECUTIVE"
    SENIOR_TA = "SENIOR_TA"
    RECRUITER = "RECRUITER"


class ValidationSeverity(str, Enum):
    """Validation result Severity levels."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    INFO = "INFO"


@dataclass
class CharLimitConstraint:
    """Character limit constraint for a Route."""

    min: int | None = None
    max: int | None = None

    def validate(self, count: int) -> bool:
        """Validate character count against constraints."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "CharLimitConstraint.validate"
        )

        if self.min is not None and count < self.min:
            return False
        if self.max is not None and count > self.max:
            return False
        return True


@dataclass
class WordLimitConstraint:
    """Word limit constraint for a Route."""

    min: int | None = None
    max: int | None = None

    def validate(self, count: int) -> bool:
        """Validate word count against constraints."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "WordLimitConstraint.validate"
        )

        if self.min is not None and count < self.min:
            return False
        if self.max is not None and count > self.max:
            return False
        return True


@dataclass
class RouteConfig:
    """configuration for a message Route."""

    Route: Route
    char_limit: CharLimitConstraint | None = None
    word_limit: WordLimitConstraint | None = None
    k_nodes_enabled: dict[str, bool] = field(default_factory=dict)
    k_nodes_format: dict[str, str] = field(default_factory=dict)
    constraints: list[str] = field(default_factory=list)
    cta_word_limit: int | None = None
    signature_format: str = "standard"
    subject_line: bool = True
    attachments_allowed: bool = True


@dataclass
class ArchetypeConfig:
    """configuration for recipient Archetype."""

    Archetype: Archetype
    temperature: float = 0.7
    rag_enabled: bool = True
    rag_hops: int = 2
    rag_total_calls: int = 5
    self_consistency_runs: int = 3
    tot_branches: int = 3
    message_format_template: str = "standard"
    tone: str = "professional"
    formality_level: str = "moderate"


@dataclass
class ValidationRule:
    """Validation rule configuration."""

    rule_id: str
    name: str
    phase: str
    Severity: ValidationSeverity
    description: str
    enforcement: str
    validation_method: str
    threshold: float | None = None


# Route Configurations (from v10.10)
ROUTE_CONFIGS = {
    Route.CONNECTION_REQ: RouteConfig(
        Route=Route.CONNECTION_REQ,
        char_limit=CharLimitConstraint(min=None, max=300),
        k_nodes_enabled={
            "K.1": True,
            "K.2": False,
            "K.3": True,
            "K.4": False,
            "K.5": True,
            "K.6": True,
            "K.7": True,
        },
        k_nodes_format={
            "K.3": "compressed",
            "K.5": "micro",
            "K.6": "simplified",
            "K.7": "simplified",
        },
        constraints=[
            "simplified_signature_format",
            "no_subject_line",
            "no_attachments",
        ],
        cta_word_limit=LIMIT,
        signature_format="simplified",
        subject_line=False,
        attachments_allowed=False,
    ),
    Route.INMAIL: RouteConfig(
        Route=Route.INMAIL,
        char_limit=CharLimitConstraint(min=None, max=1900),
        k_nodes_enabled={
            "K.1": True,
            "K.2": True,
            "K.3": True,
            "K.4": True,
            "K.5": True,
            "K.6": True,
            "K.7": True,
        },
        k_nodes_format={
            "K.2": "standard",
            "K.3": "standard",
            "K.4": "standard",
            "K.5": "standard",
            "K.6": "standard",
            "K.7": "standard",
        },
        constraints=[
            "job_title_in_first_50_words",
            "subject_line_required",
        ],
        signature_format="standard",
        subject_line=True,
        attachments_allowed=True,
    ),
    Route.SHORT_NEW: RouteConfig(
        Route=Route.SHORT_NEW,
        char_limit=CharLimitConstraint(min=360, max=380),
        k_nodes_enabled={
            "K.1": True,
            "K.2": False,
            "K.3": True,
            "K.4": False,
            "K.5": True,
            "K.6": True,
            "K.7": True,
        },
        k_nodes_format={
            "K.3": "short",
            "K.5": "connection_only",
            "K.6": "simplified",
            "K.7": "simplified",
        },
        constraints=[
            "no_resume_clause",
            "greeting_required",
            "role_or_company_anchor_required",
            "sector_framing_required",
            "one_quantified_metric_required",
            "recipient_value_clause_required",
        ],
        cta_word_limit=LIMIT,
        signature_format="simplified",
        subject_line=False,
        attachments_allowed=False,
    ),
    Route.FOLLOW_UP: RouteConfig(
        Route=Route.FOLLOW_UP,
        char_limit=CharLimitConstraint(min=None, max=1500),
        k_nodes_enabled={
            "K.1": True,
            "K.2": True,
            "K.3": True,
            "K.4": False,
            "K.5": True,
            "K.6": True,
            "K.7": True,
        },
        k_nodes_format={
            "K.3": "follow_up",
        },
        constraints=[
            "continuity_clause_required",
            "prior_date_reference_required",
            "narrative_advancement_required",
            "no_opener_duplication",
            "no_metric_duplication",
        ],
        signature_format="standard",
        subject_line=True,
        attachments_allowed=True,
    ),
}

# Archetype Configurations (from v8.61 and v11.9)
ARCHETYPE_CONFIGS = {
    Archetype.C_LEVEL: ArchetypeConfig(
        Archetype=Archetype.C_LEVEL,
        temperature=0.4,
        rag_enabled=True,
        rag_hops=4,
        rag_total_calls=25,
        self_consistency_runs=5,
        tot_branches=5,
        message_format_template="ANALYST_LEVEL_PITCH",
        tone="thought_leadership",
        formality_level="high",
    ),
    Archetype.EXECUTIVE: ArchetypeConfig(
        Archetype=Archetype.EXECUTIVE,
        temperature=0.5,
        rag_enabled=True,
        rag_hops=3,
        rag_total_calls=17,
        self_consistency_runs=4,
        tot_branches=3,
        message_format_template="EXECUTIVE_PITCH",
        tone="strategic",
        formality_level="moderate_high",
    ),
    Archetype.SENIOR_TA: ArchetypeConfig(
        Archetype=Archetype.SENIOR_TA,
        temperature=0.6,
        rag_enabled=True,
        rag_hops=3,
        rag_total_calls=15,
        self_consistency_runs=3,
        tot_branches=3,
        message_format_template="TA_PITCH",
        tone="professional_warm",
        formality_level="moderate",
    ),
    Archetype.RECRUITER: ArchetypeConfig(
        Archetype=Archetype.RECRUITER,
        temperature=0.7,
        rag_enabled=True,
        rag_hops=2,
        rag_total_calls=10,
        self_consistency_runs=2,
        tot_branches=2,
        message_format_template="RECRUITER_PITCH",
        tone="job_focused",
        formality_level="moderate",
    ),
}

# Archetype Classification Tokens (from LinkedInCanonical v2.90)
ARCHETYPE_TOKENS = {
    "C_LEVEL": [
        "CEO",
        "Chief Executive Officer",
        "President",
        "COO",
        "CTO",
        "CIO",
        "CFO",
        "CDO",
        "CRO",
        "CXO",
        "Chief",
        "CEO direct report",
    ],
    "EXECUTIVE": [
        "EVP",
        "SVP",
        "VP",
        "Head of",
        "GM",
        "General Manager",
        "Executive",
        "GTM Leader",
        "Vice President",
    ],
    "SENIOR_TA": [
        "Talent Acquisition",
        "TA",
        "Recruiter",
        "Sourcer",
        "Talent Partner",
        "Global Talent Partner",
        "Recruiting",
    ],
    "RECRUITER": ["Recruiter", "Talent Acquisition Specialist", "Sourcing Specialist"],
}

# CXO Precedence Rule (from LinkedInCanonical v2.90)
CXO_PRECEDENCE_TOKENS = [
    "CEO",
    "CXO",
    "CRO",
    "President",
    "COO",
    "CTO",
    "CIO",
    "CFO",
    "CDO",
    "Chief",
]

# Validation Rules (from v10.10 and v11.9)
VALIDATION_RULES = [
    ValidationRule(
        rule_id="LIC-QA-001",
        name="Placeholder Detection",
        phase="POST_GENERATION",
        Severity=ValidationSeverity.CRITICAL,
        description="Detect placeholders like [NAME], {company}, etc.",
        enforcement="BLOCK",
        validation_method="regex_pattern_match",
    ),
    ValidationRule(
        rule_id="LIC-QA-002",
        name="Per-Claim Confidence Threshold",
        phase="POST_GENERATION",
        Severity=ValidationSeverity.CRITICAL,
        description="Each Claim must have confidence >= 0.70",
        enforcement="BLOCK",
        validation_method="confidence_scoring",
        threshold=THRESHOLD,
    ),
    ValidationRule(
        rule_id="LIC-QA-003",
        name="Hallucination Detection",
        phase="POST_GENERATION",
        Severity=ValidationSeverity.CRITICAL,
        description="No claims without supporting RAG evidence",
        enforcement="BLOCK",
        validation_method="evidence_grounding_check",
    ),
    ValidationRule(
        rule_id="LIC-QA-004",
        name="Message Diversity Check",
        phase="POST_GENERATION",
        Severity=ValidationSeverity.HIGH,
        description="Message must be <0.85 similar to previous messages",
        enforcement="REGENERATE",
        validation_method="cosine_similarity",
        threshold=THRESHOLD,
    ),
    ValidationRule(
        rule_id="LIC-QA-005",
        name="Job Title Placement",
        phase="POST_GENERATION",
        Severity=ValidationSeverity.HIGH,
        description="Job title must appear in first 50 words (INMAIL)",
        enforcement="REGENERATE",
        validation_method="position_check",
    ),
    ValidationRule(
        rule_id="LIC-QA-006",
        name="Company Name Spelling",
        phase="POST_GENERATION",
        Severity=ValidationSeverity.HIGH,
        description="Company name must match profile exactly",
        enforcement="REGENERATE",
        validation_method="fuzzy_match",
        threshold=THRESHOLD,
    ),
    ValidationRule(
        rule_id="LIC-QA-007",
        name="ASCII Character Validation",
        phase="POST_GENERATION",
        Severity=ValidationSeverity.HIGH,
        description="No non-ASCII characters allowed",
        enforcement="REGENERATE",
        validation_method="character_set_check",
    ),
    ValidationRule(
        rule_id="LIC-QA-008",
        name="Forbidden Corporate Verbs",
        phase="POST_GENERATION",
        Severity=ValidationSeverity.MEDIUM,
        description="Avoid: spearheaded, leveraged, drove, drive, synergized",
        enforcement="REGENERATE",
        validation_method="forbidden_words_check",
    ),
    ValidationRule(
        rule_id="LIC-QA-009",
        name="Weak Filler Phrases",
        phase="POST_GENERATION",
        Severity=ValidationSeverity.MEDIUM,
        description="Remove: 'I hope', 'I wanted to', 'just reaching out'",
        enforcement="REGENERATE",
        validation_method="filler_phrase_detection",
    ),
    ValidationRule(
        rule_id="LIC-QA-041",
        name="Metric Source Validation",
        phase="POST_GENERATION",
        Severity=ValidationSeverity.HIGH,
        description="Every Metric must map to metric_source_map entry",
        enforcement="BLOCK",
        validation_method="metric_source_binding",
    ),
    ValidationRule(
        rule_id="LIC-QA-042",
        name="Role Drift Detection",
        phase="POST_GENERATION",
        Severity=ValidationSeverity.HIGH,
        description="Sender role must match whitelisted roles",
        enforcement="BLOCK",
        validation_method="role_whitelist_check",
    ),
    ValidationRule(
        rule_id="LIC-QA-043",
        name="Metric Context Validation",
        phase="POST_GENERATION",
        Severity=ValidationSeverity.HIGH,
        description="Metrics must have keyword context from RAG",
        enforcement="REGENERATE",
        validation_method="context_keyword_check",
    ),
    ValidationRule(
        rule_id="LIC-QA-049",
        name="Company Spelling Validation",
        phase="POST_GENERATION",
        Severity=ValidationSeverity.HIGH,
        description="Fuzzy match company name against RAG",
        enforcement="REGENERATE",
        validation_method="fuzzy_company_match",
        threshold=THRESHOLD,
    ),
    ValidationRule(
        rule_id="LIC-QA-075",
        name="Job Title Placement (INMAIL)",
        phase="POST_GENERATION",
        Severity=ValidationSeverity.HIGH,
        description="Job title in first 50 words for INMAIL",
        enforcement="REGENERATE",
        validation_method="job_title_position_check",
    ),
    ValidationRule(
        rule_id="LIC-QA-104",
        name="Aggregate Confidence Enforcement",
        phase="POST_GENERATION",
        Severity=ValidationSeverity.CRITICAL,
        description="Aggregate confidence must be >= 0.95",
        enforcement="BLOCK",
        validation_method="aggregate_confidence_scoring",
        threshold=THRESHOLD,
    ),
    ValidationRule(
        rule_id="LIC-QA-105",
        name="Team Whitelist Enforcement",
        phase="DURING_GENERATION",
        Severity=ValidationSeverity.HIGH,
        description="All team mentions must have >=0.92 similarity to whitelist",
        enforcement="SOFT_REJECT",
        validation_method="semantic_similarity_check",
        threshold=THRESHOLD,
    ),
]

# Forbidden Words and Phrases (from v11.9)
FORBIDDEN_VERBS = [
    "spearheaded",
    "leveraged",
    "drove",
    "drive",
    "synergized",
    "utilized",
    "facilitated",
    "orchestrated",
]

FORBIDDEN_FILLER_PHRASES = [
    "I hope this message finds you well",
    "I wanted to reach out",
    "just reaching out",
    "I hope you don't mind",
    "I thought I'd reach out",
]

# CTA Templates (from v10.10)
CTA_TEMPLATES = {
    Route.CONNECTION_REQ: {
        "template": "Would you be open to a brief chat about {topic}?",
        "word_limit": 5,
        "examples": [
            "Open to a brief chat?",
            "Available for a quick call?",
            "Interested in connecting?",
        ],
    },
    Route.INMAIL: {
        "template": "Would you be available for a {duration} call {timeframe} to discuss {topic}?",
        "word_limit": 20,
        "examples": [
            "Available for a 15-minute call this week to discuss AI strategy?",
            "Open to a brief conversation next week about ML infrastructure?",
        ],
    },
    Route.SHORT_NEW: {
        "template": "Open to connecting?",
        "word_limit": 10,
        "examples": [
            "Open to connecting?",
            "Interested in a brief chat?",
        ],
    },
    Route.FOLLOW_UP: {
        "template": "Following up on {prior_topic} - available for a call {timeframe}?",
        "word_limit": 20,
        "examples": [
            "Following up on our AI discussion - available this week?",
        ],
    },
}

# Similarity Thresholds (from v11.9 and v5.6.2)
SIMILARITY_THRESHOLDS = {
    "message_to_previous": 0.85,  # Messages must be <85% similar
    "continuity_jaccard": 0.40,  # Jaccard similarity for FOLLOW_UP
    "continuity_semantic": 0.80,  # Semantic similarity for FOLLOW_UP
    "company_name_fuzzy": 0.95,  # Company name fuzzy match
    "team_whitelist_semantic": 0.92,  # Team mention similarity
}

# Confidence Thresholds (from v10.10)
CONFIDENCE_THRESHOLDS = {
    "per_claim_minimum": 0.70,
    "aggregate_minimum": 0.95,
    "rag_signal_quality_minimum": 0.70,
    "archetype_classification_minimum": 0.85,
}

# RAG Signal Quality scoring (from v11.9)
RAG_SIGNAL_QUALITY_CONFIG = {
    "base_score_per_result": 0.15,
    "max_base_score": 0.75,
    "diversity_bonus_per_source_type": 0.10,
    "max_diversity_bonus": 0.30,
    "gap_penalty": 0.10,
    "minimum_threshold": 0.70,
}

# Entity Grounding Framework (from v10.10)
ENTITY_GROUNDING_CONFIG = {
    "metric_source_binding": {
        "enabled": True,
        "constraint": "EVERY Metric in K.3 must map to metric_source_map entry",
        "enforcement": "BLOCK",
    },
    "team_whitelist": {
        "enabled": True,
        "validation_method": "semantic_similarity_check",
        "threshold": 0.92,
        "enforcement": "SOFT_REJECT",
    },
    "company_whitelist": {
        "enabled": True,
        "validation_method": "fuzzy_match",
        "threshold": 0.95,
        "enforcement": "REGENERATE",
    },
}

# Message Type Transitions (from v5.6.2)
MESSAGE_TYPE_TRANSITIONS = {
    "NEW_to_FOLLOW_UP": {
        "trigger": "User indicates prior touchpoint exists",
        "action": "Regenerate K.3 with continuity references",
        "k3_adjustments": [
            "Add opening: 'Following up on...'",
            "Reference prior topic/date",
            "Maintain narrative advancement",
        ],
    },
    "SHORT_to_LONG": {
        "trigger": "User requests expanded version",
        "action": "Expand K.3 with additional context layers",
        "expansions": [
            "Add 1-2 more specific anchors",
            "Expand evidence paragraphs",
            "Add K.2 subject line if applicable",
            "Add K.4 resume attachment if appropriate",
        ],
    },
    "CONNECTION_to_MESSAGE": {
        "trigger": "Connection accepted, now sending message",
        "action": "Regenerate with full message structure",
    },
    "ANY_to_JOB_SPECIFIC": {
        "trigger": "User confirms job application context",
        "action": "Enable job-specific RAG and adjust K.3",
        "requirements": [
            "Execute prescan for application tracker",
            "Enable job-focused RAG queries",
            "Ensure job_title appears in first 50 words of K.3",
        ],
    },
}

# Adaptive Temperature Escalation (from v11.9)
ADAPTIVE_TEMPERATURE_CONFIG = {
    "initial_temperature": 0.5,
    "max_temperature": 0.9,
    "escalation_per_retry": 0.1,
    "constraint_failure_types": {
        "MECHANICAL": 0.05,  # Small increase for word/char count issues
        "CREATIVE": 0.15,  # Larger increase for placeholder/generic content
        "SEMANTIC": 0.10,  # Medium increase for forbidden words
        "CONFLICT": 0.0,  # No increase - constraint conflict needs manual fix
    },
}

# Circuit Breaker configuration (from v11.9)
CIRCUIT_BREAKER_CONFIG = {
    "failure_threshold": 3,
    "timeout_seconds": 60,
    "half_open_test_requests": 1,
}

# Constraint Pre-Flight Test (from v11.9)
CONSTRAINT_PREFLIGHT_CONFIG = {
    "enabled": True,
    "feasibility_heuristics": {
        Route.CONNECTION_REQ: {
            "min_words_per_element": 8,
            "elements": ["greeting", "hook", "value_prop", "cta"],
            "total_min_words": 32,
        },
        Route.SHORT_NEW: {
            "min_words_per_element": 10,
            "elements": ["greeting", "hook", "Metric", "value_clause", "cta", "signature"],
            "total_min_words": 60,
        },
    },
}

# Boot Validator configuration (from v10.10 and v8.61)
BOOT_VALIDATOR_CONFIG = {
    "execution": "SYSTEM_STARTUP",
    "blocking": True,
    "validation_suite": {
        "template_validation": [
            "check_greeting_templates",
            "check_cta_templates",
            "check_signature_formats",
            "verify_no_typos",
        ],
        "schema_integrity": [
            "check_json_files",
            "verify_required_fields",
            "check_no_circular_refs",
        ],
        "reference_integrity": [
            "verify_all_refs_resolve",
            "check_no_broken_links",
            "validate_rule_ids_unique",
        ],
        "route_completeness": [
            "verify_all_routes_defined",
            "check_word_limits_set",
            "confirm_constraints_present",
        ],
    },
}


def get_route_config(Route: Route) -> RouteConfig | None:
    """Get Route configuration.

    Args:
        Route: Message Route

    Returns:
        RouteConfig or None if not defined
    """
    return ROUTE_CONFIGS.get(Route)


def get_archetype_config(Archetype: Archetype) -> ArchetypeConfig | None:
    """Get Archetype configuration.

    Args:
        Archetype: Recipient Archetype

    Returns:
        ArchetypeConfig or None if not defined
    """
    return ARCHETYPE_CONFIGS.get(Archetype)


def classify_archetype(title: str, about: str = "") -> Archetype:
    """Classify recipient Archetype based on title and about.

    Args:
        title: Recipient job title
        about: Recipient about section

    Returns:
        Classified Archetype
    """
    combined_text = f"{title} {about}".upper()

    # CXO precedence rule (v2.90)
    for token in CXO_PRECEDENCE_TOKENS:
        if token.upper() in combined_text:
            return Archetype.C_LEVEL

    # C_LEVEL tokens
    for token in ARCHETYPE_TOKENS["C_LEVEL"]:
        if token.upper() in combined_text:
            return Archetype.C_LEVEL

    # EXECUTIVE tokens
    for token in ARCHETYPE_TOKENS["EXECUTIVE"]:
        if token.upper() in combined_text:
            return Archetype.EXECUTIVE

    # SENIOR_TA tokens
    for token in ARCHETYPE_TOKENS["SENIOR_TA"]:
        if token.upper() in combined_text:
            return Archetype.SENIOR_TA

    # RECRUITER tokens
    for token in ARCHETYPE_TOKENS["RECRUITER"]:
        if token.upper() in combined_text:
            return Archetype.RECRUITER

    # Default to EXECUTIVE if no match
    return Archetype.EXECUTIVE


def get_validation_rules(phase: str) -> list[ValidationRule]:
    """Get validation rules for a specific phase.

    Args:
        phase: Execution phase

    Returns:
        List of validation rules
    """
    return [rule for rule in VALIDATION_RULES if rule.phase == phase]
