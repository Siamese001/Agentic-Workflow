"""
Phase 5: Human Feedback Schemas

Defines ReviewRubric, FeedbackExample, and DPO pair structures.
"""

from __future__ import annotations

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

_emit_applies_guardrail("p0", "schemas", "p0_governance")
_emit_reads_policy_state("p0", "schemas", "policy_binding")
_emit_snapshots_state("p0", "schemas", "state_snapshot")
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

_emit_emits_metric_event("schemas", "p4obs", "metric_1")
_emit_emits_metric_event("schemas", "p4obs", "metric_2")
_emit_emits_metric_event("schemas", "p4obs", "metric_3")
_emit_emits_metric_event("schemas", "p4obs", "metric_4")
_emit_emits_metric_event("schemas", "p4obs", "metric_5")
_emit_emits_metric_event("schemas", "p4obs", "metric_6")
_emit_records_incident_event("schemas", "p4obs", "incident")
_emit_captures_runtime_anomaly("schemas", "p4obs", "anomaly")
_emit_writes_observability_log("schemas", "p4obs", "obs_log")
_emit_updates_monitoring_state("schemas", "p4obs", "mon_state")
_emit_triggers_alert("schemas", "p4obs", "alert")
_emit_links_incident_trace("schemas", "p4obs", "trace_link")
_emit_captures_pattern("schemas", "p3lm", "pattern")
_emit_records_learning_event("schemas", "p3lm", "learning_event")
_emit_writes_learning_snapshot("schemas", "p3lm", "snapshot")
_emit_feeds_meta_learning("schemas", "p3lm", "meta_feed")
_emit_updates_routing_strategy("schemas", "p3lm", "routing")
_emit_improves_agent_policy("schemas", "p3lm", "policy")
_emit_stores_learning_state("schemas", "p3lm", "state")
_emit_records_execution_trace("schemas", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("schemas", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("schemas", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("schemas", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("schemas", "L4_STATE", "p2_trace_5")
_emit_reads_environ("schemas", "env_read", "p2_env_1")
_emit_reads_environ("schemas", "env_read", "p2_env_2")
_emit_reads_runtime_state("schemas", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("schemas", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "schemas", "context_pull")
_emit_pulls_context("p1", "schemas", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "schemas", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "schemas", "uwg_term_2")
_emit_writes_through("p1", "schemas", "write_through")
_emit_writes_through("p1", "schemas", "write_through_2")
_emit_validated_by_safety_plane("p1", "schemas", "safety_validation")
_emit_invokes_eval("p1", "schemas", "eval_call")
_emit_proposal_commits_routing("p1", "schemas", "routing_commit")
_emit_escalates_to_human("p1", "schemas", "human_escalation")
_emit_routes_through("p1", "schemas", "route_through")
_emit_checks_agent_registry("p1", "schemas", "agent_registry")
_emit_validates_agent_capability("p1", "schemas", "capability")
_emit_dispatches_execution_plan("p1", "schemas", "exec_plan")
_emit_agent_executes_agent("p1", "schemas", "sub_agent")
_emit_routes_to_agent("p1", "schemas", "target_agent")
_emit_verifies_policy("p1", "schemas", "policy_check")
_emit_observes_runtime_state("p1", "schemas", "runtime_state")
_emit_verifies_boundary("p1", "schemas", "boundary_check")
_emit_transcripts_response("p1", "schemas", "transcript")
_emit_hard_fails_untranscripted("p1", "schemas")
_emit_gated_by_confidence("p1", "schemas", "confidence_gate")
emit_replay_key("p0", "schemas")
emit_determinism_digest("p0", "schemas")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "schemas", "execution_auth")
_emit_validates_capability("p2", "schemas", "capability_check")
_emit_routes_to_capability("p2", "schemas", "capability_route")
_emit_writes_via_uwg("p2", "schemas", "uwg_write")
_emit_blocks_direct_write("p2", "schemas", "direct_write_block")
_emit_records_tool_invocation("p2", "schemas", "tool_invocation")
_emit_captures_execution_output("p2", "schemas", "exec_output")
_emit_dispatches_agent("p3", "schemas", "agent_dispatch")
_emit_coordinates_agents("p3", "schemas", "agent_coordination")
_emit_records_workflow_lineage("p3", "schemas", "workflow_lineage")
_emit_records_healing_outcome("p3", "schemas", "healing_outcome")
_emit_escalates_failure("p3", "schemas", "failure_escalation")
_emit_orchestrates_workflow("p3", "schemas", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "schemas", "healing_dispatch")
_emit_invokes_evaluation("p3", "schemas", "evaluation_signal")
_emit_records_telemetry_event("p4", "schemas", "telemetry_event")
_emit_captures_evaluation_metric("p4", "schemas", "eval_metric")
_emit_stores_embedding("p4", "schemas", "embedding_store")
_emit_updates_meta_learning_state("p4", "schemas", "meta_learning")
_emit_links_execution_to_snapshot("p4", "schemas", "exec_snapshot_link")


@dataclass
class ReviewRubric:
    """Human review rubric for a single model response."""

    grounded: bool
    useful: bool
    correct: bool
    safe: bool
    missing_context: bool
    reviewer_id: str = ""
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "grounded": self.grounded,
            "useful": self.useful,
            "correct": self.correct,
            "safe": self.safe,
            "missing_context": self.missing_context,
            "reviewer_id": self.reviewer_id,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ReviewRubric:
        return cls(
            grounded=data["grounded"],
            useful=data["useful"],
            correct=data["correct"],
            safe=data["safe"],
            missing_context=data["missing_context"],
            reviewer_id=data.get("reviewer_id", ""),
            notes=data.get("notes", ""),
        )

    @property
    def is_positive(self) -> bool:
        """True if the review is overall positive (all critical dimensions pass)."""
        return self.grounded and self.useful and self.correct and self.safe

    @property
    def quality_score(self) -> float:
        """Numeric quality score [0.0, 1.0] computed from rubric dimensions."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ReviewRubric.quality_score")

        dimensions = [self.grounded, self.useful, self.correct, self.safe]
        penalty = 0.1 if self.missing_context else 0.0
        raw = sum(1 for d in dimensions if d) / len(dimensions)
        return max(0.0, raw - penalty)


@dataclass
class FeedbackExample:
    """A single human-annotated feedback example for training or evaluation."""

    example_id: str
    query: str
    model_answer: str
    human_annotation: ReviewRubric
    context_documents: list[str]
    timestamp: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "example_id": self.example_id,
            "query": self.query,
            "model_answer": self.model_answer,
            "human_annotation": self.human_annotation.to_dict(),
            "context_documents": self.context_documents,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FeedbackExample:
        return cls(
            example_id=data["example_id"],
            query=data["query"],
            model_answer=data["model_answer"],
            human_annotation=ReviewRubric.from_dict(data["human_annotation"]),
            context_documents=data["context_documents"],
            timestamp=data["timestamp"],
            metadata=data.get("metadata", {}),
        )


@dataclass(frozen=True)
class DPOPair:
    """A Direct Preference Optimization training pair (chosen vs rejected)."""

    pair_id: str
    query: str
    chosen_response: str
    rejected_response: str
    context_documents: list[str]
    chosen_score: float
    rejected_score: float
    source_example_ids: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "pair_id": self.pair_id,
            "query": self.query,
            "chosen_response": self.chosen_response,
            "rejected_response": self.rejected_response,
            "context_documents": list(self.context_documents),
            "chosen_score": self.chosen_score,
            "rejected_score": self.rejected_score,
            "source_example_ids": list(self.source_example_ids),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DPOPair:
        return cls(
            pair_id=data["pair_id"],
            query=data["query"],
            chosen_response=data["chosen_response"],
            rejected_response=data["rejected_response"],
            context_documents=data["context_documents"],
            chosen_score=data["chosen_score"],
            rejected_score=data["rejected_score"],
            source_example_ids=data["source_example_ids"],
            metadata=data.get("metadata", {}),
        )


@dataclass(frozen=True)
class DPOBatch:
    """A batch of DPO training pairs ready for fine-tuning."""

    batch_id: str
    timestamp: str
    pair_count: int
    pairs: list[DPOPair]
    source_feedback_count: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "batch_id": self.batch_id,
            "timestamp": self.timestamp,
            "pair_count": self.pair_count,
            "pairs": [p.to_dict() for p in self.pairs],
            "source_feedback_count": self.source_feedback_count,
            "metadata": dict(self.metadata),
        }


__all__ = ["ReviewRubric", "FeedbackExample", "DPOPair", "DPOBatch"]
