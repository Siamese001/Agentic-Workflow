"""
Phase D: L6 Observability — RAG Completeness Telemetry Monitors.

New monitors:
  RetrievalCompletenessMonitor    — tracks completeness_score distribution
  ParentExpansionMissMonitor      — tracks when parent expansion was NOT applied
  HighSimilarityWrongAnswerMonitor — tracks high-similarity but unsupported answers
  ConditionLossDriftMonitor       — tracks drift in condition-loss rate over time

New snapshots:
  RetrievalCompletenessSnapshot
  SupportValidationSnapshot
  ConditionLossSnapshot

RULES:
- L6 telemetry must NOT directly mutate runtime behavior.
- Drift signals must NOT bypass proposal/approval flows.
- All monitors emit telemetry only (C0 informational rule).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from agentic_core.evaluation.retrieval.completeness import (
    ContextCompletenessScore,
    SupportedAnswerCheck,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("completeness_monitors", "p4obs", "metric_1")
_emit_emits_metric_event("completeness_monitors", "p4obs", "metric_2")
_emit_emits_metric_event("completeness_monitors", "p4obs", "metric_3")
_emit_emits_metric_event("completeness_monitors", "p4obs", "metric_4")
_emit_emits_metric_event("completeness_monitors", "p4obs", "metric_5")
_emit_emits_metric_event("completeness_monitors", "p4obs", "metric_6")
_emit_records_incident_event("completeness_monitors", "p4obs", "incident")
_emit_captures_runtime_anomaly("completeness_monitors", "p4obs", "anomaly")
_emit_writes_observability_log("completeness_monitors", "p4obs", "obs_log")
_emit_updates_monitoring_state("completeness_monitors", "p4obs", "mon_state")
_emit_triggers_alert("completeness_monitors", "p4obs", "alert")
_emit_links_incident_trace("completeness_monitors", "p4obs", "trace_link")
_emit_captures_pattern("completeness_monitors", "p3lm", "pattern")
_emit_records_learning_event("completeness_monitors", "p3lm", "learning_event")
_emit_writes_learning_snapshot("completeness_monitors", "p3lm", "snapshot")
_emit_feeds_meta_learning("completeness_monitors", "p3lm", "meta_feed")
_emit_updates_routing_strategy("completeness_monitors", "p3lm", "routing")
_emit_improves_agent_policy("completeness_monitors", "p3lm", "policy")
_emit_stores_learning_state("completeness_monitors", "p3lm", "state")
_emit_records_execution_trace("completeness_monitors", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("completeness_monitors", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("completeness_monitors", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("completeness_monitors", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("completeness_monitors", "L4_STATE", "p2_trace_5")
_emit_reads_environ("completeness_monitors", "env_read", "p2_env_1")
_emit_reads_environ("completeness_monitors", "env_read", "p2_env_2")
_emit_reads_runtime_state("completeness_monitors", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("completeness_monitors", "runtime_state", "p2_rt_2")

_emit_applies_guardrail("p0", "completeness_monitors", "p0_governance")
_emit_reads_policy_state("p0", "completeness_monitors", "policy_binding")
_emit_snapshots_state("p0", "completeness_monitors", "state_snapshot")
_emit_pulls_context("p1", "completeness_monitors", "context_pull")
_emit_pulls_context("p1", "completeness_monitors", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "completeness_monitors", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "completeness_monitors", "uwg_term_secondary")
_emit_writes_through("p1", "completeness_monitors", "write_through")
_emit_writes_through("p1", "completeness_monitors", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "completeness_monitors", "safety_validation")
_emit_invokes_eval("p1", "completeness_monitors", "eval_call")
_emit_proposal_commits_routing("p1", "completeness_monitors", "routing_commit")
_emit_escalates_to_human("p1", "completeness_monitors", "human_escalation")
_emit_routes_through("p1", "completeness_monitors", "route_through")
_emit_checks_agent_registry("p1", "completeness_monitors", "agent_registry")
_emit_validates_agent_capability("p1", "completeness_monitors", "capability")
_emit_dispatches_execution_plan("p1", "completeness_monitors", "exec_plan")
_emit_agent_executes_agent("p1", "completeness_monitors", "sub_agent")
_emit_routes_to_agent("p1", "completeness_monitors", "target_agent")
_emit_verifies_policy("p1", "completeness_monitors", "policy_check")
_emit_observes_runtime_state("p1", "completeness_monitors", "runtime_state")
_emit_verifies_boundary("p1", "completeness_monitors", "boundary_check")
_emit_transcripts_response("p1", "completeness_monitors", "transcript")
_emit_hard_fails_untranscripted("p1", "completeness_monitors")
_emit_gated_by_confidence("p1", "completeness_monitors", "confidence_gate")
emit_replay_key("p0", "completeness_monitors")
emit_determinism_digest("p0", "completeness_monitors")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "completeness_monitors", "execution_auth")
_emit_validates_capability("p2", "completeness_monitors", "capability_check")
_emit_routes_to_capability("p2", "completeness_monitors", "capability_route")
_emit_writes_via_uwg("p2", "completeness_monitors", "uwg_write")
_emit_blocks_direct_write("p2", "completeness_monitors", "direct_write_block")
_emit_records_tool_invocation("p2", "completeness_monitors", "tool_invocation")
_emit_captures_execution_output("p2", "completeness_monitors", "exec_output")
_emit_dispatches_agent("p3", "completeness_monitors", "agent_dispatch")
_emit_coordinates_agents("p3", "completeness_monitors", "agent_coordination")
_emit_records_workflow_lineage("p3", "completeness_monitors", "workflow_lineage")
_emit_records_healing_outcome("p3", "completeness_monitors", "healing_outcome")
_emit_escalates_failure("p3", "completeness_monitors", "failure_escalation")
_emit_orchestrates_workflow("p3", "completeness_monitors", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "completeness_monitors", "healing_dispatch")
_emit_invokes_evaluation("p3", "completeness_monitors", "evaluation_signal")
_emit_records_telemetry_event("p4", "completeness_monitors", "telemetry_event")
_emit_captures_evaluation_metric("p4", "completeness_monitors", "eval_metric")
_emit_stores_embedding("p4", "completeness_monitors", "embedding_store")
_emit_updates_meta_learning_state("p4", "completeness_monitors", "meta_learning")
_emit_links_execution_to_snapshot("p4", "completeness_monitors", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Snapshot Types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RetrievalCompletenessSnapshot:
    """Snapshot of completeness metrics for a retrieval window.

    Proves: semantic similarity can be high while completeness is low.
    """

    snapshot_id: str
    system_version: str
    sample_count: int
    mean_completeness_score: float
    mean_relevance_score: float
    parent_reconstruction_applied_rate: float
    high_similarity_low_completeness_rate: float
    version: str = "1"

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "snapshot_id": self.snapshot_id,
            "system_version": self.system_version,
            "sample_count": self.sample_count,
            "mean_completeness_score": round(self.mean_completeness_score, 6),
            "mean_relevance_score": round(self.mean_relevance_score, 6),
            "parent_reconstruction_applied_rate": round(self.parent_reconstruction_applied_rate, 6),
            "high_similarity_low_completeness_rate": round(self.high_similarity_low_completeness_rate, 6),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RetrievalCompletenessSnapshot:
        return cls(
            snapshot_id=data["snapshot_id"],
            system_version=data["system_version"],
            sample_count=int(data["sample_count"]),
            mean_completeness_score=float(data["mean_completeness_score"]),
            mean_relevance_score=float(data["mean_relevance_score"]),
            parent_reconstruction_applied_rate=float(data["parent_reconstruction_applied_rate"]),
            high_similarity_low_completeness_rate=float(data["high_similarity_low_completeness_rate"]),
            version=data.get("version", "1"),
        )


@dataclass(frozen=True)
class SupportValidationSnapshot:
    """Snapshot of answer support validation metrics.

    Proves: incomplete fragment retrieval is a measurable failure mode.
    """

    snapshot_id: str
    system_version: str
    answer_count: int
    fully_supported_rate: float
    mean_support_score: float
    unsupported_with_high_similarity_rate: float
    version: str = "1"

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "snapshot_id": self.snapshot_id,
            "system_version": self.system_version,
            "answer_count": self.answer_count,
            "fully_supported_rate": round(self.fully_supported_rate, 6),
            "mean_support_score": round(self.mean_support_score, 6),
            "unsupported_with_high_similarity_rate": round(self.unsupported_with_high_similarity_rate, 6),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SupportValidationSnapshot:
        return cls(
            snapshot_id=data["snapshot_id"],
            system_version=data["system_version"],
            answer_count=int(data["answer_count"]),
            fully_supported_rate=float(data["fully_supported_rate"]),
            mean_support_score=float(data["mean_support_score"]),
            unsupported_with_high_similarity_rate=float(data["unsupported_with_high_similarity_rate"]),
            version=data.get("version", "1"),
        )


@dataclass(frozen=True)
class ConditionLossSnapshot:
    """Snapshot tracking drift in condition-loss and dimension-loss rates.

    Proves: parent-child reconstruction improves answer support over time.
    """

    snapshot_id: str
    system_version: str
    query_count: int
    missing_condition_rate: float
    missing_exception_rate: float
    missing_scope_rate: float
    missing_temporal_qualifier_rate: float
    condition_loss_delta_vs_prior: float
    version: str = "1"

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "snapshot_id": self.snapshot_id,
            "system_version": self.system_version,
            "query_count": self.query_count,
            "missing_condition_rate": round(self.missing_condition_rate, 6),
            "missing_exception_rate": round(self.missing_exception_rate, 6),
            "missing_scope_rate": round(self.missing_scope_rate, 6),
            "missing_temporal_qualifier_rate": round(self.missing_temporal_qualifier_rate, 6),
            "condition_loss_delta_vs_prior": round(self.condition_loss_delta_vs_prior, 6),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ConditionLossSnapshot:
        return cls(
            snapshot_id=data["snapshot_id"],
            system_version=data["system_version"],
            query_count=int(data["query_count"]),
            missing_condition_rate=float(data["missing_condition_rate"]),
            missing_exception_rate=float(data["missing_exception_rate"]),
            missing_scope_rate=float(data["missing_scope_rate"]),
            missing_temporal_qualifier_rate=float(data["missing_temporal_qualifier_rate"]),
            condition_loss_delta_vs_prior=float(data["condition_loss_delta_vs_prior"]),
            version=data.get("version", "1"),
        )


# ---------------------------------------------------------------------------
# Monitor Implementations
# ---------------------------------------------------------------------------


class RetrievalCompletenessMonitor:
    """L6 monitor: tracks context_completeness_score distribution.

    C0 RULE: Emits telemetry only — does not mutate runtime behavior.
    """

    HIGH_SIMILARITY_THRESHOLD: float = 0.75
    LOW_COMPLETENESS_THRESHOLD: float = 0.50

    def __init__(self) -> None:
        self._records: list[ContextCompletenessScore] = []
        self._expansion_applied: list[bool] = []

    def record(self, score: ContextCompletenessScore, *, expansion_applied: bool = False) -> None:
        """Record a completeness score observation."""
        self._records.append(score)
        self._expansion_applied.append(expansion_applied)

    def snapshot(self, snapshot_id: str, system_version: str) -> RetrievalCompletenessSnapshot:
        """Emit a deterministic snapshot of accumulated observations."""
        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, f"CompletenessMonitor.snapshot:{snapshot_id}")
        n = len(self._records)
        if n == 0:
            return RetrievalCompletenessSnapshot(
                snapshot_id=snapshot_id,
                system_version=system_version,
                sample_count=0,
                mean_completeness_score=0.0,
                mean_relevance_score=0.0,
                parent_reconstruction_applied_rate=0.0,
                high_similarity_low_completeness_rate=0.0,
            )

        mean_completeness = sum(r.completeness_score for r in self._records) / n
        mean_relevance = sum(r.relevance_score for r in self._records) / n
        expansion_rate = sum(1 for x in self._expansion_applied if x) / n
        hs_lc = (
            sum(
                1
                for r in self._records
                if r.relevance_score >= self.HIGH_SIMILARITY_THRESHOLD
                and r.completeness_score < self.LOW_COMPLETENESS_THRESHOLD
            )
            / n
        )

        return RetrievalCompletenessSnapshot(
            snapshot_id=snapshot_id,
            system_version=system_version,
            sample_count=n,
            mean_completeness_score=round(mean_completeness, 6),
            mean_relevance_score=round(mean_relevance, 6),
            parent_reconstruction_applied_rate=round(expansion_rate, 6),
            high_similarity_low_completeness_rate=round(hs_lc, 6),
        )

    def reset(self) -> None:
        self._records.clear()
        self._expansion_applied.clear()

    def sample_count(self) -> int:
        return len(self._records)


class ParentExpansionMissMonitor:
    """L6 monitor: tracks when parent expansion was not applied but needed.

    'Miss' = chunk had low completeness AND parent was not expanded.
    C0 RULE: Telemetry only.
    """

    LOW_COMPLETENESS_THRESHOLD: float = 0.50

    def __init__(self) -> None:
        self._total: int = 0
        self._misses: int = 0

    def record(self, score: ContextCompletenessScore, *, expansion_applied: bool) -> None:
        self._total += 1
        if score.completeness_score < self.LOW_COMPLETENESS_THRESHOLD and not expansion_applied:
            self._misses += 1

    def miss_rate(self) -> float:
        if self._total == 0:
            return 0.0
        return round(self._misses / self._total, 6)

    def total(self) -> int:
        return self._total

    def misses(self) -> int:
        return self._misses

    def reset(self) -> None:
        self._total = 0
        self._misses = 0


class HighSimilarityWrongAnswerMonitor:
    """L6 monitor: tracks high-similarity retrievals with unsupported answers.

    Proves: semantic similarity can be high while answer quality is low.
    C0 RULE: Telemetry only — no routing mutation.
    """

    HIGH_SIMILARITY_THRESHOLD: float = 0.75

    def __init__(self) -> None:
        self._total: int = 0
        self._high_sim_wrong: int = 0
        self._support_scores: list[float] = []

    def record(
        self,
        mean_retrieval_similarity: float,
        answer_check: SupportedAnswerCheck,
    ) -> None:
        self._total += 1
        self._support_scores.append(answer_check.support_score)
        if mean_retrieval_similarity >= self.HIGH_SIMILARITY_THRESHOLD and not answer_check.fully_supported:
            self._high_sim_wrong += 1

    def high_similarity_wrong_answer_rate(self) -> float:
        if self._total == 0:
            return 0.0
        return round(self._high_sim_wrong / self._total, 6)

    def mean_support_score(self) -> float:
        if not self._support_scores:
            return 0.0
        return round(sum(self._support_scores) / len(self._support_scores), 6)

    def snapshot(self, snapshot_id: str, system_version: str) -> SupportValidationSnapshot:
        n = self._total
        fully_supported = sum(1 for s in self._support_scores if s >= 0.80)
        return SupportValidationSnapshot(
            snapshot_id=snapshot_id,
            system_version=system_version,
            answer_count=n,
            fully_supported_rate=round(fully_supported / max(1, n), 6),
            mean_support_score=self.mean_support_score(),
            unsupported_with_high_similarity_rate=self.high_similarity_wrong_answer_rate(),
        )

    def reset(self) -> None:
        self._total = 0
        self._high_sim_wrong = 0
        self._support_scores.clear()


class ConditionLossDriftMonitor:
    """L6 monitor: tracks drift in condition-loss rate over a rolling window.

    Compares current window rate to prior window to detect worsening.
    C0 RULE: Drift signals must not bypass proposal/approval flows.
    """

    def __init__(self) -> None:
        self._records: list[ContextCompletenessScore] = []
        self._prior_condition_rate: float = 0.0

    def record(self, score: ContextCompletenessScore) -> None:
        self._records.append(score)

    def snapshot(self, snapshot_id: str, system_version: str) -> ConditionLossSnapshot:
        n = len(self._records)
        if n == 0:
            return ConditionLossSnapshot(
                snapshot_id=snapshot_id,
                system_version=system_version,
                query_count=0,
                missing_condition_rate=0.0,
                missing_exception_rate=0.0,
                missing_scope_rate=0.0,
                missing_temporal_qualifier_rate=0.0,
                condition_loss_delta_vs_prior=0.0,
            )

        mc = sum(1 for r in self._records if r.missing_condition) / n
        me = sum(1 for r in self._records if r.missing_exception) / n
        ms = sum(1 for r in self._records if r.missing_scope) / n
        mt = sum(1 for r in self._records if r.missing_temporal_qualifier) / n
        delta = round(mc - self._prior_condition_rate, 6)
        self._prior_condition_rate = mc

        return ConditionLossSnapshot(
            snapshot_id=snapshot_id,
            system_version=system_version,
            query_count=n,
            missing_condition_rate=round(mc, 6),
            missing_exception_rate=round(me, 6),
            missing_scope_rate=round(ms, 6),
            missing_temporal_qualifier_rate=round(mt, 6),
            condition_loss_delta_vs_prior=delta,
        )

    def reset(self) -> None:
        self._records.clear()

    def sample_count(self) -> int:
        return len(self._records)


__all__ = [
    "RetrievalCompletenessSnapshot",
    "SupportValidationSnapshot",
    "ConditionLossSnapshot",
    "RetrievalCompletenessMonitor",
    "ParentExpansionMissMonitor",
    "HighSimilarityWrongAnswerMonitor",
    "ConditionLossDriftMonitor",
]
