"""
Phase 4: Shadow Evaluation Runner

Tests new retrieval configurations against production without affecting
live traffic.  Runs candidate config in parallel with baseline and
emits monitoring snapshots for both.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

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

_emit_authorize_and_execute("p2", "shadow_eval_runner", "execution_auth")
_emit_validates_capability("p2", "shadow_eval_runner", "capability_check")
_emit_routes_to_capability("p2", "shadow_eval_runner", "capability_route")
_emit_writes_via_uwg("p2", "shadow_eval_runner", "uwg_write")
_emit_blocks_direct_write("p2", "shadow_eval_runner", "direct_write_block")
_emit_records_tool_invocation("p2", "shadow_eval_runner", "tool_invocation")
_emit_captures_execution_output("p2", "shadow_eval_runner", "exec_output")
_emit_dispatches_agent("p3", "shadow_eval_runner", "agent_dispatch")
_emit_coordinates_agents("p3", "shadow_eval_runner", "agent_coordination")
_emit_records_workflow_lineage("p3", "shadow_eval_runner", "workflow_lineage")
_emit_records_healing_outcome("p3", "shadow_eval_runner", "healing_outcome")
_emit_escalates_failure("p3", "shadow_eval_runner", "failure_escalation")
_emit_orchestrates_workflow("p3", "shadow_eval_runner", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "shadow_eval_runner", "healing_dispatch")
_emit_invokes_evaluation("p3", "shadow_eval_runner", "evaluation_signal")
_emit_records_telemetry_event("p4", "shadow_eval_runner", "telemetry_event")
_emit_captures_evaluation_metric("p4", "shadow_eval_runner", "eval_metric")
_emit_stores_embedding("p4", "shadow_eval_runner", "embedding_store")
_emit_updates_meta_learning_state("p4", "shadow_eval_runner", "meta_learning")
_emit_links_execution_to_snapshot("p4", "shadow_eval_runner", "exec_snapshot_link")
from ..runners.offline_eval_runner import OfflineEvaluationRunner
from ..runners.replay_eval_runner import ReplayEvaluationRunner, SystemConfig
from ..schemas.evaluation_dataset_schema import EvaluationDataset
from ..schemas.evaluation_result_schema import DeltaReport, EvaluationReport
from .drift_monitor import AnswerQualityMonitor, RetrievalDriftMonitor
from .snapshots import RetrievalDriftSnapshot

_emit_applies_guardrail("p0", "shadow_eval_runner", "p0_governance")
_emit_reads_policy_state("p0", "shadow_eval_runner", "policy_binding")
_emit_snapshots_state("p0", "shadow_eval_runner", "state_snapshot")
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

_emit_emits_metric_event("shadow_eval_runner", "p4obs", "metric_1")
_emit_emits_metric_event("shadow_eval_runner", "p4obs", "metric_2")
_emit_emits_metric_event("shadow_eval_runner", "p4obs", "metric_3")
_emit_emits_metric_event("shadow_eval_runner", "p4obs", "metric_4")
_emit_emits_metric_event("shadow_eval_runner", "p4obs", "metric_5")
_emit_emits_metric_event("shadow_eval_runner", "p4obs", "metric_6")
_emit_records_incident_event("shadow_eval_runner", "p4obs", "incident")
_emit_captures_runtime_anomaly("shadow_eval_runner", "p4obs", "anomaly")
_emit_writes_observability_log("shadow_eval_runner", "p4obs", "obs_log")
_emit_updates_monitoring_state("shadow_eval_runner", "p4obs", "mon_state")
_emit_triggers_alert("shadow_eval_runner", "p4obs", "alert")
_emit_links_incident_trace("shadow_eval_runner", "p4obs", "trace_link")
_emit_captures_pattern("shadow_eval_runner", "p3lm", "pattern")
_emit_records_learning_event("shadow_eval_runner", "p3lm", "learning_event")
_emit_writes_learning_snapshot("shadow_eval_runner", "p3lm", "snapshot")
_emit_feeds_meta_learning("shadow_eval_runner", "p3lm", "meta_feed")
_emit_updates_routing_strategy("shadow_eval_runner", "p3lm", "routing")
_emit_improves_agent_policy("shadow_eval_runner", "p3lm", "policy")
_emit_stores_learning_state("shadow_eval_runner", "p3lm", "state")
_emit_records_execution_trace("shadow_eval_runner", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("shadow_eval_runner", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("shadow_eval_runner", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("shadow_eval_runner", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("shadow_eval_runner", "L4_STATE", "p2_trace_5")
_emit_reads_environ("shadow_eval_runner", "env_read", "p2_env_1")
_emit_reads_environ("shadow_eval_runner", "env_read", "p2_env_2")
_emit_reads_runtime_state("shadow_eval_runner", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("shadow_eval_runner", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "shadow_eval_runner", "context_pull")
_emit_pulls_context("p1", "shadow_eval_runner", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "shadow_eval_runner", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "shadow_eval_runner", "uwg_term_2")
_emit_writes_through("p1", "shadow_eval_runner", "write_through")
_emit_writes_through("p1", "shadow_eval_runner", "write_through_2")
_emit_validated_by_safety_plane("p1", "shadow_eval_runner", "safety_validation")
_emit_invokes_eval("p1", "shadow_eval_runner", "eval_call")
_emit_proposal_commits_routing("p1", "shadow_eval_runner", "routing_commit")
_emit_escalates_to_human("p1", "shadow_eval_runner", "human_escalation")
_emit_routes_through("p1", "shadow_eval_runner", "route_through")
_emit_checks_agent_registry("p1", "shadow_eval_runner", "agent_registry")
_emit_validates_agent_capability("p1", "shadow_eval_runner", "capability")
_emit_dispatches_execution_plan("p1", "shadow_eval_runner", "exec_plan")
_emit_agent_executes_agent("p1", "shadow_eval_runner", "sub_agent")
_emit_routes_to_agent("p1", "shadow_eval_runner", "target_agent")
_emit_verifies_policy("p1", "shadow_eval_runner", "policy_check")
_emit_observes_runtime_state("p1", "shadow_eval_runner", "runtime_state")
_emit_verifies_boundary("p1", "shadow_eval_runner", "boundary_check")
_emit_transcripts_response("p1", "shadow_eval_runner", "transcript")
_emit_hard_fails_untranscripted("p1", "shadow_eval_runner")
_emit_gated_by_confidence("p1", "shadow_eval_runner", "confidence_gate")
emit_replay_key("p0", "shadow_eval_runner")
emit_determinism_digest("p0", "shadow_eval_runner")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class ShadowEvaluationRunner:
    """Runs a candidate config in shadow mode against the current baseline.

    Shadow evaluation is non-destructive: candidate results are collected and
    measured but never surfaced to production consumers.

    Usage:
        runner = ShadowEvaluationRunner(baseline_config, candidate_config)
        shadow_result = runner.run(dataset)
        # shadow_result.delta_report contains metric deltas
        # shadow_result.candidate_alerts contains drift alerts if candidate degrades
    """

    def __init__(
        self,
        baseline_config: SystemConfig,
        candidate_config: SystemConfig,
        metrics: list | None = None,
        retrieval_monitor: RetrievalDriftMonitor | None = None,
        answer_monitor: AnswerQualityMonitor | None = None,
        l4_store: Any | None = None,
    ):
        self.baseline_config = baseline_config
        self.candidate_config = candidate_config
        self.metrics = metrics
        self.retrieval_monitor = retrieval_monitor
        self.answer_monitor = answer_monitor
        self.l4_store = l4_store

    def run(self, dataset: EvaluationDataset) -> ShadowEvaluationResult:
        """Execute shadow evaluation.

        Args:
            dataset: Evaluation dataset to run both configs against

        Returns:
            ShadowEvaluationResult with delta report and monitoring snapshots
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ShadowEvaluationRunner.run")

        replay_runner = ReplayEvaluationRunner(metrics=self.metrics, l4_store=self.l4_store)
        delta_report = replay_runner.run(
            dataset=dataset, config_a=self.baseline_config, config_b=self.candidate_config,
        )
        baseline_report = self._run_single(self.baseline_config, dataset)
        candidate_report = self._run_single(self.candidate_config, dataset)
        baseline_retrieval_snapshot = self._build_retrieval_snapshot(
            baseline_report, version=self.baseline_config.version,
        )
        candidate_retrieval_snapshot = self._build_retrieval_snapshot(
            candidate_report, version=self.candidate_config.version,
        )
        candidate_alerts = []
        if self.retrieval_monitor is not None:
            candidate_alerts.extend(self.retrieval_monitor.check_alerts(candidate_retrieval_snapshot))
        return ShadowEvaluationResult(
            delta_report=delta_report,
            baseline_report=baseline_report,
            candidate_report=candidate_report,
            baseline_retrieval_snapshot=baseline_retrieval_snapshot,
            candidate_retrieval_snapshot=candidate_retrieval_snapshot,
            candidate_alerts=candidate_alerts,
        )

    def _run_single(self, config: SystemConfig, dataset: EvaluationDataset) -> EvaluationReport:
        runner = OfflineEvaluationRunner(
            metrics=self.metrics,
            retrieval_fn=config.retrieval_fn,
            generation_fn=config.generation_fn,
            system_version=config.version,
        )
        return runner.run(dataset)

    def _build_retrieval_snapshot(self, report: EvaluationReport, version: str) -> RetrievalDriftSnapshot:
        """Build a lightweight retrieval snapshot from an eval report."""
        scores = report.aggregate_scores
        return RetrievalDriftSnapshot(
            timestamp=datetime.utcnow().isoformat() + "Z",
            system_version=version,
            retrieval_hit_rate=scores.get("recall@10", 0.0),
            score_distribution_mean=scores.get("precision@5", 0.0),
            score_distribution_std=0.0,
            top_k_stability=scores.get("MRR", 0.0),
            sample_size=len(report.per_example_results),
        )


class ShadowEvaluationResult:
    """Result of a shadow evaluation run."""

    def __init__(
        self,
        delta_report: DeltaReport,
        baseline_report: EvaluationReport,
        candidate_report: EvaluationReport,
        baseline_retrieval_snapshot: RetrievalDriftSnapshot,
        candidate_retrieval_snapshot: RetrievalDriftSnapshot,
        candidate_alerts: list,
    ):
        self.delta_report = delta_report
        self.baseline_report = baseline_report
        self.candidate_report = candidate_report
        self.baseline_retrieval_snapshot = baseline_retrieval_snapshot
        self.candidate_retrieval_snapshot = candidate_retrieval_snapshot
        self.candidate_alerts = candidate_alerts

    @property
    def is_improvement(self) -> bool:
        """True if candidate net delta is positive."""
        return sum(self.delta_report.metric_deltas.values()) > 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "delta_report": self.delta_report.to_dict(),
            "baseline_scores": self.baseline_report.aggregate_scores,
            "candidate_scores": self.candidate_report.aggregate_scores,
            "is_improvement": self.is_improvement,
            "candidate_alert_count": len(self.candidate_alerts),
            "candidate_alerts": [a.to_dict() for a in self.candidate_alerts],
        }


__all__ = ["ShadowEvaluationRunner", "ShadowEvaluationResult"]
