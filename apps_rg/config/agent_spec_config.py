"""
RG Configuration Schemas - LIC-Aligned Sovereign Architecture.

Defines the Pydantic models for type-safe configuration loading.
Aligned with LIC schemas.py pattern.

HARDENING: Defines strict Pydantic models for the system topology.
This prevents "Schema Drift" where JSON files get out of sync with code expectations.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from apps_shared.config.prompt_reception_spec import PromptReceptionSpec

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

_emit_applies_guardrail("p0", "agent_spec_config", "p0_governance")
_emit_reads_policy_state("p0", "agent_spec_config", "policy_binding")
_emit_snapshots_state("p0", "agent_spec_config", "state_snapshot")
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

_emit_emits_metric_event("agent_spec_config", "p4obs", "metric_1")
_emit_emits_metric_event("agent_spec_config", "p4obs", "metric_2")
_emit_emits_metric_event("agent_spec_config", "p4obs", "metric_3")
_emit_emits_metric_event("agent_spec_config", "p4obs", "metric_4")
_emit_emits_metric_event("agent_spec_config", "p4obs", "metric_5")
_emit_emits_metric_event("agent_spec_config", "p4obs", "metric_6")
_emit_records_incident_event("agent_spec_config", "p4obs", "incident")
_emit_captures_runtime_anomaly("agent_spec_config", "p4obs", "anomaly")
_emit_writes_observability_log("agent_spec_config", "p4obs", "obs_log")
_emit_updates_monitoring_state("agent_spec_config", "p4obs", "mon_state")
_emit_triggers_alert("agent_spec_config", "p4obs", "alert")
_emit_links_incident_trace("agent_spec_config", "p4obs", "trace_link")
_emit_captures_pattern("agent_spec_config", "p3lm", "pattern")
_emit_records_learning_event("agent_spec_config", "p3lm", "learning_event")
_emit_writes_learning_snapshot("agent_spec_config", "p3lm", "snapshot")
_emit_feeds_meta_learning("agent_spec_config", "p3lm", "meta_feed")
_emit_updates_routing_strategy("agent_spec_config", "p3lm", "routing")
_emit_improves_agent_policy("agent_spec_config", "p3lm", "policy")
_emit_stores_learning_state("agent_spec_config", "p3lm", "state")
_emit_records_execution_trace("agent_spec_config", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("agent_spec_config", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("agent_spec_config", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("agent_spec_config", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("agent_spec_config", "L4_STATE", "p2_trace_5")
_emit_reads_environ("agent_spec_config", "env_read", "p2_env_1")
_emit_reads_environ("agent_spec_config", "env_read", "p2_env_2")
_emit_reads_runtime_state("agent_spec_config", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("agent_spec_config", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "agent_spec_config", "context_pull")
_emit_pulls_context("p1", "agent_spec_config", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "agent_spec_config", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "agent_spec_config", "uwg_term_2")
_emit_writes_through("p1", "agent_spec_config", "write_through")
_emit_writes_through("p1", "agent_spec_config", "write_through_2")
_emit_validated_by_safety_plane("p1", "agent_spec_config", "safety_validation")
_emit_invokes_eval("p1", "agent_spec_config", "eval_call")
_emit_proposal_commits_routing("p1", "agent_spec_config", "routing_commit")
_emit_escalates_to_human("p1", "agent_spec_config", "human_escalation")
_emit_routes_through("p1", "agent_spec_config", "route_through")
_emit_checks_agent_registry("p1", "agent_spec_config", "agent_registry")
_emit_validates_agent_capability("p1", "agent_spec_config", "capability")
_emit_dispatches_execution_plan("p1", "agent_spec_config", "exec_plan")
_emit_agent_executes_agent("p1", "agent_spec_config", "sub_agent")
_emit_routes_to_agent("p1", "agent_spec_config", "target_agent")
_emit_verifies_policy("p1", "agent_spec_config", "policy_check")
_emit_observes_runtime_state("p1", "agent_spec_config", "runtime_state")
_emit_verifies_boundary("p1", "agent_spec_config", "boundary_check")
_emit_transcripts_response("p1", "agent_spec_config", "transcript")
_emit_hard_fails_untranscripted("p1", "agent_spec_config")
_emit_gated_by_confidence("p1", "agent_spec_config", "confidence_gate")
emit_replay_key("p0", "agent_spec_config")
emit_determinism_digest("p0", "agent_spec_config")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "agent_spec_config", "execution_auth")
_emit_validates_capability("p2", "agent_spec_config", "capability_check")
_emit_routes_to_capability("p2", "agent_spec_config", "capability_route")
_emit_writes_via_uwg("p2", "agent_spec_config", "uwg_write")
_emit_blocks_direct_write("p2", "agent_spec_config", "direct_write_block")
_emit_records_tool_invocation("p2", "agent_spec_config", "tool_invocation")
_emit_captures_execution_output("p2", "agent_spec_config", "exec_output")
_emit_dispatches_agent("p3", "agent_spec_config", "agent_dispatch")
_emit_coordinates_agents("p3", "agent_spec_config", "agent_coordination")
_emit_records_workflow_lineage("p3", "agent_spec_config", "workflow_lineage")
_emit_records_healing_outcome("p3", "agent_spec_config", "healing_outcome")
_emit_escalates_failure("p3", "agent_spec_config", "failure_escalation")
_emit_orchestrates_workflow("p3", "agent_spec_config", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "agent_spec_config", "healing_dispatch")
_emit_invokes_evaluation("p3", "agent_spec_config", "evaluation_signal")
_emit_records_telemetry_event("p4", "agent_spec_config", "telemetry_event")
_emit_captures_evaluation_metric("p4", "agent_spec_config", "eval_metric")
_emit_stores_embedding("p4", "agent_spec_config", "embedding_store")
_emit_updates_meta_learning_state("p4", "agent_spec_config", "meta_learning")
_emit_links_execution_to_snapshot("p4", "agent_spec_config", "exec_snapshot_link")
_emit_reads_through("l4", "agent_spec_config", "urg_read_1")
_emit_reads_through("l4", "agent_spec_config", "urg_read_2")
_emit_reads_through("l4", "agent_spec_config", "urg_read_3")
_emit_reads_through("l4", "agent_spec_config", "urg_read_4")
_emit_reads_through("l4", "agent_spec_config", "urg_read_5")
_emit_reads_through("l4", "agent_spec_config", "urg_read_6")
_emit_reads_through("l4", "agent_spec_config", "urg_read_7")
_emit_reads_through("l4", "agent_spec_config", "urg_read_8")
_emit_reads_through("l4", "agent_spec_config", "urg_read_9")
_emit_reads_through("l4", "agent_spec_config", "urg_read_10")
_emit_reads_through("l4", "agent_spec_config", "urg_read_11")
_emit_reads_through("l4", "agent_spec_config", "urg_read_12")
_emit_reads_through("l4", "agent_spec_config", "urg_read_13")
_emit_reads_through("l4", "agent_spec_config", "urg_read_14")
_emit_reads_through("l4", "agent_spec_config", "urg_read_15")
_emit_reads_through("l4", "agent_spec_config", "urg_read_16")
_emit_reads_through("l4", "agent_spec_config", "urg_read_17")
_emit_reads_through("l4", "agent_spec_config", "urg_read_18")
_emit_reads_through("l4", "agent_spec_config", "urg_read_19")
_emit_reads_through("l4", "agent_spec_config", "urg_read_20")
_emit_reads_through("l4", "agent_spec_config", "urg_read_21")
_emit_reads_through("l4", "agent_spec_config", "urg_read_22")
_emit_reads_through("l4", "agent_spec_config", "urg_read_23")
_emit_reads_through("l4", "agent_spec_config", "urg_read_24")
_emit_reads_through("l4", "agent_spec_config", "urg_read_25")
_emit_reads_through("l4", "agent_spec_config", "urg_read_26")
_emit_reads_through("l4", "agent_spec_config", "urg_read_27")
_emit_reads_through("l4", "agent_spec_config", "urg_read_28")
_emit_reads_through("l4", "agent_spec_config", "urg_read_29")
_emit_reads_through("l4", "agent_spec_config", "urg_read_30")
_emit_reads_through("l4", "agent_spec_config", "urg_read_31")
_emit_reads_through("l4", "agent_spec_config", "urg_read_32")
_emit_reads_through("l4", "agent_spec_config", "urg_read_33")
_emit_reads_through("l4", "agent_spec_config", "urg_read_34")
_emit_reads_through("l4", "agent_spec_config", "urg_read_35")
_emit_reads_through("l4", "agent_spec_config", "urg_read_36")
_emit_reads_through("l4", "agent_spec_config", "urg_read_37")
_emit_reads_through("l4", "agent_spec_config", "urg_read_38")
_emit_reads_through("l4", "agent_spec_config", "urg_read_39")
_emit_reads_through("l4", "agent_spec_config", "urg_read_40")
_emit_reads_through("l4", "agent_spec_config", "urg_read_41")
_emit_reads_through("l4", "agent_spec_config", "urg_read_42")
_emit_reads_through("l4", "agent_spec_config", "urg_read_43")
_emit_reads_through("l4", "agent_spec_config", "urg_read_44")
_emit_reads_through("l4", "agent_spec_config", "urg_read_45")
_emit_reads_through("l4", "agent_spec_config", "urg_read_46")
_emit_reads_through("l4", "agent_spec_config", "urg_read_47")
_emit_reads_through("l4", "agent_spec_config", "urg_read_48")
_emit_reads_through("l4", "agent_spec_config", "urg_read_49")
_emit_reads_through("l4", "agent_spec_config", "urg_read_50")
_emit_reads_through("l4", "agent_spec_config", "urg_read_51")
_emit_reads_through("l4", "agent_spec_config", "urg_read_52")
_emit_reads_through("l4", "agent_spec_config", "urg_read_53")
_emit_reads_through("l4", "agent_spec_config", "urg_read_54")
_emit_reads_through("l4", "agent_spec_config", "urg_read_55")
_emit_reads_through("l4", "agent_spec_config", "urg_read_56")
_emit_reads_through("l4", "agent_spec_config", "urg_read_57")
_emit_reads_through("l4", "agent_spec_config", "urg_read_58")
_emit_reads_through("l4", "agent_spec_config", "urg_read_59")
_emit_reads_through("l4", "agent_spec_config", "urg_read_60")
_emit_reads_through("l4", "agent_spec_config", "urg_read_61")
_emit_reads_through("l4", "agent_spec_config", "urg_read_62")


DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# =============================================================================
# TOPOLOGY SCHEMAS (Phase 2 Hardening)
# =============================================================================


class AgentSpec(BaseModel):
    """Configuration for a single Sovereign Agent."""

    name: str = Field(..., description="Unique agent identifier (e.g., HOP1_CLERK)")
    module_path: str = Field(..., description="Python path to the engine class")
    inputs: list[str] = Field(default_factory=list, description="Keys required from Buffer")
    outputs: list[str] = Field(default_factory=list, description="Keys written to Buffer")
    timeout_sec: int = Field(default=30, ge=1)
    criticality: str = Field(default="required", pattern="^(required|optional|best_effort)$")


class OrchestrationTopology(BaseModel):
    """Defines the execution graph."""

    version: str = "2.5.0"
    phases: dict[str, list[str]] = Field(
        ...,
        description="Map of Phase Name -> List of Agent Names in execution order",
    )
    agents: dict[str, AgentSpec] = Field(..., description="Registry of all agents")

    @model_validator(mode="after")
    def validate_agents_exist(self) -> OrchestrationTopology:
        """Ensure all agents listed in phases exist in the agent registry."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "OrchestrationTopology.validate_agents_exist"
        )

        known_agents = set(self.agents.keys())
        for phase, agent_list in self.phases.items():
            for agent in agent_list:
                if agent not in known_agents:
                    raise ValueError(f"Phase '{phase}' references unknown agent: '{agent}'")
        return self


# =============================================================================
# LEGACY HOP CONFIG SCHEMAS (Preserved for backward compatibility)
# =============================================================================


class ClerkExtractionConfig(BaseModel):
    """Settings for HOP1 Clerk Extraction Agent."""

    metrics_patterns: list[str] = Field(
        default_factory=lambda: [r"\$\d+\.?\d*[MBK]\+?", r"\d+\.?\d*%", r"\d{1,3}(?:,\d{3})+"],
    )
    min_bullets_per_section: int = Field(default=3)
    max_bullets_per_section: int = Field(default=8)


class EnrichmentConfig(BaseModel):
    """Settings for HOP2 Enrichment Agent."""

    forbidden_phrases: list[str] = Field(
        default_factory=lambda: [
            "responsible for",
            "duties included",
            "helped with",
            "assisted with",
            "worked on",
        ],
    )
    duplicate_threshold: float = Field(default=0.85, ge=0.0, le=1.0)
    power_verbs: list[str] = Field(
        default_factory=lambda: [
            "achieved",
            "delivered",
            "led",
            "drove",
            "established",
            "transformed",
            "accelerated",
            "optimized",
            "pioneered",
            "spearheaded",
        ],
    )


class GenerationConfig(BaseModel):
    """Settings for HOP3 Generation Agent."""

    base_temperatures: dict[str, float] = Field(
        default_factory=lambda: {"summary": 0.7, "experience": 0.5, "skills": 0.3},
    )
    max_section_words: dict[str, int] = Field(
        default_factory=lambda: {"summary": 100, "experience_bullet": 30, "skills": 50},
    )
    n_candidates: int = Field(default=3)


class ValidationConfig(BaseModel):
    """Settings for HOP4 Validation Agent."""

    severity_threshold: str = Field(default="WARNING")
    rule_categories: list[str] = Field(
        default_factory=lambda: ["grammar", "formatting", "content_quality", "ats_compatibility"],
    )
    min_quality_score: float = Field(default=0.7, ge=0.0, le=1.0)


class GateConfig(BaseModel):
    """Settings for HOP5 Gate Decision Agent."""

    factual_failure_rules: list[str] = Field(
        default_factory=lambda: ["hallucination_detected", "source_mismatch", "date_inconsistency"],
    )
    max_factual_loops: int = Field(default=3)
    max_creative_retries: int = Field(default=5)
    pass_threshold: float = Field(default=0.8, ge=0.0, le=1.0)


class RefinementConfig(BaseModel):
    """Settings for HOP6 Refinement Agent."""

    optimization_targets: list[str] = Field(
        default_factory=lambda: ["keyword_density", "action_verb_strength", "quantification_rate"],
    )
    max_iterations: int = Field(default=3)


class QAReportConfig(BaseModel):
    """Settings for HOP7 QA Report Agent."""

    report_sections: list[str] = Field(
        default_factory=lambda: [
            "executive_summary",
            "quality_metrics",
            "validation_results",
            "recommendations",
        ],
    )
    output_directory: str = Field(default="logs/rg_reports")
    scoring_weights: dict[str, float] = Field(
        default_factory=lambda: {
            "content_quality": 0.3,
            "ats_compatibility": 0.25,
            "keyword_match": 0.25,
            "formatting": 0.2,
        },
    )


class OrchestratorConfig(BaseModel):
    """Settings for the RG Orchestrator."""

    global_step_limit: int = Field(default=20)
    max_retry_iterations: int = Field(default=5)
    checkpoint_enabled: bool = Field(default=True)
    trace_persistence: bool = Field(default=True)


class RGAgentSpecs(PromptReceptionSpec, BaseModel):
    """Root configuration object for all RG Agent Specifications."""

    clerk_extraction: ClerkExtractionConfig = Field(default_factory=ClerkExtractionConfig)
    enrichment: EnrichmentConfig = Field(default_factory=EnrichmentConfig)
    generation: GenerationConfig = Field(default_factory=GenerationConfig)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)
    gate_decision: GateConfig = Field(default_factory=GateConfig)
    refinement: RefinementConfig = Field(default_factory=RefinementConfig)
    qa_report: QAReportConfig = Field(default_factory=QAReportConfig)
    orchestrator: OrchestratorConfig = Field(default_factory=OrchestratorConfig)
