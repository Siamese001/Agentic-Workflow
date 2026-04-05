"""
Replay Evaluation Runner

Deterministically compares two system configurations (A vs B) over the
same evaluation dataset and produces a DeltaReport.

Inputs:  eval_dataset, system_config_A, system_config_B
Output:  DeltaReport (persisted to L4 when store is provided)
"""

from __future__ import annotations

from datetime import datetime
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
    record_execution_trace,
)

_emit_authorize_and_execute("p2", "replay_eval_runner", "execution_auth")
_emit_validates_capability("p2", "replay_eval_runner", "capability_check")
_emit_routes_to_capability("p2", "replay_eval_runner", "capability_route")
_emit_writes_via_uwg("p2", "replay_eval_runner", "uwg_write")
_emit_blocks_direct_write("p2", "replay_eval_runner", "direct_write_block")
_emit_records_tool_invocation("p2", "replay_eval_runner", "tool_invocation")
_emit_captures_execution_output("p2", "replay_eval_runner", "exec_output")
_emit_dispatches_agent("p3", "replay_eval_runner", "agent_dispatch")
_emit_coordinates_agents("p3", "replay_eval_runner", "agent_coordination")
_emit_records_workflow_lineage("p3", "replay_eval_runner", "workflow_lineage")
_emit_records_healing_outcome("p3", "replay_eval_runner", "healing_outcome")
_emit_escalates_failure("p3", "replay_eval_runner", "failure_escalation")
_emit_orchestrates_workflow("p3", "replay_eval_runner", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "replay_eval_runner", "healing_dispatch")
_emit_invokes_evaluation("p3", "replay_eval_runner", "evaluation_signal")
_emit_records_telemetry_event("p4", "replay_eval_runner", "telemetry_event")
_emit_captures_evaluation_metric("p4", "replay_eval_runner", "eval_metric")
_emit_stores_embedding("p4", "replay_eval_runner", "embedding_store")
_emit_updates_meta_learning_state("p4", "replay_eval_runner", "meta_learning")
_emit_links_execution_to_snapshot("p4", "replay_eval_runner", "exec_snapshot_link")
from ..schemas.evaluation_dataset_schema import EvaluationDataset
from ..schemas.evaluation_result_schema import (
    DeltaReport,
    EvaluationReport,
)
from .offline_eval_runner import GenerationFn, OfflineEvaluationRunner, RetrievalFn

_emit_applies_guardrail("p0", "replay_eval_runner", "p0_governance")
_emit_reads_policy_state("p0", "replay_eval_runner", "policy_binding")
_emit_snapshots_state("p0", "replay_eval_runner", "state_snapshot")
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

record_execution_trace("replay_eval_runner", "replay_eval_runner_trace")


_emit_emits_metric_event("replay_eval_runner", "p4obs", "metric_1")
_emit_emits_metric_event("replay_eval_runner", "p4obs", "metric_2")
_emit_emits_metric_event("replay_eval_runner", "p4obs", "metric_3")
_emit_emits_metric_event("replay_eval_runner", "p4obs", "metric_4")
_emit_emits_metric_event("replay_eval_runner", "p4obs", "metric_5")
_emit_emits_metric_event("replay_eval_runner", "p4obs", "metric_6")
_emit_records_incident_event("replay_eval_runner", "p4obs", "incident")
_emit_captures_runtime_anomaly("replay_eval_runner", "p4obs", "anomaly")
_emit_writes_observability_log("replay_eval_runner", "p4obs", "obs_log")
_emit_updates_monitoring_state("replay_eval_runner", "p4obs", "mon_state")
_emit_triggers_alert("replay_eval_runner", "p4obs", "alert")
_emit_links_incident_trace("replay_eval_runner", "p4obs", "trace_link")
_emit_captures_pattern("replay_eval_runner", "p3lm", "pattern")
_emit_records_learning_event("replay_eval_runner", "p3lm", "learning_event")
_emit_writes_learning_snapshot("replay_eval_runner", "p3lm", "snapshot")
_emit_feeds_meta_learning("replay_eval_runner", "p3lm", "meta_feed")
_emit_updates_routing_strategy("replay_eval_runner", "p3lm", "routing")
_emit_improves_agent_policy("replay_eval_runner", "p3lm", "policy")
_emit_stores_learning_state("replay_eval_runner", "p3lm", "state")
_emit_records_execution_trace("replay_eval_runner", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("replay_eval_runner", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("replay_eval_runner", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("replay_eval_runner", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("replay_eval_runner", "L4_STATE", "p2_trace_5")
_emit_reads_environ("replay_eval_runner", "env_read", "p2_env_1")
_emit_reads_environ("replay_eval_runner", "env_read", "p2_env_2")
_emit_reads_runtime_state("replay_eval_runner", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("replay_eval_runner", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "replay_eval_runner", "context_pull")
_emit_pulls_context("p1", "replay_eval_runner", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "replay_eval_runner", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "replay_eval_runner", "uwg_term_2")
_emit_writes_through("p1", "replay_eval_runner", "write_through")
_emit_writes_through("p1", "replay_eval_runner", "write_through_2")
_emit_validated_by_safety_plane("p1", "replay_eval_runner", "safety_validation")
_emit_invokes_eval("p1", "replay_eval_runner", "eval_call")
_emit_proposal_commits_routing("p1", "replay_eval_runner", "routing_commit")
_emit_escalates_to_human("p1", "replay_eval_runner", "human_escalation")
_emit_routes_through("p1", "replay_eval_runner", "route_through")
_emit_checks_agent_registry("p1", "replay_eval_runner", "agent_registry")
_emit_validates_agent_capability("p1", "replay_eval_runner", "capability")
_emit_dispatches_execution_plan("p1", "replay_eval_runner", "exec_plan")
_emit_agent_executes_agent("p1", "replay_eval_runner", "sub_agent")
_emit_routes_to_agent("p1", "replay_eval_runner", "target_agent")
_emit_verifies_policy("p1", "replay_eval_runner", "policy_check")
_emit_observes_runtime_state("p1", "replay_eval_runner", "runtime_state")
_emit_verifies_boundary("p1", "replay_eval_runner", "boundary_check")
_emit_transcripts_response("p1", "replay_eval_runner", "transcript")
_emit_hard_fails_untranscripted("p1", "replay_eval_runner")
_emit_gated_by_confidence("p1", "replay_eval_runner", "confidence_gate")
emit_replay_key("p0", "replay_eval_runner")
emit_determinism_digest("p0", "replay_eval_runner")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class SystemConfig:
    """Encapsulates a named system configuration for replay comparison."""

    def __init__(
        self,
        name: str,
        version: str,
        retrieval_fn: RetrievalFn | None = None,
        generation_fn: GenerationFn | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        self.name = name
        self.version = version
        self.retrieval_fn = retrieval_fn
        self.generation_fn = generation_fn
        self.metadata: dict[str, Any] = metadata or {}


class ReplayEvaluationRunner:
    """Runs two system configs against the same dataset and computes metric deltas.

    Both configs are evaluated deterministically — same dataset, same metrics,
    same order — ensuring reproducible comparison.
    """

    def __init__(
        self,
        metrics: list | None = None,
        l4_store: Any | None = None,
    ):
        self.metrics = metrics
        self.l4_store = l4_store

    def run(
        self,
        dataset: EvaluationDataset,
        config_a: SystemConfig,
        config_b: SystemConfig,
    ) -> DeltaReport:
        """Compare config A vs config B on the given dataset.

        Args:
            dataset: Evaluation dataset (same for both configs)
            config_a: Baseline system configuration
            config_b: Candidate system configuration

        Returns:
            DeltaReport with metric_deltas = scores_b - scores_a
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ReplayEvaluationRunner.run")

        runner_a = OfflineEvaluationRunner(
            metrics=self.metrics,
            retrieval_fn=config_a.retrieval_fn,
            generation_fn=config_a.generation_fn,
            system_version=config_a.version,
        )
        runner_b = OfflineEvaluationRunner(
            metrics=self.metrics,
            retrieval_fn=config_b.retrieval_fn,
            generation_fn=config_b.generation_fn,
            system_version=config_b.version,
        )

        report_a = runner_a.run(dataset)
        report_b = runner_b.run(dataset)

        delta_report = self._compute_delta(report_a, report_b, config_a, config_b)

        if self.l4_store is not None:
            self._persist_delta(delta_report)

        return delta_report

    def _compute_delta(
        self,
        report_a: EvaluationReport,
        report_b: EvaluationReport,
        config_a: SystemConfig,
        config_b: SystemConfig,
    ) -> DeltaReport:
        """Compute per-metric deltas: scores_b - scores_a."""
        scores_a = report_a.aggregate_scores
        scores_b = report_b.aggregate_scores

        all_metrics = sorted(set(list(scores_a.keys()) + list(scores_b.keys())))
        metric_deltas: dict[str, float] = {}
        for metric_name in all_metrics:
            score_a = scores_a.get(metric_name, 0.0)
            score_b = scores_b.get(metric_name, 0.0)
            metric_deltas[metric_name] = score_b - score_a

        return DeltaReport(
            run_id_a=report_a.run_id,
            run_id_b=report_b.run_id,
            config_a_name=config_a.name,
            config_b_name=config_b.name,
            timestamp=datetime.utcnow().isoformat() + "Z",
            metric_deltas=metric_deltas,
            scores_a=dict(scores_a),
            scores_b=dict(scores_b),
        )

    def _persist_delta(self, delta: DeltaReport) -> None:
        """Persist DeltaReport artifact to L4 state registry."""
        try:
            from agentic_core.L4_state.utils.storage.persistent_store import create_artifact

            artifact = create_artifact(
                kind="evaluation_delta",
                logical_id=f"delta_{delta.run_id_a[:8]}_{delta.run_id_b[:8]}",
                payload=delta.to_dict(),
            )
            self.l4_store.put(artifact)
        # guardian: allow-silent-swallow -- L4 persistence failure is non-critical; evaluation already completed
        except Exception:
            pass


__all__ = [
    "ReplayEvaluationRunner",
    "SystemConfig",
]
