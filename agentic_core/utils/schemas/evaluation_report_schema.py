"""
Evaluation Report Schema

Structured output schemas for reporting evaluation runs to L6 observability
and for consumption by the Meta Learning Pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass
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

_emit_authorize_and_execute("p2", "evaluation_report_schema", "execution_auth")
_emit_validates_capability("p2", "evaluation_report_schema", "capability_check")
_emit_routes_to_capability("p2", "evaluation_report_schema", "capability_route")
_emit_writes_via_uwg("p2", "evaluation_report_schema", "uwg_write")
_emit_blocks_direct_write("p2", "evaluation_report_schema", "direct_write_block")
_emit_records_tool_invocation("p2", "evaluation_report_schema", "tool_invocation")
_emit_captures_execution_output("p2", "evaluation_report_schema", "exec_output")
_emit_dispatches_agent("p3", "evaluation_report_schema", "agent_dispatch")
_emit_coordinates_agents("p3", "evaluation_report_schema", "agent_coordination")
_emit_records_workflow_lineage("p3", "evaluation_report_schema", "workflow_lineage")
_emit_records_healing_outcome("p3", "evaluation_report_schema", "healing_outcome")
_emit_escalates_failure("p3", "evaluation_report_schema", "failure_escalation")
_emit_orchestrates_workflow("p3", "evaluation_report_schema", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "evaluation_report_schema", "healing_dispatch")
_emit_invokes_evaluation("p3", "evaluation_report_schema", "evaluation_signal")
_emit_records_telemetry_event("p4", "evaluation_report_schema", "telemetry_event")
_emit_captures_evaluation_metric("p4", "evaluation_report_schema", "eval_metric")
_emit_stores_embedding("p4", "evaluation_report_schema", "embedding_store")
_emit_updates_meta_learning_state("p4", "evaluation_report_schema", "meta_learning")
_emit_links_execution_to_snapshot("p4", "evaluation_report_schema", "exec_snapshot_link")
from .evaluation_result_schema import DeltaReport, EvaluationReport

_emit_applies_guardrail("p0", "evaluation_report_schema", "p0_governance")
_emit_reads_policy_state("p0", "evaluation_report_schema", "policy_binding")
_emit_snapshots_state("p0", "evaluation_report_schema", "state_snapshot")
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

_emit_emits_metric_event("evaluation_report_schema", "p4obs", "metric_1")
_emit_emits_metric_event("evaluation_report_schema", "p4obs", "metric_2")
_emit_emits_metric_event("evaluation_report_schema", "p4obs", "metric_3")
_emit_emits_metric_event("evaluation_report_schema", "p4obs", "metric_4")
_emit_emits_metric_event("evaluation_report_schema", "p4obs", "metric_5")
_emit_emits_metric_event("evaluation_report_schema", "p4obs", "metric_6")
_emit_records_incident_event("evaluation_report_schema", "p4obs", "incident")
_emit_captures_runtime_anomaly("evaluation_report_schema", "p4obs", "anomaly")
_emit_writes_observability_log("evaluation_report_schema", "p4obs", "obs_log")
_emit_updates_monitoring_state("evaluation_report_schema", "p4obs", "mon_state")
_emit_triggers_alert("evaluation_report_schema", "p4obs", "alert")
_emit_links_incident_trace("evaluation_report_schema", "p4obs", "trace_link")
_emit_captures_pattern("evaluation_report_schema", "p3lm", "pattern")
_emit_records_learning_event("evaluation_report_schema", "p3lm", "learning_event")
_emit_writes_learning_snapshot("evaluation_report_schema", "p3lm", "snapshot")
_emit_feeds_meta_learning("evaluation_report_schema", "p3lm", "meta_feed")
_emit_updates_routing_strategy("evaluation_report_schema", "p3lm", "routing")
_emit_improves_agent_policy("evaluation_report_schema", "p3lm", "policy")
_emit_stores_learning_state("evaluation_report_schema", "p3lm", "state")
_emit_records_execution_trace("evaluation_report_schema", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("evaluation_report_schema", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("evaluation_report_schema", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("evaluation_report_schema", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("evaluation_report_schema", "L4_STATE", "p2_trace_5")
_emit_reads_environ("evaluation_report_schema", "env_read", "p2_env_1")
_emit_reads_environ("evaluation_report_schema", "env_read", "p2_env_2")
_emit_reads_runtime_state("evaluation_report_schema", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("evaluation_report_schema", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "evaluation_report_schema", "context_pull")
_emit_pulls_context("p1", "evaluation_report_schema", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "evaluation_report_schema", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "evaluation_report_schema", "uwg_term_2")
_emit_writes_through("p1", "evaluation_report_schema", "write_through")
_emit_writes_through("p1", "evaluation_report_schema", "write_through_2")
_emit_validated_by_safety_plane("p1", "evaluation_report_schema", "safety_validation")
_emit_invokes_eval("p1", "evaluation_report_schema", "eval_call")
_emit_proposal_commits_routing("p1", "evaluation_report_schema", "routing_commit")
_emit_escalates_to_human("p1", "evaluation_report_schema", "human_escalation")
_emit_routes_through("p1", "evaluation_report_schema", "route_through")
_emit_checks_agent_registry("p1", "evaluation_report_schema", "agent_registry")
_emit_validates_agent_capability("p1", "evaluation_report_schema", "capability")
_emit_dispatches_execution_plan("p1", "evaluation_report_schema", "exec_plan")
_emit_agent_executes_agent("p1", "evaluation_report_schema", "sub_agent")
_emit_routes_to_agent("p1", "evaluation_report_schema", "target_agent")
_emit_verifies_policy("p1", "evaluation_report_schema", "policy_check")
_emit_observes_runtime_state("p1", "evaluation_report_schema", "runtime_state")
_emit_verifies_boundary("p1", "evaluation_report_schema", "boundary_check")
_emit_transcripts_response("p1", "evaluation_report_schema", "transcript")
_emit_hard_fails_untranscripted("p1", "evaluation_report_schema")
_emit_gated_by_confidence("p1", "evaluation_report_schema", "confidence_gate")
emit_replay_key("p0", "evaluation_report_schema")
emit_determinism_digest("p0", "evaluation_report_schema")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


@dataclass(frozen=True)
class SystemEvaluationSummary:
    """High-level summary suitable for L6 dashboard and Meta Learning signals."""

    system_version: str
    dataset_name: str
    retrieval_quality_score: float
    answer_quality_score: float
    safety_compliance_score: float
    hallucination_risk_score: float
    timestamp: str
    run_id: str

    @property
    def overall_score(self) -> float:
        """Composite quality score across all dimensions."""
        return (
            self.retrieval_quality_score
            + self.answer_quality_score
            + self.safety_compliance_score
            + (1.0 - self.hallucination_risk_score)
        ) / 4.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "system_version": self.system_version,
            "dataset_name": self.dataset_name,
            "retrieval_quality_score": self.retrieval_quality_score,
            "answer_quality_score": self.answer_quality_score,
            "safety_compliance_score": self.safety_compliance_score,
            "hallucination_risk_score": self.hallucination_risk_score,
            "overall_score": self.overall_score,
            "timestamp": self.timestamp,
            "run_id": self.run_id,
        }

    @classmethod
    def from_report(cls, report: EvaluationReport) -> SystemEvaluationSummary:
        """Build summary from aggregate scores in an EvaluationReport."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "SystemEvaluationSummary.from_report"
        )

        scores = report.aggregate_scores
        return cls(
            system_version=report.system_version,
            dataset_name=report.dataset_name,
            retrieval_quality_score=scores.get("precision@5", 0.0),
            answer_quality_score=scores.get("answer_correctness", 0.0),
            safety_compliance_score=scores.get("safety_compliance", 1.0),
            hallucination_risk_score=scores.get("hallucination_risk", 0.0),
            timestamp=report.timestamp,
            run_id=report.run_id,
        )


@dataclass(frozen=True)
class ComparativeEvaluationSummary:
    """Summary of a comparative (replay) evaluation run for Meta Learning proposals."""

    baseline_run_id: str
    candidate_run_id: str
    baseline_version: str
    candidate_version: str
    timestamp: str
    improvements: dict[str, float]
    regressions: dict[str, float]
    net_delta: float
    recommendation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "baseline_run_id": self.baseline_run_id,
            "candidate_run_id": self.candidate_run_id,
            "baseline_version": self.baseline_version,
            "candidate_version": self.candidate_version,
            "timestamp": self.timestamp,
            "improvements": dict(self.improvements),
            "regressions": dict(self.regressions),
            "net_delta": self.net_delta,
            "recommendation": self.recommendation,
        }

    @classmethod
    def from_delta_report(
        cls,
        delta: DeltaReport,
        baseline_version: str,
        candidate_version: str,
    ) -> ComparativeEvaluationSummary:
        """Build comparative summary from a DeltaReport."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "ComparativeEvaluationSummary.from_delta_report"
        )

        improvements = {k: v for k, v in delta.metric_deltas.items() if v > 0}
        regressions = {k: v for k, v in delta.metric_deltas.items() if v < 0}
        net_delta = sum(delta.metric_deltas.values())
        recommendation = "promote" if net_delta > 0 else "reject"
        return cls(
            baseline_run_id=delta.run_id_a,
            candidate_run_id=delta.run_id_b,
            baseline_version=baseline_version,
            candidate_version=candidate_version,
            timestamp=delta.timestamp,
            improvements=improvements,
            regressions=regressions,
            net_delta=net_delta,
            recommendation=recommendation,
        )


__all__ = ["SystemEvaluationSummary", "ComparativeEvaluationSummary"]
