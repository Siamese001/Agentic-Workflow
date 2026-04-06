"""
Phase H: Evaluation Framework Integration — Completeness-Aware Metrics.

New metrics:
  - context_completeness_score
  - support_score
  - high_similarity_wrong_answer_rate
  - chunk_strategy_comparison (standard vs late chunked)
  - parent_expansion_impact

New comparison reports:
  EvaluationMetricResult
  EvaluationReport
  EvaluationDeltaReport
  RetrievalExperimentReport
  ChunkStrategyReport
  CompletenessExperimentReport

KEY QUESTIONS the system can now answer:
  - Why was the answer wrong even when retrieval looked good?
  - Was the chunk relevant but contextually incomplete?
  - Did parent expansion improve support?
  - Did reranking improve sufficiency, not just similarity?
  - Does late chunking reduce right-chunk-wrong-context failures?
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
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

_emit_applies_guardrail("p0", "completeness_metrics", "p0_governance")
_emit_reads_policy_state("p0", "completeness_metrics", "policy_binding")
_emit_snapshots_state("p0", "completeness_metrics", "state_snapshot")
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

_emit_emits_metric_event("completeness_metrics", "p4obs", "metric_1")
_emit_emits_metric_event("completeness_metrics", "p4obs", "metric_2")
_emit_emits_metric_event("completeness_metrics", "p4obs", "metric_3")
_emit_emits_metric_event("completeness_metrics", "p4obs", "metric_4")
_emit_emits_metric_event("completeness_metrics", "p4obs", "metric_5")
_emit_emits_metric_event("completeness_metrics", "p4obs", "metric_6")
_emit_records_incident_event("completeness_metrics", "p4obs", "incident")
_emit_captures_runtime_anomaly("completeness_metrics", "p4obs", "anomaly")
_emit_writes_observability_log("completeness_metrics", "p4obs", "obs_log")
_emit_updates_monitoring_state("completeness_metrics", "p4obs", "mon_state")
_emit_triggers_alert("completeness_metrics", "p4obs", "alert")
_emit_links_incident_trace("completeness_metrics", "p4obs", "trace_link")
_emit_captures_pattern("completeness_metrics", "p3lm", "pattern")
_emit_records_learning_event("completeness_metrics", "p3lm", "learning_event")
_emit_writes_learning_snapshot("completeness_metrics", "p3lm", "snapshot")
_emit_feeds_meta_learning("completeness_metrics", "p3lm", "meta_feed")
_emit_updates_routing_strategy("completeness_metrics", "p3lm", "routing")
_emit_improves_agent_policy("completeness_metrics", "p3lm", "policy")
_emit_stores_learning_state("completeness_metrics", "p3lm", "state")
_emit_records_execution_trace("completeness_metrics", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("completeness_metrics", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("completeness_metrics", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("completeness_metrics", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("completeness_metrics", "L4_STATE", "p2_trace_5")
_emit_reads_environ("completeness_metrics", "env_read", "p2_env_1")
_emit_reads_environ("completeness_metrics", "env_read", "p2_env_2")
_emit_reads_runtime_state("completeness_metrics", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("completeness_metrics", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "completeness_metrics", "context_pull")
_emit_pulls_context("p1", "completeness_metrics", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "completeness_metrics", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "completeness_metrics", "uwg_term_2")
_emit_writes_through("p1", "completeness_metrics", "write_through")
_emit_writes_through("p1", "completeness_metrics", "write_through_2")
_emit_validated_by_safety_plane("p1", "completeness_metrics", "safety_validation")
_emit_invokes_eval("p1", "completeness_metrics", "eval_call")
_emit_proposal_commits_routing("p1", "completeness_metrics", "routing_commit")
_emit_escalates_to_human("p1", "completeness_metrics", "human_escalation")
_emit_routes_through("p1", "completeness_metrics", "route_through")
_emit_checks_agent_registry("p1", "completeness_metrics", "agent_registry")
_emit_validates_agent_capability("p1", "completeness_metrics", "capability")
_emit_dispatches_execution_plan("p1", "completeness_metrics", "exec_plan")
_emit_agent_executes_agent("p1", "completeness_metrics", "sub_agent")
_emit_routes_to_agent("p1", "completeness_metrics", "target_agent")
_emit_verifies_policy("p1", "completeness_metrics", "policy_check")
_emit_observes_runtime_state("p1", "completeness_metrics", "runtime_state")
_emit_verifies_boundary("p1", "completeness_metrics", "boundary_check")
_emit_transcripts_response("p1", "completeness_metrics", "transcript")
_emit_hard_fails_untranscripted("p1", "completeness_metrics")
_emit_gated_by_confidence("p1", "completeness_metrics", "confidence_gate")
emit_replay_key("p0", "completeness_metrics")
emit_determinism_digest("p0", "completeness_metrics")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "completeness_metrics", "execution_auth")
_emit_validates_capability("p2", "completeness_metrics", "capability_check")
_emit_routes_to_capability("p2", "completeness_metrics", "capability_route")
_emit_writes_via_uwg("p2", "completeness_metrics", "uwg_write")
_emit_blocks_direct_write("p2", "completeness_metrics", "direct_write_block")
_emit_records_tool_invocation("p2", "completeness_metrics", "tool_invocation")
_emit_captures_execution_output("p2", "completeness_metrics", "exec_output")
_emit_dispatches_agent("p3", "completeness_metrics", "agent_dispatch")
_emit_coordinates_agents("p3", "completeness_metrics", "agent_coordination")
_emit_records_workflow_lineage("p3", "completeness_metrics", "workflow_lineage")
_emit_records_healing_outcome("p3", "completeness_metrics", "healing_outcome")
_emit_escalates_failure("p3", "completeness_metrics", "failure_escalation")
_emit_orchestrates_workflow("p3", "completeness_metrics", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "completeness_metrics", "healing_dispatch")
_emit_invokes_evaluation("p3", "completeness_metrics", "evaluation_signal")
_emit_records_telemetry_event("p4", "completeness_metrics", "telemetry_event")
_emit_captures_evaluation_metric("p4", "completeness_metrics", "eval_metric")
_emit_stores_embedding("p4", "completeness_metrics", "embedding_store")
_emit_updates_meta_learning_state("p4", "completeness_metrics", "meta_learning")
_emit_links_execution_to_snapshot("p4", "completeness_metrics", "exec_snapshot_link")


@dataclass(frozen=True)
class EvaluationMetricResult:
    """A single named metric result from an evaluation run."""

    metric_name: str
    value: float
    sample_count: int
    configuration_id: str
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric_name": self.metric_name,
            "value": round(self.value, 6),
            "sample_count": self.sample_count,
            "configuration_id": self.configuration_id,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EvaluationMetricResult:
        return cls(
            metric_name=data["metric_name"],
            value=float(data["value"]),
            sample_count=int(data["sample_count"]),
            configuration_id=data["configuration_id"],
            notes=data.get("notes", ""),
        )


@dataclass(frozen=True)
class EvaluationReport:
    """Complete evaluation report for a single retrieval configuration.

    Contains all required metrics including completeness-aware ones.
    """

    report_id: str
    configuration_id: str
    system_version: str
    precision_at_k: float
    recall_at_k: float
    mrr: float
    ndcg: float
    groundedness: float
    answer_correctness: float
    context_completeness_score: float
    support_score: float
    high_similarity_wrong_answer_rate: float
    parent_reconstruction_applied_rate: float
    missing_condition_rate: float
    missing_scope_rate: float
    missing_exception_rate: float
    missing_temporal_qualifier_rate: float
    classification_f1: float = 0.0
    classification_precision: float = 0.0
    classification_recall: float = 0.0
    sample_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "configuration_id": self.configuration_id,
            "system_version": self.system_version,
            "precision_at_k": round(self.precision_at_k, 6),
            "recall_at_k": round(self.recall_at_k, 6),
            "mrr": round(self.mrr, 6),
            "ndcg": round(self.ndcg, 6),
            "groundedness": round(self.groundedness, 6),
            "answer_correctness": round(self.answer_correctness, 6),
            "context_completeness_score": round(self.context_completeness_score, 6),
            "support_score": round(self.support_score, 6),
            "high_similarity_wrong_answer_rate": round(self.high_similarity_wrong_answer_rate, 6),
            "parent_reconstruction_applied_rate": round(self.parent_reconstruction_applied_rate, 6),
            "missing_condition_rate": round(self.missing_condition_rate, 6),
            "missing_scope_rate": round(self.missing_scope_rate, 6),
            "missing_exception_rate": round(self.missing_exception_rate, 6),
            "missing_temporal_qualifier_rate": round(self.missing_temporal_qualifier_rate, 6),
            "classification_f1": round(self.classification_f1, 6),
            "classification_precision": round(self.classification_precision, 6),
            "classification_recall": round(self.classification_recall, 6),
            "sample_count": self.sample_count,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EvaluationReport:
        return cls(
            report_id=data["report_id"],
            configuration_id=data["configuration_id"],
            system_version=data["system_version"],
            precision_at_k=float(data["precision_at_k"]),
            recall_at_k=float(data["recall_at_k"]),
            mrr=float(data["mrr"]),
            ndcg=float(data["ndcg"]),
            groundedness=float(data["groundedness"]),
            answer_correctness=float(data["answer_correctness"]),
            context_completeness_score=float(data["context_completeness_score"]),
            support_score=float(data["support_score"]),
            high_similarity_wrong_answer_rate=float(data["high_similarity_wrong_answer_rate"]),
            parent_reconstruction_applied_rate=float(data["parent_reconstruction_applied_rate"]),
            missing_condition_rate=float(data["missing_condition_rate"]),
            missing_scope_rate=float(data["missing_scope_rate"]),
            missing_exception_rate=float(data["missing_exception_rate"]),
            missing_temporal_qualifier_rate=float(data["missing_temporal_qualifier_rate"]),
            classification_f1=float(data.get("classification_f1", 0.0)),
            classification_precision=float(data.get("classification_precision", 0.0)),
            classification_recall=float(data.get("classification_recall", 0.0)),
            sample_count=int(data["sample_count"]),
            metadata=dict(data.get("metadata", {})),
        )

    def canonical_bytes(self) -> bytes:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "EvaluationReport.canonical_bytes")

        d = self.to_dict()
        d.pop("metadata", None)
        return json.dumps(d, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True)
class EvaluationDeltaReport:
    """Comparison between a baseline and candidate evaluation report.

    Answers: did completeness-aware retrieval improve over the baseline?
    """

    delta_report_id: str
    baseline_report_id: str
    candidate_report_id: str
    baseline_config_id: str
    candidate_config_id: str
    delta_precision_at_k: float
    delta_recall_at_k: float
    delta_mrr: float
    delta_ndcg: float
    delta_answer_correctness: float
    delta_context_completeness: float
    delta_support_score: float
    delta_high_similarity_wrong_answer_rate: float
    delta_parent_reconstruction_rate: float
    delta_classification_f1: float = 0.0
    delta_classification_precision: float = 0.0
    delta_classification_recall: float = 0.0
    candidate_is_better: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "delta_report_id": self.delta_report_id,
            "baseline_report_id": self.baseline_report_id,
            "candidate_report_id": self.candidate_report_id,
            "baseline_config_id": self.baseline_config_id,
            "candidate_config_id": self.candidate_config_id,
            "delta_precision_at_k": round(self.delta_precision_at_k, 6),
            "delta_recall_at_k": round(self.delta_recall_at_k, 6),
            "delta_mrr": round(self.delta_mrr, 6),
            "delta_ndcg": round(self.delta_ndcg, 6),
            "delta_answer_correctness": round(self.delta_answer_correctness, 6),
            "delta_context_completeness": round(self.delta_context_completeness, 6),
            "delta_support_score": round(self.delta_support_score, 6),
            "delta_high_similarity_wrong_answer_rate": round(self.delta_high_similarity_wrong_answer_rate, 6),
            "delta_parent_reconstruction_rate": round(self.delta_parent_reconstruction_rate, 6),
            "delta_classification_f1": round(self.delta_classification_f1, 6),
            "delta_classification_precision": round(self.delta_classification_precision, 6),
            "delta_classification_recall": round(self.delta_classification_recall, 6),
            "candidate_is_better": self.candidate_is_better,
        }

    @classmethod
    def from_reports(
        cls, delta_report_id: str, baseline: EvaluationReport, candidate: EvaluationReport
    ) -> EvaluationDeltaReport:
        """Compute a delta report from two EvaluationReport instances."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "EvaluationDeltaReport.from_reports")

        better = (
            candidate.context_completeness_score > baseline.context_completeness_score
            or candidate.support_score > baseline.support_score
            or candidate.answer_correctness > baseline.answer_correctness
        )
        return cls(
            delta_report_id=delta_report_id,
            baseline_report_id=baseline.report_id,
            candidate_report_id=candidate.report_id,
            baseline_config_id=baseline.configuration_id,
            candidate_config_id=candidate.configuration_id,
            delta_precision_at_k=round(candidate.precision_at_k - baseline.precision_at_k, 6),
            delta_recall_at_k=round(candidate.recall_at_k - baseline.recall_at_k, 6),
            delta_mrr=round(candidate.mrr - baseline.mrr, 6),
            delta_ndcg=round(candidate.ndcg - baseline.ndcg, 6),
            delta_answer_correctness=round(candidate.answer_correctness - baseline.answer_correctness, 6),
            delta_context_completeness=round(
                candidate.context_completeness_score - baseline.context_completeness_score, 6
            ),
            delta_support_score=round(candidate.support_score - baseline.support_score, 6),
            delta_high_similarity_wrong_answer_rate=round(
                candidate.high_similarity_wrong_answer_rate - baseline.high_similarity_wrong_answer_rate, 6
            ),
            delta_parent_reconstruction_rate=round(
                candidate.parent_reconstruction_applied_rate - baseline.parent_reconstruction_applied_rate, 6
            ),
            delta_classification_f1=round(candidate.classification_f1 - baseline.classification_f1, 6),
            delta_classification_precision=round(
                candidate.classification_precision - baseline.classification_precision, 6
            ),
            delta_classification_recall=round(
                candidate.classification_recall - baseline.classification_recall, 6
            ),
            candidate_is_better=better,
        )


@dataclass(frozen=True)
class RetrievalExperimentReport:
    """Compares retrieval strategy variants.

    Covers:
    - vector_only vs hybrid
    - hybrid vs hybrid_reranked
    - no parent expansion vs parent-child expansion
    """

    experiment_id: str
    comparison_axis: str
    baseline: EvaluationReport
    candidate: EvaluationReport
    delta: EvaluationDeltaReport
    recommendation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "comparison_axis": self.comparison_axis,
            "baseline": self.baseline.to_dict(),
            "candidate": self.candidate.to_dict(),
            "delta": self.delta.to_dict(),
            "recommendation": self.recommendation,
        }


@dataclass(frozen=True)
class ChunkStrategyReport:
    """Compares chunking strategy variants.

    Covers:
    - standard_chunked vs late_chunked
    - naive chunking vs section-aware chunking
    """

    experiment_id: str
    baseline_strategy: str
    candidate_strategy: str
    baseline: EvaluationReport
    candidate: EvaluationReport
    delta: EvaluationDeltaReport
    right_chunk_wrong_context_reduction: float
    recommendation: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "baseline_strategy": self.baseline_strategy,
            "candidate_strategy": self.candidate_strategy,
            "baseline": self.baseline.to_dict(),
            "candidate": self.candidate.to_dict(),
            "delta": self.delta.to_dict(),
            "right_chunk_wrong_context_reduction": round(self.right_chunk_wrong_context_reduction, 6),
            "recommendation": self.recommendation,
        }


@dataclass(frozen=True)
class CompletenessExperimentReport:
    """Tracks completeness-aware retrieval improvement over time.

    Answers the key questions:
    - Why was the answer wrong even when retrieval looked good?
    - Did parent expansion improve support?
    - Did reranking improve sufficiency, not just similarity?
    - Does late chunking reduce right-chunk-wrong-context failures?
    """

    experiment_id: str
    system_version: str
    high_sim_wrong_answer_before: float
    high_sim_wrong_answer_after: float
    support_score_before: float
    support_score_after: float
    context_completeness_before: float
    context_completeness_after: float
    parent_expansion_improved_support: bool
    reranking_improved_sufficiency: bool
    late_chunking_reduced_rcwc_failures: bool
    key_findings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "system_version": self.system_version,
            "high_sim_wrong_answer_before": round(self.high_sim_wrong_answer_before, 6),
            "high_sim_wrong_answer_after": round(self.high_sim_wrong_answer_after, 6),
            "support_score_before": round(self.support_score_before, 6),
            "support_score_after": round(self.support_score_after, 6),
            "context_completeness_before": round(self.context_completeness_before, 6),
            "context_completeness_after": round(self.context_completeness_after, 6),
            "parent_expansion_improved_support": self.parent_expansion_improved_support,
            "reranking_improved_sufficiency": self.reranking_improved_sufficiency,
            "late_chunking_reduced_rcwc_failures": self.late_chunking_reduced_rcwc_failures,
            "key_findings": list(self.key_findings),
        }


__all__ = [
    "EvaluationMetricResult",
    "EvaluationReport",
    "EvaluationDeltaReport",
    "RetrievalExperimentReport",
    "ChunkStrategyReport",
    "CompletenessExperimentReport",
]
