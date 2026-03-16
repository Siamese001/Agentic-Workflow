"""
Evaluation Report Schema

Structured output schemas for reporting evaluation runs to L6 observability
and for consumption by the Meta Learning Pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
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
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SystemEvaluationSummary.from_report")

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
        cls, delta: DeltaReport, baseline_version: str, candidate_version: str
    ) -> ComparativeEvaluationSummary:
        """Build comparative summary from a DeltaReport."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ComparativeEvaluationSummary.from_delta_report")

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
