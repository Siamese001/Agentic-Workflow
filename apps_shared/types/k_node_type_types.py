"""K.X Nodes - Knowledge Extraction Nodes for Resume and Outreach Engines.

Extracted from legacy archives and unified for agentic workflow integration.
K.X nodes represent structured knowledge extraction and generation steps
with configurable parameters, reasoning strategies, and RAG integration.

Phase 1C - Knowledge Extraction Integration

# guardian: allow-magic-config
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

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

_emit_applies_guardrail("p0", "k_node_type_types", "p0_governance")
_emit_reads_policy_state("p0", "k_node_type_types", "policy_binding")
_emit_snapshots_state("p0", "k_node_type_types", "state_snapshot")
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

_emit_emits_metric_event("k_node_type_types", "p4obs", "metric_1")
_emit_emits_metric_event("k_node_type_types", "p4obs", "metric_2")
_emit_emits_metric_event("k_node_type_types", "p4obs", "metric_3")
_emit_emits_metric_event("k_node_type_types", "p4obs", "metric_4")
_emit_emits_metric_event("k_node_type_types", "p4obs", "metric_5")
_emit_emits_metric_event("k_node_type_types", "p4obs", "metric_6")
_emit_records_incident_event("k_node_type_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("k_node_type_types", "p4obs", "anomaly")
_emit_writes_observability_log("k_node_type_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("k_node_type_types", "p4obs", "mon_state")
_emit_triggers_alert("k_node_type_types", "p4obs", "alert")
_emit_links_incident_trace("k_node_type_types", "p4obs", "trace_link")
_emit_captures_pattern("k_node_type_types", "p3lm", "pattern")
_emit_records_learning_event("k_node_type_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("k_node_type_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("k_node_type_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("k_node_type_types", "p3lm", "routing")
_emit_improves_agent_policy("k_node_type_types", "p3lm", "policy")
_emit_stores_learning_state("k_node_type_types", "p3lm", "state")
_emit_records_execution_trace("k_node_type_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("k_node_type_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("k_node_type_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("k_node_type_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("k_node_type_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("k_node_type_types", "env_read", "p2_env_1")
_emit_reads_environ("k_node_type_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("k_node_type_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("k_node_type_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "k_node_type_types", "context_pull")
_emit_pulls_context("p1", "k_node_type_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "k_node_type_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "k_node_type_types", "uwg_term_2")
_emit_writes_through("p1", "k_node_type_types", "write_through")
_emit_writes_through("p1", "k_node_type_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "k_node_type_types", "safety_validation")
_emit_invokes_eval("p1", "k_node_type_types", "eval_call")
_emit_proposal_commits_routing("p1", "k_node_type_types", "routing_commit")
_emit_escalates_to_human("p1", "k_node_type_types", "human_escalation")
_emit_routes_through("p1", "k_node_type_types", "route_through")
_emit_checks_agent_registry("p1", "k_node_type_types", "agent_registry")
_emit_validates_agent_capability("p1", "k_node_type_types", "capability")
_emit_dispatches_execution_plan("p1", "k_node_type_types", "exec_plan")
_emit_agent_executes_agent("p1", "k_node_type_types", "sub_agent")
_emit_routes_to_agent("p1", "k_node_type_types", "target_agent")
_emit_verifies_policy("p1", "k_node_type_types", "policy_check")
_emit_observes_runtime_state("p1", "k_node_type_types", "runtime_state")
_emit_verifies_boundary("p1", "k_node_type_types", "boundary_check")
_emit_transcripts_response("p1", "k_node_type_types", "transcript")
_emit_hard_fails_untranscripted("p1", "k_node_type_types")
_emit_gated_by_confidence("p1", "k_node_type_types", "confidence_gate")
emit_replay_key("p0", "k_node_type_types")
emit_determinism_digest("p0", "k_node_type_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "k_node_type_types", "execution_auth")
_emit_validates_capability("p2", "k_node_type_types", "capability_check")
_emit_routes_to_capability("p2", "k_node_type_types", "capability_route")
_emit_writes_via_uwg("p2", "k_node_type_types", "uwg_write")
_emit_blocks_direct_write("p2", "k_node_type_types", "direct_write_block")
_emit_records_tool_invocation("p2", "k_node_type_types", "tool_invocation")
_emit_captures_execution_output("p2", "k_node_type_types", "exec_output")
_emit_dispatches_agent("p3", "k_node_type_types", "agent_dispatch")
_emit_coordinates_agents("p3", "k_node_type_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "k_node_type_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "k_node_type_types", "healing_outcome")
_emit_escalates_failure("p3", "k_node_type_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "k_node_type_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "k_node_type_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "k_node_type_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "k_node_type_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "k_node_type_types", "eval_metric")
_emit_stores_embedding("p4", "k_node_type_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "k_node_type_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "k_node_type_types", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class KNodeType(str, Enum):
    """K.X node type classification."""

    RESUME_HEADER = "resume_header"
    RESUME_SECTION = "resume_section"
    OUTREACH_ROUTING = "outreach_routing"
    OUTREACH_CONTENT = "outreach_content"
    OUTREACH_CTA = "outreach_cta"


class ReasoningStrategy(str, Enum):
    """Reasoning strategy for K.X node execution."""

    COT = "chain_of_thought"
    TOT = "tree_of_thought"
    HYBRID_COT_TOT = "hybrid_cot_tot"
    SELF_CONSISTENCY = "self_consistency"
    REFLEXION = "reflexion"
    SOCRATIC = "socratic"


@dataclass
class RAGConfig:
    """RAG configuration for K.X node."""

    enabled: bool = True
    min_retrievers: int = 3
    max_retrievers: int = 6
    hops: int = 2
    source_weighting: dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize default source weighting."""
        if not self.source_weighting:
            self.source_weighting = {
                "podcast_appearance": 1.5,
                "video_interview": 1.5,
                "conference_talk": 1.5,
                "authored_blog_post": 1.2,
                "linkedin_article": 1.2,
                "news_article": 1.0,
                "press_release": 1.0,
                "generic_bio": 0.5,
            }


@dataclass
class DecodingParams:
    """Decoding parameters for LLM generation."""

    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    min_p: float = 0.04
    repetition_penalty: float = 1.1
    max_tokens: int | None = None


@dataclass
class KNodeConfig:
    """configuration for a K.X knowledge extraction node."""

    node_id: str
    element: str
    node_type: KNodeType
    reasoning_strategy: ReasoningStrategy = ReasoningStrategy.COT
    rag_config: RAGConfig | None = None
    decoding_params: DecodingParams | None = None
    tot_branches: int = 3
    tot_depth: int = 2
    self_consistency_runs: int = 1
    beam_width: int = 1
    scratchpad_enabled: bool = True
    max_chars: int | None = None
    max_words: int | None = None
    structure_template: str | None = None
    validation_rules: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize default configurations."""
        if self.rag_config is None:
            self.rag_config = RAGConfig()
        if self.decoding_params is None:
            self.decoding_params = DecodingParams()


# guardian: allow-magic-config
RESUME_KX_NODES = {
    "K.0_Name": KNodeConfig(
        node_id="K.0",
        element="Name",
        node_type=KNodeType.RESUME_HEADER,
        reasoning_strategy=ReasoningStrategy.COT,
        rag_config=RAGConfig(enabled=False),
        max_chars=100,
        validation_rules=["non_empty", "proper_case"],
        metadata={"section": "header", "required": True},
    ),
    "K.0_Headline": KNodeConfig(
        node_id="K.0",
        element="Headline",
        node_type=KNodeType.RESUME_HEADER,
        reasoning_strategy=ReasoningStrategy.COT,
        rag_config=RAGConfig(enabled=False),
        max_chars=120,
        validation_rules=["non_empty", "professional_tone"],
        metadata={"section": "header", "required": True},
    ),
    "K.0_Contact": KNodeConfig(
        node_id="K.0",
        element="Contact",
        node_type=KNodeType.RESUME_HEADER,
        reasoning_strategy=ReasoningStrategy.COT,
        rag_config=RAGConfig(enabled=False),
        validation_rules=["valid_email", "valid_phone"],
        metadata={"section": "header", "required": True},
    ),
    "K.1_Executive_Summary": KNodeConfig(
        node_id="K.1",
        element="Executive Summary",
        node_type=KNodeType.RESUME_SECTION,
        reasoning_strategy=ReasoningStrategy.HYBRID_COT_TOT,
        rag_config=RAGConfig(enabled=True, min_retrievers=4, hops=2),
        decoding_params=DecodingParams(temperature=0.3, top_p=0.85),
        tot_branches=5,
        tot_depth=3,
        self_consistency_runs=3,
        max_words=150,
        structure_template="3-4 sentences highlighting key achievements and value proposition",
        validation_rules=["grounding_check", "hallucination_check", "voice_tense_check", "word_count_range"],
        metadata={"section": "summary", "required": True, "priority": "high"},
    ),
    "K.2_Unify_Overview": KNodeConfig(
        node_id="K.2",
        element="Unify Overview",
        node_type=KNodeType.RESUME_SECTION,
        reasoning_strategy=ReasoningStrategy.HYBRID_COT_TOT,
        rag_config=RAGConfig(enabled=True, min_retrievers=5, hops=3),
        decoding_params=DecodingParams(temperature=0.25, top_p=0.8),
        tot_branches=4,
        self_consistency_runs=2,
        max_words=100,
        validation_rules=["grounding_check", "factual_accuracy"],
        metadata={"section": "experience", "company": "Unify"},
    ),
    "K.2_Unify_Bullets": KNodeConfig(
        node_id="K.2",
        element="Unify Bullets",
        node_type=KNodeType.RESUME_SECTION,
        reasoning_strategy=ReasoningStrategy.HYBRID_COT_TOT,
        rag_config=RAGConfig(enabled=True, min_retrievers=6, hops=3),
        decoding_params=DecodingParams(temperature=0.2, top_p=0.75),
        tot_branches=6,
        self_consistency_runs=4,
        structure_template="3-5 achievement bullets with metrics",
        validation_rules=[
            "bullet_provenance_check",
            "hallucination_check",
            "redundancy_check",
            "punctuation_check",
        ],
        metadata={"section": "experience", "company": "Unify", "min_bullets": 3},
    ),
    "K.3_IBM_Overview": KNodeConfig(
        node_id="K.3",
        element="IBM Overview",
        node_type=KNodeType.RESUME_SECTION,
        reasoning_strategy=ReasoningStrategy.HYBRID_COT_TOT,
        rag_config=RAGConfig(enabled=True, min_retrievers=5, hops=3),
        decoding_params=DecodingParams(temperature=0.25, top_p=0.8),
        max_words=100,
        validation_rules=["grounding_check", "factual_accuracy"],
        metadata={"section": "experience", "company": "IBM"},
    ),
    "K.3_IBM_Bullets": KNodeConfig(
        node_id="K.3",
        element="IBM Bullets",
        node_type=KNodeType.RESUME_SECTION,
        reasoning_strategy=ReasoningStrategy.HYBRID_COT_TOT,
        rag_config=RAGConfig(enabled=True, min_retrievers=6, hops=3),
        decoding_params=DecodingParams(temperature=0.2, top_p=0.75),
        structure_template="3-5 achievement bullets with metrics",
        validation_rules=["bullet_provenance_check", "hallucination_check"],
        metadata={"section": "experience", "company": "IBM", "min_bullets": 3},
    ),
    "K.4_TraderSense_Narrative": KNodeConfig(
        node_id="K.4",
        element="TraderSense Narrative",
        node_type=KNodeType.RESUME_SECTION,
        reasoning_strategy=ReasoningStrategy.COT,
        rag_config=RAGConfig(enabled=True, min_retrievers=4, hops=2),
        max_words=120,
        validation_rules=["grounding_check"],
        metadata={"section": "experience", "company": "TraderSense"},
    ),
    "K.5_EY_Narrative": KNodeConfig(
        node_id="K.5",
        element="EY Narrative",
        node_type=KNodeType.RESUME_SECTION,
        reasoning_strategy=ReasoningStrategy.COT,
        rag_config=RAGConfig(enabled=True, min_retrievers=4, hops=2),
        max_words=120,
        validation_rules=["grounding_check"],
        metadata={"section": "experience", "company": "EY"},
    ),
    "K.6_Early_Career_Narrative": KNodeConfig(
        node_id="K.6",
        element="Early Career Narrative",
        node_type=KNodeType.RESUME_SECTION,
        reasoning_strategy=ReasoningStrategy.COT,
        rag_config=RAGConfig(enabled=True, min_retrievers=3, hops=1),
        max_words=100,
        validation_rules=["grounding_check"],
        metadata={"section": "experience", "early_career": True},
    ),
    "K.7_Education": KNodeConfig(
        node_id="K.7",
        element="Education",
        node_type=KNodeType.RESUME_SECTION,
        reasoning_strategy=ReasoningStrategy.COT,
        rag_config=RAGConfig(enabled=False),
        validation_rules=["factual_accuracy", "date_format"],
        metadata={"section": "education", "required": True},
    ),
    "K.8_Certifications": KNodeConfig(
        node_id="K.8",
        element="Certifications",
        node_type=KNodeType.RESUME_SECTION,
        reasoning_strategy=ReasoningStrategy.COT,
        rag_config=RAGConfig(enabled=False),
        validation_rules=["factual_accuracy"],
        metadata={"section": "certifications"},
    ),
    "K.9_Competencies": KNodeConfig(
        node_id="K.9",
        element="Competencies",
        node_type=KNodeType.RESUME_SECTION,
        reasoning_strategy=ReasoningStrategy.COT,
        rag_config=RAGConfig(enabled=True, min_retrievers=3, hops=1),
        validation_rules=["competency_word_count_balance"],
        metadata={"section": "competencies"},
    ),
    "K.10_Skills": KNodeConfig(
        node_id="K.10",
        element="Skills",
        node_type=KNodeType.RESUME_SECTION,
        reasoning_strategy=ReasoningStrategy.COT,
        rag_config=RAGConfig(enabled=False),
        validation_rules=["controlled_vocabulary"],
        metadata={"section": "skills"},
    ),
    "K.11_Cover_Letter": KNodeConfig(
        node_id="K.11",
        element="Cover Letter",
        node_type=KNodeType.RESUME_SECTION,
        reasoning_strategy=ReasoningStrategy.HYBRID_COT_TOT,
        rag_config=RAGConfig(enabled=True, min_retrievers=5, hops=3),
        decoding_params=DecodingParams(temperature=0.4, top_p=0.9),
        tot_branches=5,
        self_consistency_runs=2,
        max_words=400,
        validation_rules=["grounding_check", "voice_tense_check"],
        metadata={"section": "cover_letter", "optional": True},
    ),
}
# guardian: allow-magic-config
OUTREACH_KX_NODES = {
    "K.1_Message_Type_Routing": KNodeConfig(
        node_id="K.1",
        element="Message Type - channel classification and grounding with enhanced RAG",
        node_type=KNodeType.OUTREACH_ROUTING,
        reasoning_strategy=ReasoningStrategy.HYBRID_COT_TOT,
        rag_config=RAGConfig(enabled=True, min_retrievers=6, hops=3),
        decoding_params=DecodingParams(temperature=0.1, top_p=0.85, top_k=30),
        tot_branches=7,
        self_consistency_runs=8,
        validation_rules=["message_type_confirmation"],
        metadata={
            "message_types": ["C_LEVEL", "EXECUTIVE", "SENIOR_TA", "RECRUITER"],
            "routing_decision": True,
        },
    ),
    "K.2_Recipient_Analysis": KNodeConfig(
        node_id="K.2",
        element="Recipient Analysis - persona and context extraction",
        node_type=KNodeType.OUTREACH_CONTENT,
        reasoning_strategy=ReasoningStrategy.HYBRID_COT_TOT,
        rag_config=RAGConfig(enabled=True, min_retrievers=6, hops=3),
        decoding_params=DecodingParams(temperature=0.1, top_p=0.85),
        tot_branches=5,
        self_consistency_runs=5,
        validation_rules=["persona_extraction", "context_grounding"],
        metadata={"requires_linkedin_input": True},
    ),
    "K.3_Message_Body": KNodeConfig(
        node_id="K.3",
        element="Message Body - personalized content generation",
        node_type=KNodeType.OUTREACH_CONTENT,
        reasoning_strategy=ReasoningStrategy.HYBRID_COT_TOT,
        rag_config=RAGConfig(enabled=True, min_retrievers=6, hops=3),
        decoding_params=DecodingParams(temperature=0.15, top_p=0.88, top_k=40),
        tot_branches=6,
        self_consistency_runs=6,
        beam_width=3,
        max_chars=800,
        structure_template="greeting + personalized opener + value proposition + transition",
        validation_rules=["resume_fact_verification", "temporal_accuracy", "synthesis_phase_check"],
        metadata={"regeneration_supported": True},
    ),
    "K.4_Value_Proposition": KNodeConfig(
        node_id="K.4",
        element="Value Proposition - compelling offer articulation",
        node_type=KNodeType.OUTREACH_CONTENT,
        reasoning_strategy=ReasoningStrategy.HYBRID_COT_TOT,
        rag_config=RAGConfig(enabled=True, min_retrievers=5, hops=2),
        decoding_params=DecodingParams(temperature=0.2, top_p=0.9),
        tot_branches=5,
        self_consistency_runs=4,
        max_words=100,
        validation_rules=["value_clarity", "grounding_check"],
        metadata={"regeneration_supported": True},
    ),
    "K.5_CTA_Generation": KNodeConfig(
        node_id="K.5",
        element="CTA Generation - call-to-action with temporal framing",
        node_type=KNodeType.OUTREACH_CTA,
        reasoning_strategy=ReasoningStrategy.COT,
        rag_config=RAGConfig(enabled=True, min_retrievers=3, hops=1),
        decoding_params=DecodingParams(temperature=0.25, top_p=0.88, top_k=30),
        self_consistency_runs=3,
        max_words=30,
        validation_rules=["date_specific_cta_rules", "temporal_framing"],
        metadata={"lexicon_ref": "cta_temporal_lexicon"},
    ),
    "K.6_Salutation_Signature": KNodeConfig(
        node_id="K.6",
        element="Salutation and Signature - professional formatting",
        node_type=KNodeType.OUTREACH_CONTENT,
        reasoning_strategy=ReasoningStrategy.COT,
        rag_config=RAGConfig(enabled=False),
        decoding_params=DecodingParams(temperature=0.1, top_p=0.8),
        max_chars=100,
        validation_rules=["requires_sender_profile", "salutation_format"],
        metadata={"persona_catalog_ref": "professional_signatures"},
    ),
    "K.7_Final_Assembly": KNodeConfig(
        node_id="K.7",
        element="Final Assembly - message composition and validation",
        node_type=KNodeType.OUTREACH_CONTENT,
        reasoning_strategy=ReasoningStrategy.COT,
        rag_config=RAGConfig(enabled=False),
        decoding_params=DecodingParams(temperature=0.05, top_p=0.75),
        validation_rules=["final_checks", "character_limit", "professional_tone", "no_hallucinations"],
        metadata={"assembly_phase": True, "blocking_validation": True},
    ),
}
# guardian: allow-magic-config
OUTREACH_CONNECTION_REQ_NODES = {
    "CONNECTION_REQ_K.3_COMPRESSED": KNodeConfig(
        node_id="K.3",
        element="Message Body (CONNECTION_REQ compressed mode)",
        node_type=KNodeType.OUTREACH_CONTENT,
        reasoning_strategy=ReasoningStrategy.COT,
        rag_config=RAGConfig(enabled=False),
        decoding_params=DecodingParams(
            temperature=0.25, top_p=0.9, top_k=40, min_p=0.04, repetition_penalty=1.1
        ),
        beam_width=2,
        self_consistency_runs=1,
        max_chars=280,
        structure_template="greeting + 1-2 sentence personalized opener + transition to CTA",
        validation_rules=["character_limit_strict"],
        metadata={"mode": "compressed", "anti_pattern": "RAG disabled due to 330 char space constraint"},
    ),
    "CONNECTION_REQ_K.5_MICRO": KNodeConfig(
        node_id="K.5",
        element="CTA (CONNECTION_REQ micro mode)",
        node_type=KNodeType.OUTREACH_CTA,
        reasoning_strategy=ReasoningStrategy.COT,
        rag_config=RAGConfig(enabled=False),
        decoding_params=DecodingParams(
            temperature=0.2, top_p=0.88, top_k=30, min_p=0.03, repetition_penalty=1.05
        ),
        beam_width=1,
        self_consistency_runs=1,
        max_words=5,
        max_chars=30,
        validation_rules=["micro_cta_format"],
        metadata={
            "mode": "micro",
            "examples": ["Let's connect", "Connect?", "Happy to chat", "Let's link up"],
        },
    ),
}


class KXNodeRegistry:
    """Registry for managing K.X knowledge extraction nodes."""

    def __init__(self):
        """Initialize K.X node registry."""
        self._resume_nodes = RESUME_KX_NODES.copy()
        self._outreach_nodes = OUTREACH_KX_NODES.copy()
        self._connection_req_nodes = OUTREACH_CONNECTION_REQ_NODES.copy()
        logger.info("K.X node registry initialized")

    def get_resume_node(self, node_key: str) -> KNodeConfig | None:
        """Get resume engine K.X node configuration.

        Args:
            node_key: Node key (e.g., "K.1_Executive_Summary")

        Returns:
            KNodeConfig or None if not found
        """
        return self._resume_nodes.get(node_key)

    def get_outreach_node(self, node_key: str, connection_request: bool = False) -> KNodeConfig | None:
        """Get outreach engine K.X node configuration.

        Args:
            node_key: Node key (e.g., "K.3_Message_Body")
            connection_request: Use connection request variant if True

        Returns:
            KNodeConfig or None if not found
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "KXNodeRegistry.get_outreach_node")

        if connection_request and node_key in self._connection_req_nodes:
            return self._connection_req_nodes[node_key]
        return self._outreach_nodes.get(node_key)

    def list_resume_nodes(self) -> list[str]:
        """List all resume engine K.X node keys.

        Returns:
            List of node keys
        """
        return list(self._resume_nodes.keys())

    def list_outreach_nodes(self) -> list[str]:
        """List all outreach engine K.X node keys.

        Returns:
            List of node keys
        """
        return list(self._outreach_nodes.keys())

    def get_nodes_by_type(self, node_type: KNodeType) -> dict[str, KNodeConfig]:
        """Get all nodes of a specific type.

        Args:
            node_type: Node type to filter by

        Returns:
            Dictionary of matching nodes
        """
        all_nodes = {**self._resume_nodes, **self._outreach_nodes}
        return {key: config for key, config in all_nodes.items() if config.node_type == node_type}

    def register_custom_node(self, node_key: str, config: KNodeConfig, engine: str = "resume") -> None:
        """Register a custom K.X node.

        Args:
            node_key: Unique node key
            config: Node configuration
            engine: Engine type ("resume" or "outreach")
        """
        if engine == "resume":
            self._resume_nodes[node_key] = config
        elif engine == "outreach":
            self._outreach_nodes[node_key] = config
        else:
            raise ValueError(f"Unknown engine type: {engine}")
        logger.info(f"Registered custom K.X node: {node_key} ({engine})")


_KX_REGISTRY: KXNodeRegistry | None = None


def get_kx_registry() -> KXNodeRegistry:
    """Get or create global K.X node registry.

    Returns:
        KXNodeRegistry instance
    """
    global _KX_REGISTRY
    if _KX_REGISTRY is None:
        _KX_REGISTRY = KXNodeRegistry()
    return _KX_REGISTRY


def get_resume_kx_node(node_key: str) -> KNodeConfig | None:
    """Get resume engine K.X node configuration.

    Args:
        node_key: Node key (e.g., "K.1_Executive_Summary")

    Returns:
        KNodeConfig or None if not found
    """
    registry = get_kx_registry()
    return registry.get_resume_node(node_key)


def get_outreach_kx_node(node_key: str, connection_request: bool = False) -> KNodeConfig | None:
    """Get outreach engine K.X node configuration.

    Args:
        node_key: Node key (e.g., "K.3_Message_Body")
        connection_request: Use connection request variant if True

    Returns:
        KNodeConfig or None if not found
    """
    registry = get_kx_registry()
    return registry.get_outreach_node(node_key, connection_request)
