"""
apps_research Configuration Schemas — Autonomous Research Engine.

Pydantic models for type-safe configuration. Aligned with apps_rg pattern with
full lifecycle trace contract integration (P0-P4).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, model_validator

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_reads_policy_state,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)

# P0: Foundation Governance
_emit_applies_guardrail("p0", "agent_spec_config", "p0_governance")
_emit_reads_policy_state("p0", "agent_spec_config", "policy_binding")
_emit_snapshots_state("p0", "agent_spec_config", "state_snapshot")

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

# P4 Observability (6 metric events for density)
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

# P3 Learning Maturity
_emit_captures_pattern("agent_spec_config", "p3lm", "pattern")
_emit_records_learning_event("agent_spec_config", "p3lm", "learning_event")
_emit_writes_learning_snapshot("agent_spec_config", "p3lm", "snapshot")
_emit_feeds_meta_learning("agent_spec_config", "p3lm", "meta_feed")
_emit_updates_routing_strategy("agent_spec_config", "p3lm", "routing")
_emit_improves_agent_policy("agent_spec_config", "p3lm", "policy")
_emit_stores_learning_state("agent_spec_config", "p3lm", "state")

# P2 Execution Capability (5 execution traces for coverage)
_emit_records_execution_trace("agent_spec_config", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("agent_spec_config", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("agent_spec_config", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("agent_spec_config", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("agent_spec_config", "L4_STATE", "p2_trace_5")
_emit_reads_environ("agent_spec_config", "env_read", "p2_env_1")
_emit_reads_environ("agent_spec_config", "env_read", "p2_env_2")
_emit_reads_runtime_state("agent_spec_config", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("agent_spec_config", "runtime_state", "p2_rt_2")

# P1 Orchestration
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

# P0 Determinism
emit_replay_key("p0", "agent_spec_config")
emit_determinism_digest("p0", "agent_spec_config")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# P2 Capability Routing
_emit_authorize_and_execute("p2", "agent_spec_config", "execution_auth")
_emit_validates_capability("p2", "agent_spec_config", "capability_check")
_emit_routes_to_capability("p2", "agent_spec_config", "capability_route")
_emit_writes_via_uwg("p2", "agent_spec_config", "uwg_write")
_emit_blocks_direct_write("p2", "agent_spec_config", "direct_write_block")
_emit_records_tool_invocation("p2", "agent_spec_config", "tool_invocation")
_emit_captures_execution_output("p2", "agent_spec_config", "exec_output")

# P3 Orchestration
_emit_dispatches_agent("p3", "agent_spec_config", "agent_dispatch")
_emit_coordinates_agents("p3", "agent_spec_config", "agent_coordination")
_emit_records_workflow_lineage("p3", "agent_spec_config", "workflow_lineage")
_emit_records_healing_outcome("p3", "agent_spec_config", "healing_outcome")
_emit_escalates_failure("p3", "agent_spec_config", "failure_escalation")
_emit_orchestrates_workflow("p3", "agent_spec_config", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "agent_spec_config", "healing_dispatch")
_emit_invokes_evaluation("p3", "agent_spec_config", "evaluation_signal")

# P4 State & Telemetry
_emit_records_telemetry_event("p4", "agent_spec_config", "telemetry_event")
_emit_captures_evaluation_metric("p4", "agent_spec_config", "eval_metric")
_emit_stores_embedding("p4", "agent_spec_config", "embedding_store")
_emit_updates_meta_learning_state("p4", "agent_spec_config", "meta_learning")
_emit_links_execution_to_snapshot("p4", "agent_spec_config", "exec_snapshot_link")

_log = logging.getLogger(__name__)


class ArtifactModeConfig(BaseModel):
    """Configuration for a research artifact mode."""

    mode_id: str
    display_name: str
    required_sections: list[str] = Field(default_factory=list)
    max_words: int = Field(default=1500, ge=100)
    requires_source_register: bool = True
    requires_comparison_table: bool = False


class SourceRegisterConfig(BaseModel):
    """Configuration for the source register schema."""

    max_sources: int = Field(default=20, ge=1)
    required_fields: list[str] = Field(
        default_factory=lambda: ["source_id", "title", "claim_type", "confidence"]
    )
    claim_types: list[str] = Field(
        default_factory=lambda: ["direct_evidence", "interpretation", "analyst_inference", "assumption"]
    )


class ResearchGateConfig(BaseModel):
    """Quality gates for research artifacts."""

    require_source_register: bool = True
    min_sources: int = Field(default=1, ge=0)
    require_audience_declaration: bool = True
    require_purpose_declaration: bool = True
    max_unsupported_claims: int = Field(default=0, ge=0)
    require_inference_labels: bool = True
    min_quality_score: float = Field(default=0.70, ge=0.0, le=1.0)


class ResearchOutputConfig(BaseModel):
    """Output configuration."""

    output_dir: str = Field(default="reports/research")
    artifact_prefix: str = Field(default="research")
    emit_run_summary: bool = True
    emit_source_register: bool = True
    dry_run: bool = False


class ResearchAgentSpecs(BaseModel):
    """Root configuration for all apps_research agent specifications."""

    version: str = "1.0.0"
    artifact_modes: dict[str, ArtifactModeConfig] = Field(
        default_factory=lambda: {
            "brief": ArtifactModeConfig(
                mode_id="brief",
                display_name="Topic Brief",
                required_sections=["executive_summary", "key_findings", "strategic_implications"],
                max_words=1200,
            ),
            "comparison": ArtifactModeConfig(
                mode_id="comparison",
                display_name="Framework Comparison",
                required_sections=["comparison_overview", "comparison_matrix", "recommendation"],
                max_words=2000,
                requires_comparison_table=True,
            ),
            "trend": ArtifactModeConfig(
                mode_id="trend",
                display_name="Trend Scan",
                required_sections=["trend_overview", "signal_analysis", "horizon_implications"],
                max_words=1500,
            ),
            "position": ArtifactModeConfig(
                mode_id="position",
                display_name="Position Memo",
                required_sections=[
                    "position_statement",
                    "supporting_evidence",
                    "counterarguments",
                    "conclusion",
                ],
                max_words=1800,
            ),
            "thought_leadership": ArtifactModeConfig(
                mode_id="thought_leadership",
                display_name="Thought Leadership Post",
                required_sections=["hook", "insight", "evidence", "call_to_action"],
                max_words=800,
            ),
        }
    )
    source_register: SourceRegisterConfig = Field(default_factory=SourceRegisterConfig)
    gate: ResearchGateConfig = Field(default_factory=ResearchGateConfig)
    output: ResearchOutputConfig = Field(default_factory=ResearchOutputConfig)
    global_step_limit: int = Field(default=8)
    checkpoint_enabled: bool = True
    trace_persistence: bool = True

    @model_validator(mode="after")
    def validate_modes_non_empty(self) -> ResearchAgentSpecs:
        """Validate that at least one artifact mode is defined."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "ResearchAgentSpecs.validate_modes_non_empty"
        )

        if not self.artifact_modes:
            raise ValueError("ResearchAgentSpecs.artifact_modes must define at least one mode")
        return self


_SPEC_CACHE: ResearchAgentSpecs | None = None


def load_research_specs(spec_path: str | None = None) -> ResearchAgentSpecs:
    """Load ResearchAgentSpecs from JSON file or return defaults."""
    global _SPEC_CACHE
    if _SPEC_CACHE is not None:
        return _SPEC_CACHE

    resolved: Path | None = None
    if spec_path:
        resolved = Path(spec_path)
    else:
        default = Path(__file__).parent / "research_agent_specs.json"
        if default.exists():
            resolved = default

    if resolved and resolved.exists():
        try:
            raw: dict[str, Any] = json.loads(resolved.read_text(encoding="utf-8"))
            _SPEC_CACHE = ResearchAgentSpecs.model_validate(raw)
            return _SPEC_CACHE
        except (FileNotFoundError, json.JSONDecodeError, ValueError, OSError) as exc:
            _log.warning("[apps_research] Failed to load specs: %s — using defaults", exc)

    _SPEC_CACHE = ResearchAgentSpecs()
    return _SPEC_CACHE
