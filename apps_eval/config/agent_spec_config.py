"""
apps_eval Configuration Schemas — Evaluation Lab.

Pydantic models for type-safe configuration. Aligned with apps_rg pattern.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, model_validator

from apps_shared.config.prompt_reception_spec import PromptReceptionSpec
from agentic_core.L0_routing.config.model_registry import QWEN_LOCAL_MODEL_ID

from apps_eval._telemetry import (
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

_emit_applies_guardrail("p0", "agent_spec_config", "p0_governance")
_emit_reads_policy_state("p0", "agent_spec_config", "policy_binding")
_emit_snapshots_state("p0", "agent_spec_config", "state_snapshot")
from apps_eval._telemetry import (
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

_log = logging.getLogger(__name__)


class BenchmarkSuiteConfig(BaseModel):
    """Configuration for a single benchmark suite."""

    suite_id: str
    display_name: str
    target_module: str = Field(..., description="Python import path to the module under test")
    scenario_ids: list[str] = Field(default_factory=list)
    timeout_sec: int = Field(default=60, ge=1)
    required: bool = True


class ScorecardDimensionConfig(BaseModel):
    """A single scored dimension in the evaluation scorecard."""

    dimension_id: str
    display_name: str
    weight: float = Field(default=1.0, ge=0.0, le=10.0)
    threshold_pass: float = Field(default=0.70, ge=0.0, le=1.0)
    threshold_warn: float = Field(default=0.80, ge=0.0, le=1.0)


class RegressionConfig(BaseModel):
    """Configuration for regression detection."""

    baseline_dir: str = Field(default="eval_baselines")
    tolerance_delta: float = Field(
        default=0.05,
        ge=0.0,
        le=1.0,
        description="Max allowed score drop before REGRESSION flag",
    )
    auto_update_baseline: bool = False


class EvalOutputConfig(BaseModel):
    """Output configuration for evaluation lab."""

    output_dir: str = Field(default="artifacts/eval")
    artifact_prefix: str = Field(default="eval_report")
    emit_run_summary: bool = True
    emit_scorecard_csv: bool = True
    emit_json_manifest: bool = True
    dry_run: bool = False


class EvalGateConfig(BaseModel):
    """Quality gates for evaluation runs."""

    min_overall_score: float = Field(default=0.70, ge=0.0, le=1.0)
    fail_on_regression: bool = True
    fail_on_missing_suite: bool = True
    max_timeout_violations: int = Field(default=0, ge=0)


class EvalQwenPilotConfig(BaseModel):
    """Qwen pilot settings for apps_eval."""

    enabled: bool = True
    model_id: str = QWEN_LOCAL_MODEL_ID
    confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    prompt_templates_file: str = "apps_eval/data/evaluation_prompts.json"
    max_tokens: int = Field(default=1536, ge=1)
    temperature: float = Field(default=0.05, ge=0.0, le=2.0)


class EvalAgentSpecs(PromptReceptionSpec, BaseModel):
    """Root configuration for all apps_eval agent specifications."""

    version: str = "1.0.0"
    benchmark_suites: dict[str, BenchmarkSuiteConfig] = Field(
        default_factory=lambda: {
            "routing_enforcement": BenchmarkSuiteConfig(
                suite_id="routing_enforcement",
                display_name="L0 Routing Enforcement",
                target_module="agentic_core.L0_routing.enforcement",
                scenario_ids=["policy_hash_valid", "policy_hash_invalid", "missing_hash"],
            ),
            "determinism_contracts": BenchmarkSuiteConfig(
                suite_id="determinism_contracts",
                display_name="Determinism Contract Checks",
                target_module="agentic_core.L5_safety.static_checks.determinism_serialization_check",
                scenario_ids=["nondeterministic_time_call", "allowlisted_call", "clean_module"],
            ),
            "orchestration_hop": BenchmarkSuiteConfig(
                suite_id="orchestration_hop",
                display_name="Multi-Hop Orchestration",
                target_module="apps_shared.adapters.rg_orchestrator_facade",
                scenario_ids=["single_hop", "multi_hop_pass", "multi_hop_gate_fail"],
            ),
            "output_contracts": BenchmarkSuiteConfig(
                suite_id="output_contracts",
                display_name="Output Contract Integrity",
                target_module="agentic_core.interfaces.execution_contracts",
                scenario_ids=["signed_output_valid", "tampered_signature"],
            ),
            "exec_brief_generation": BenchmarkSuiteConfig(
                suite_id="exec_brief_generation",
                display_name="Executive Brief Generation (apps_exec)",
                target_module="apps_exec.reasoning.ExecOrchestrator",
                scenario_ids=["recruiter_brief", "cto_brief", "dry_run"],
            ),
            "ml_metrics_validation": BenchmarkSuiteConfig(
                suite_id="ml_metrics_validation",
                display_name="ML Evaluation Metrics Validation",
                target_module="agentic_core.evaluation.metrics.classification",
                scenario_ids=[
                    "binary_precision_perfect",
                    "binary_recall_perfect",
                    "binary_f1_harmonic_mean",
                    "multiclass_macro_f1",
                    "multiclass_weighted_f1",
                    "confusion_matrix_invariants",
                ],
            ),
        },
    )
    scorecard_dimensions: list[ScorecardDimensionConfig] = Field(
        default_factory=lambda: [
            ScorecardDimensionConfig(
                dimension_id="correctness",
                display_name="Correctness",
                weight=3.0,
                threshold_pass=0.80,
            ),
            ScorecardDimensionConfig(
                dimension_id="determinism",
                display_name="Determinism Compliance",
                weight=3.0,
                threshold_pass=0.90,
            ),
            ScorecardDimensionConfig(
                dimension_id="governance",
                display_name="Governance Gate Coverage",
                weight=2.5,
                threshold_pass=0.75,
            ),
            ScorecardDimensionConfig(
                dimension_id="latency",
                display_name="Latency SLA",
                weight=1.5,
                threshold_pass=0.70,
            ),
            ScorecardDimensionConfig(
                dimension_id="output_richness",
                display_name="Output Richness",
                weight=1.0,
                threshold_pass=0.65,
            ),
            ScorecardDimensionConfig(
                dimension_id="ml_metric_correctness",
                display_name="ML Metric Correctness",
                weight=2.0,
                threshold_pass=0.90,
            ),
        ],
    )
    regression: RegressionConfig = Field(default_factory=RegressionConfig)
    output: EvalOutputConfig = Field(default_factory=EvalOutputConfig)
    gate: EvalGateConfig = Field(default_factory=EvalGateConfig)
    qwen: EvalQwenPilotConfig = Field(default_factory=EvalQwenPilotConfig)
    global_step_limit: int = Field(default=20)
    checkpoint_enabled: bool = True
    trace_persistence: bool = True

    @model_validator(mode="after")
    def validate_weights_sum(self) -> EvalAgentSpecs:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "EvalAgentSpecs.validate_weights_sum"
        )

        total = sum(d.weight for d in self.scorecard_dimensions)
        if total <= 0:
            raise ValueError("Scorecard dimension weights must sum to > 0")
        return self


_SPEC_CACHE: EvalAgentSpecs | None = None


def load_eval_specs(spec_path: str | None = None) -> EvalAgentSpecs:
    """Load EvalAgentSpecs from JSON file or return defaults."""
    global _SPEC_CACHE
    if _SPEC_CACHE is not None:
        return _SPEC_CACHE

    resolved: Path | None = None
    if spec_path:
        resolved = Path(spec_path)
    else:
        default = Path(__file__).parent / "eval_agent_specs.json"
        if default.exists():
            resolved = default

    if resolved and resolved.exists():
        try:
            raw: dict[str, Any] = json.loads(resolved.read_text(encoding="utf-8"))
            _SPEC_CACHE = EvalAgentSpecs.model_validate(raw)
            return _SPEC_CACHE
        except (FileNotFoundError, json.JSONDecodeError, ValueError, OSError) as exc:
            _log.warning("[apps_eval] Failed to load specs: %s — using defaults", exc)

    _SPEC_CACHE = EvalAgentSpecs()
    return _SPEC_CACHE
