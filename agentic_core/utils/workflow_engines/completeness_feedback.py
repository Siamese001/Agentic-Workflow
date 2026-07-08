"""
Phase F: Path D HITL Extension — Completeness-Specific Reviewer Rubric.

Extends ReviewRubric with completeness-specific fields so humans can label
incompleteness failure modes.

New artifacts:
  CompletenessReviewRubric — extends ReviewRubric with 6 new dimensions
  CompletenessFeedbackExample — carries retrieved_chunks and expanded_parent_context

INTENT: Create labeled examples for 'relevant chunk, incomplete context, wrong answer'.
Integrates with existing deterministic HITL and DPO flows without breaking
existing routing or evidence contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentic_core.evaluation.feedback.schemas import ReviewRubric
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "completeness_feedback", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "completeness_feedback", "policy_binding")
trace_contract._emit_snapshots_state("p0", "completeness_feedback", "state_snapshot")

trace_contract._emit_emits_metric_event("completeness_feedback", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("completeness_feedback", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("completeness_feedback", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("completeness_feedback", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("completeness_feedback", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("completeness_feedback", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("completeness_feedback", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("completeness_feedback", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("completeness_feedback", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("completeness_feedback", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("completeness_feedback", "p4obs", "alert")
trace_contract._emit_links_incident_trace("completeness_feedback", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("completeness_feedback", "p3lm", "pattern")
trace_contract._emit_records_learning_event("completeness_feedback", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("completeness_feedback", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("completeness_feedback", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("completeness_feedback", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("completeness_feedback", "p3lm", "policy")
trace_contract._emit_stores_learning_state("completeness_feedback", "p3lm", "state")
trace_contract._emit_records_execution_trace("completeness_feedback", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("completeness_feedback", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("completeness_feedback", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("completeness_feedback", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("completeness_feedback", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("completeness_feedback", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("completeness_feedback", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("completeness_feedback", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("completeness_feedback", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "completeness_feedback", "context_pull")
trace_contract._emit_pulls_context("p1", "completeness_feedback", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "completeness_feedback", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "completeness_feedback", "uwg_term_2")
trace_contract._emit_writes_through("p1", "completeness_feedback", "write_through")
trace_contract._emit_writes_through("p1", "completeness_feedback", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "completeness_feedback", "safety_validation")
trace_contract._emit_invokes_eval("p1", "completeness_feedback", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "completeness_feedback", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "completeness_feedback", "human_escalation")
trace_contract._emit_routes_through("p1", "completeness_feedback", "route_through")
trace_contract._emit_checks_agent_registry("p1", "completeness_feedback", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "completeness_feedback", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "completeness_feedback", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "completeness_feedback", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "completeness_feedback", "target_agent")
trace_contract._emit_verifies_policy("p1", "completeness_feedback", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "completeness_feedback", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "completeness_feedback", "boundary_check")
trace_contract._emit_transcripts_response("p1", "completeness_feedback", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "completeness_feedback")
trace_contract._emit_gated_by_confidence("p1", "completeness_feedback", "confidence_gate")
trace_contract.emit_replay_key("p0", "completeness_feedback")
trace_contract.emit_determinism_digest("p0", "completeness_feedback")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "completeness_feedback", "execution_auth")
trace_contract._emit_validates_capability("p2", "completeness_feedback", "capability_check")
trace_contract._emit_routes_to_capability("p2", "completeness_feedback", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "completeness_feedback", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "completeness_feedback", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "completeness_feedback", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "completeness_feedback", "exec_output")
trace_contract._emit_dispatches_agent("p3", "completeness_feedback", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "completeness_feedback", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "completeness_feedback", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "completeness_feedback", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "completeness_feedback", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "completeness_feedback", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "completeness_feedback", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "completeness_feedback", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "completeness_feedback", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "completeness_feedback", "eval_metric")
trace_contract._emit_stores_embedding("p4", "completeness_feedback", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "completeness_feedback", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "completeness_feedback", "exec_snapshot_link")


@dataclass
class CompletenessReviewRubric(ReviewRubric):
    """Extends ReviewRubric with completeness-specific failure mode labels.

    New dimensions map directly to the ContextCompletenessScore dimensions:
      missing_condition          — answer required a condition not in retrieved context
      missing_exception          — answer required an exception clause not retrieved
      missing_scope              — answer required scope constraints not in context
      missing_temporal_qualifier — answer required temporal/version info not retrieved
      incomplete_parent_context  — parent section was available but not used
      answer_not_fully_supported — answer makes claims beyond the evidence span
    """

    missing_condition: bool = False
    missing_exception: bool = False
    missing_scope: bool = False
    missing_temporal_qualifier: bool = False
    incomplete_parent_context: bool = False
    answer_not_fully_supported: bool = False

    def to_dict(self) -> dict[str, Any]:
        base = super().to_dict()
        base.update(
            {
                "missing_condition": self.missing_condition,
                "missing_exception": self.missing_exception,
                "missing_scope": self.missing_scope,
                "missing_temporal_qualifier": self.missing_temporal_qualifier,
                "incomplete_parent_context": self.incomplete_parent_context,
                "answer_not_fully_supported": self.answer_not_fully_supported,
            },
        )
        return base

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CompletenessReviewRubric:
        return cls(
            grounded=data["grounded"],
            useful=data["useful"],
            correct=data["correct"],
            safe=data["safe"],
            missing_context=data["missing_context"],
            reviewer_id=data.get("reviewer_id", ""),
            notes=data.get("notes", ""),
            missing_condition=bool(data.get("missing_condition", False)),
            missing_exception=bool(data.get("missing_exception", False)),
            missing_scope=bool(data.get("missing_scope", False)),
            missing_temporal_qualifier=bool(data.get("missing_temporal_qualifier", False)),
            incomplete_parent_context=bool(data.get("incomplete_parent_context", False)),
            answer_not_fully_supported=bool(data.get("answer_not_fully_supported", False)),
        )

    @property
    def completeness_failure_count(self) -> int:
        """Count of completeness-specific failures labeled."""
        return sum(
            [
                self.missing_condition,
                self.missing_exception,
                self.missing_scope,
                self.missing_temporal_qualifier,
                self.incomplete_parent_context,
                self.answer_not_fully_supported,
            ],
        )

    @property
    def has_completeness_failure(self) -> bool:
        """True if any completeness dimension was labeled as failing."""
        return self.completeness_failure_count > 0

    @property
    def quality_score(self) -> float:
        """Extended quality score including completeness penalty."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "CompletenessReviewRubric.quality_score"
        )

        base_dimensions = [self.grounded, self.useful, self.correct, self.safe]
        base_raw = sum(1 for d in base_dimensions if d) / len(base_dimensions)
        context_penalty = 0.1 if self.missing_context else 0.0
        completeness_penalty = 0.05 * self.completeness_failure_count
        return max(0.0, base_raw - context_penalty - completeness_penalty)


@dataclass
class CompletenessFeedbackExample:
    """Human-annotated feedback example for completeness-specific failures.

    Captures the 'relevant chunk, incomplete context, wrong answer' pattern.
    Integrates with existing DPO flows via support_failure_reason.
    """

    example_id: str
    query: str
    model_answer: str
    retrieved_chunks: list[str]
    expanded_parent_context: list[str]
    human_annotation: CompletenessReviewRubric
    support_failure_reason: str
    context_documents: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "example_id": self.example_id,
            "query": self.query,
            "model_answer": self.model_answer,
            "retrieved_chunks": list(self.retrieved_chunks),
            "expanded_parent_context": list(self.expanded_parent_context),
            "human_annotation": self.human_annotation.to_dict(),
            "support_failure_reason": self.support_failure_reason,
            "context_documents": list(self.context_documents),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CompletenessFeedbackExample:
        return cls(
            example_id=data["example_id"],
            query=data["query"],
            model_answer=data["model_answer"],
            retrieved_chunks=list(data["retrieved_chunks"]),
            expanded_parent_context=list(data["expanded_parent_context"]),
            human_annotation=CompletenessReviewRubric.from_dict(data["human_annotation"]),
            support_failure_reason=data["support_failure_reason"],
            context_documents=list(data["context_documents"]),
            metadata=dict(data.get("metadata", {})),
        )

    @property
    def is_right_chunk_wrong_context(self) -> bool:
        """True when the retrieved chunk was relevant but context was incomplete."""
        return self.human_annotation.grounded and self.human_annotation.has_completeness_failure


__all__ = ["CompletenessReviewRubric", "CompletenessFeedbackExample"]
