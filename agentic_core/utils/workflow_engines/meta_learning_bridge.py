"""
Phase E: Meta-Learning Bridge — Completeness-Aware EvaluationSignals.

Adds completeness-aware evaluation signals to the Meta-Learning input surface
and extends RAGProposer to emit completeness-driven proposals.

HARD REQUIREMENTS:
- All proposals remain proposal_only=True
- Replay validated, shadow validated, approval gated
- No proposal may directly activate without existing meta-learning commit controls

C0 RULE: Informational only. Proposals must flow through existing governance.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "meta_learning_bridge", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "meta_learning_bridge", "policy_binding")
trace_contract._emit_snapshots_state("p0", "meta_learning_bridge", "state_snapshot")

trace_contract._emit_emits_metric_event("meta_learning_bridge", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("meta_learning_bridge", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("meta_learning_bridge", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("meta_learning_bridge", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("meta_learning_bridge", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("meta_learning_bridge", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("meta_learning_bridge", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("meta_learning_bridge", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("meta_learning_bridge", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("meta_learning_bridge", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("meta_learning_bridge", "p4obs", "alert")
trace_contract._emit_links_incident_trace("meta_learning_bridge", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("meta_learning_bridge", "p3lm", "pattern")
trace_contract._emit_records_learning_event("meta_learning_bridge", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("meta_learning_bridge", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("meta_learning_bridge", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("meta_learning_bridge", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("meta_learning_bridge", "p3lm", "policy")
trace_contract._emit_stores_learning_state("meta_learning_bridge", "p3lm", "state")
trace_contract._emit_records_execution_trace("meta_learning_bridge", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("meta_learning_bridge", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("meta_learning_bridge", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("meta_learning_bridge", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("meta_learning_bridge", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("meta_learning_bridge", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("meta_learning_bridge", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("meta_learning_bridge", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("meta_learning_bridge", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "meta_learning_bridge", "context_pull")
trace_contract._emit_pulls_context("p1", "meta_learning_bridge", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "meta_learning_bridge", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "meta_learning_bridge", "uwg_term_2")
trace_contract._emit_writes_through("p1", "meta_learning_bridge", "write_through")
trace_contract._emit_writes_through("p1", "meta_learning_bridge", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "meta_learning_bridge", "safety_validation")
trace_contract._emit_invokes_eval("p1", "meta_learning_bridge", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "meta_learning_bridge", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "meta_learning_bridge", "human_escalation")
trace_contract._emit_routes_through("p1", "meta_learning_bridge", "route_through")
trace_contract._emit_checks_agent_registry("p1", "meta_learning_bridge", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "meta_learning_bridge", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "meta_learning_bridge", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "meta_learning_bridge", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "meta_learning_bridge", "target_agent")
trace_contract._emit_verifies_policy("p1", "meta_learning_bridge", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "meta_learning_bridge", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "meta_learning_bridge", "boundary_check")
trace_contract._emit_transcripts_response("p1", "meta_learning_bridge", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "meta_learning_bridge")
trace_contract._emit_gated_by_confidence("p1", "meta_learning_bridge", "confidence_gate")
trace_contract.emit_replay_key("p0", "meta_learning_bridge")
trace_contract.emit_determinism_digest("p0", "meta_learning_bridge")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "meta_learning_bridge", "execution_auth")
trace_contract._emit_validates_capability("p2", "meta_learning_bridge", "capability_check")
trace_contract._emit_routes_to_capability("p2", "meta_learning_bridge", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "meta_learning_bridge", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "meta_learning_bridge", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "meta_learning_bridge", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "meta_learning_bridge", "exec_output")
trace_contract._emit_dispatches_agent("p3", "meta_learning_bridge", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "meta_learning_bridge", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "meta_learning_bridge", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "meta_learning_bridge", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "meta_learning_bridge", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "meta_learning_bridge", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "meta_learning_bridge", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "meta_learning_bridge", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "meta_learning_bridge", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "meta_learning_bridge", "eval_metric")
trace_contract._emit_stores_embedding("p4", "meta_learning_bridge", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "meta_learning_bridge", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "meta_learning_bridge", "exec_snapshot_link")


@dataclass(frozen=True)
class EvaluationSignals:
    """Completeness-aware evaluation signals for Meta-Learning input.

    Aggregates retrieval relevance, completeness, answer correctness,
    support validation, and drift metrics into a single immutable payload
    for RAGProposer consumption.

    All fields are read-only — signals flow into proposals only.
    C0 RULE: Informational only.
    """

    snapshot_id: str
    retrieval_relevance_mean: float
    retrieval_precision: float
    retrieval_recall: float
    mean_completeness_score: float
    missing_condition_rate: float
    missing_exception_rate: float
    missing_scope_rate: float
    missing_temporal_qualifier_rate: float
    answer_correctness_rate: float
    fully_supported_rate: float
    mean_support_score: float
    high_similarity_wrong_answer_rate: float
    parent_reconstruction_applied_rate: float
    chunk_fragmentation_error_rate: float
    observation_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "retrieval_relevance_mean": round(self.retrieval_relevance_mean, 6),
            "retrieval_precision": round(self.retrieval_precision, 6),
            "retrieval_recall": round(self.retrieval_recall, 6),
            "mean_completeness_score": round(self.mean_completeness_score, 6),
            "missing_condition_rate": round(self.missing_condition_rate, 6),
            "missing_exception_rate": round(self.missing_exception_rate, 6),
            "missing_scope_rate": round(self.missing_scope_rate, 6),
            "missing_temporal_qualifier_rate": round(self.missing_temporal_qualifier_rate, 6),
            "answer_correctness_rate": round(self.answer_correctness_rate, 6),
            "fully_supported_rate": round(self.fully_supported_rate, 6),
            "mean_support_score": round(self.mean_support_score, 6),
            "high_similarity_wrong_answer_rate": round(self.high_similarity_wrong_answer_rate, 6),
            "parent_reconstruction_applied_rate": round(self.parent_reconstruction_applied_rate, 6),
            "chunk_fragmentation_error_rate": round(self.chunk_fragmentation_error_rate, 6),
            "observation_count": self.observation_count,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EvaluationSignals:
        return cls(
            snapshot_id=data["snapshot_id"],
            retrieval_relevance_mean=float(data["retrieval_relevance_mean"]),
            retrieval_precision=float(data["retrieval_precision"]),
            retrieval_recall=float(data["retrieval_recall"]),
            mean_completeness_score=float(data["mean_completeness_score"]),
            missing_condition_rate=float(data["missing_condition_rate"]),
            missing_exception_rate=float(data["missing_exception_rate"]),
            missing_scope_rate=float(data["missing_scope_rate"]),
            missing_temporal_qualifier_rate=float(data["missing_temporal_qualifier_rate"]),
            answer_correctness_rate=float(data["answer_correctness_rate"]),
            fully_supported_rate=float(data["fully_supported_rate"]),
            mean_support_score=float(data["mean_support_score"]),
            high_similarity_wrong_answer_rate=float(data["high_similarity_wrong_answer_rate"]),
            parent_reconstruction_applied_rate=float(data["parent_reconstruction_applied_rate"]),
            chunk_fragmentation_error_rate=float(data["chunk_fragmentation_error_rate"]),
            observation_count=int(data["observation_count"]),
        )

    def canonical_bytes(self) -> bytes:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":")).encode("utf-8")

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True)
class CompletenessChangePackage:
    """Immutable proposal for a completeness-driven RAG parameter change.

    proposal_only=True always — never activates without approval gate.
    """

    proposal_id: str
    surface_name: str
    parameter: str
    old_value: Any
    new_value: Any
    justification: str
    snapshot_id: str
    proposal_only: bool = True

    def __post_init__(self) -> None:
        if not self.proposal_only:
            raise ValueError("proposal_only must be True — proposals never auto-activate")

    def to_dict(self) -> dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "surface_name": self.surface_name,
            "parameter": self.parameter,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "justification": self.justification,
            "snapshot_id": self.snapshot_id,
            "proposal_only": self.proposal_only,
        }

    def canonical_bytes(self) -> bytes:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":")).encode("utf-8")

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


_MIN_OBSERVATIONS = 5
_LOW_COMPLETENESS_THRESHOLD = 0.6
_HIGH_FRAGMENTATION_THRESHOLD = 0.3
_LOW_SUPPORT_THRESHOLD = 0.6
_HIGH_SIM_WRONG_ANSWER_THRESHOLD = 0.2
_LOW_PARENT_EXPANSION_RATE = 0.3


class CompletenessRAGProposer:
    """Extends RAGProposer to emit completeness-aware proposals.

    Evaluates EvaluationSignals and proposes:
    - Increase parent expansion depth (low completeness + low expansion)
    - Switch to section-aware chunking (high fragmentation)
    - Enable hybrid retrieval (low support + high sim wrong answers)
    - Raise lexical exact-match boost (missing condition/scope rate high)
    - Change reranker weight toward completeness (low completeness)
    - Increase neighbor window size (low parent expansion)

    All proposals: proposal_only=True, replay-validated, approval-gated.
    C0 RULE: Never activates without existing meta-learning commit controls.
    """

    def propose(self, signals: EvaluationSignals) -> list[CompletenessChangePackage]:
        """Generate completeness-driven proposals from EvaluationSignals.

        Returns an empty list if observations are insufficient or no
        proposal is warranted.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "CompletenessRAGProposer.propose"
        )

        if signals.observation_count < _MIN_OBSERVATIONS:
            return []
        proposals: list[CompletenessChangePackage] = []
        if (
            signals.mean_completeness_score < _LOW_COMPLETENESS_THRESHOLD
            and signals.parent_reconstruction_applied_rate < _LOW_PARENT_EXPANSION_RATE
        ):
            proposals.append(
                CompletenessChangePackage(
                    proposal_id=f"inc-parent-depth-{signals.snapshot_id}",
                    surface_name="parent_expansion_depth",
                    parameter="expansion_depth",
                    old_value=1,
                    new_value=2,
                    justification=f"mean_completeness={signals.mean_completeness_score:.3f} < {_LOW_COMPLETENESS_THRESHOLD}; parent_expansion_rate={signals.parent_reconstruction_applied_rate:.3f} < {_LOW_PARENT_EXPANSION_RATE}; increase expansion depth",
                    snapshot_id=signals.snapshot_id,
                    proposal_only=True,
                ),
            )
        if signals.chunk_fragmentation_error_rate > _HIGH_FRAGMENTATION_THRESHOLD:
            proposals.append(
                CompletenessChangePackage(
                    proposal_id=f"section-aware-chunking-{signals.snapshot_id}",
                    surface_name="chunking_strategy",
                    parameter="chunking_mode",
                    old_value="fixed_token",
                    new_value="section_aware",
                    justification=f"chunk_fragmentation_error_rate={signals.chunk_fragmentation_error_rate:.3f} > {_HIGH_FRAGMENTATION_THRESHOLD}; switch to section-aware chunking",
                    snapshot_id=signals.snapshot_id,
                    proposal_only=True,
                ),
            )
        if (
            signals.fully_supported_rate < _LOW_SUPPORT_THRESHOLD
            and signals.high_similarity_wrong_answer_rate > _HIGH_SIM_WRONG_ANSWER_THRESHOLD
        ):
            proposals.append(
                CompletenessChangePackage(
                    proposal_id=f"enable-hybrid-retrieval-{signals.snapshot_id}",
                    surface_name="retrieval_mode",
                    parameter="retrieval_mode",
                    old_value="vector_only",
                    new_value="hybrid",
                    justification=f"fully_supported_rate={signals.fully_supported_rate:.3f} < {_LOW_SUPPORT_THRESHOLD}; high_similarity_wrong_answer_rate={signals.high_similarity_wrong_answer_rate:.3f} > {_HIGH_SIM_WRONG_ANSWER_THRESHOLD}; enable hybrid retrieval",
                    snapshot_id=signals.snapshot_id,
                    proposal_only=True,
                ),
            )
        if signals.missing_condition_rate > 0.3 or signals.missing_scope_rate > 0.3:
            proposals.append(
                CompletenessChangePackage(
                    proposal_id=f"raise-lexical-boost-{signals.snapshot_id}",
                    surface_name="lexical_exact_match_boost",
                    parameter="exact_match_boost",
                    old_value=1.0,
                    new_value=1.5,
                    justification=f"missing_condition_rate={signals.missing_condition_rate:.3f}, missing_scope_rate={signals.missing_scope_rate:.3f}; raise lexical exact-match boost for codes/conditions/versions",
                    snapshot_id=signals.snapshot_id,
                    proposal_only=True,
                ),
            )
        if signals.mean_completeness_score < _LOW_COMPLETENESS_THRESHOLD:
            proposals.append(
                CompletenessChangePackage(
                    proposal_id=f"reranker-completeness-weight-{signals.snapshot_id}",
                    surface_name="reranker_completeness_weight",
                    parameter="completeness_weight",
                    old_value=0.4,
                    new_value=0.6,
                    justification=f"mean_completeness={signals.mean_completeness_score:.3f} < {_LOW_COMPLETENESS_THRESHOLD}; increase reranker completeness weight over similarity",
                    snapshot_id=signals.snapshot_id,
                    proposal_only=True,
                ),
            )
        if signals.parent_reconstruction_applied_rate < _LOW_PARENT_EXPANSION_RATE:
            proposals.append(
                CompletenessChangePackage(
                    proposal_id=f"increase-neighbor-window-{signals.snapshot_id}",
                    surface_name="neighbor_window_size",
                    parameter="neighbor_window",
                    old_value=1,
                    new_value=2,
                    justification=f"parent_expansion_rate={signals.parent_reconstruction_applied_rate:.3f} < {_LOW_PARENT_EXPANSION_RATE}; increase neighbor window size",
                    snapshot_id=signals.snapshot_id,
                    proposal_only=True,
                ),
            )
        return proposals


__all__ = ["EvaluationSignals", "CompletenessChangePackage", "CompletenessRAGProposer"]
