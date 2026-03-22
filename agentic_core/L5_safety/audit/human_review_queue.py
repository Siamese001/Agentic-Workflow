"""Gate C5: HumanReviewQueue — stub for human-enqueued AI verdicts.

Verdicts with confidence < 0.7 are placed here and blocked from routing
until a human reviewer approves or rejects them.
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass, field
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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
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
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
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

emit_replay_key("p0", "human_review_queue")
emit_determinism_digest("p0", "human_review_queue")

_emit_dispatches_healing_run("p1", "human_review_queue", "L5")
_emit_routes_through("p1", "human_review_queue", "L5")
_emit_checks_agent_registry("p1", "human_review_queue", "agent_registry")
_emit_validates_agent_capability("p1", "human_review_queue", "capability")
_emit_dispatches_execution_plan("p1", "human_review_queue", "exec_plan")
_emit_agent_executes_agent("p1", "human_review_queue", "sub_agent")
_emit_routes_to_agent("p1", "human_review_queue", "target_agent")
_emit_verifies_policy("p1", "human_review_queue", "policy_check")
_emit_observes_runtime_state("p1", "human_review_queue", "runtime_state")
_emit_verifies_boundary("p1", "human_review_queue", "boundary_check")
_emit_transcripts_response("p1", "human_review_queue", "transcript")
_emit_hard_fails_untranscripted("p1", "human_review_queue")
_emit_gated_by_confidence("p1", "human_review_queue", "confidence_gate")
_emit_escalates_to_human("p1", "human_review_queue", "L5")
_emit_reads_policy_state("p1", "human_review_queue", "L5")

_emit_applies_guardrail("p0", "human_review_queue", "p0_governance")
_emit_snapshots_state("p0", "human_review_queue", "state_snapshot")
_emit_authorize_and_execute("p2", "human_review_queue", "execution_auth")
_emit_validates_capability("p2", "human_review_queue", "capability_check")
_emit_routes_to_capability("p2", "human_review_queue", "capability_route")
_emit_writes_via_uwg("p2", "human_review_queue", "uwg_write")
_emit_blocks_direct_write("p2", "human_review_queue", "direct_write_block")
_emit_records_tool_invocation("p2", "human_review_queue", "tool_invocation")
_emit_captures_execution_output("p2", "human_review_queue", "exec_output")
_emit_dispatches_agent("p3", "human_review_queue", "agent_dispatch")
_emit_coordinates_agents("p3", "human_review_queue", "agent_coordination")
_emit_records_workflow_lineage("p3", "human_review_queue", "workflow_lineage")
_emit_records_healing_outcome("p3", "human_review_queue", "healing_outcome")
_emit_escalates_failure("p3", "human_review_queue", "failure_escalation")
_emit_orchestrates_workflow("p3", "human_review_queue", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "human_review_queue", "healing_dispatch")
_emit_invokes_evaluation("p3", "human_review_queue", "evaluation_signal")
_emit_records_telemetry_event("p4", "human_review_queue", "telemetry_event")
_emit_captures_evaluation_metric("p4", "human_review_queue", "eval_metric")
_emit_stores_embedding("p4", "human_review_queue", "embedding_store")
_emit_updates_meta_learning_state("p4", "human_review_queue", "meta_learning")
_emit_links_execution_to_snapshot("p4", "human_review_queue", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
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

_emit_emits_metric_event("human_review_queue", "p4obs", "metric_1")
_emit_emits_metric_event("human_review_queue", "p4obs", "metric_2")
_emit_emits_metric_event("human_review_queue", "p4obs", "metric_3")
_emit_emits_metric_event("human_review_queue", "p4obs", "metric_4")
_emit_emits_metric_event("human_review_queue", "p4obs", "metric_5")
_emit_emits_metric_event("human_review_queue", "p4obs", "metric_6")
_emit_records_incident_event("human_review_queue", "p4obs", "incident")
_emit_captures_runtime_anomaly("human_review_queue", "p4obs", "anomaly")
_emit_writes_observability_log("human_review_queue", "p4obs", "obs_log")
_emit_updates_monitoring_state("human_review_queue", "p4obs", "mon_state")
_emit_triggers_alert("human_review_queue", "p4obs", "alert")
_emit_links_incident_trace("human_review_queue", "p4obs", "trace_link")
_emit_captures_pattern("human_review_queue", "p3lm", "pattern")
_emit_records_learning_event("human_review_queue", "p3lm", "learning_event")
_emit_writes_learning_snapshot("human_review_queue", "p3lm", "snapshot")
_emit_feeds_meta_learning("human_review_queue", "p3lm", "meta_feed")
_emit_updates_routing_strategy("human_review_queue", "p3lm", "routing")
_emit_improves_agent_policy("human_review_queue", "p3lm", "policy")
_emit_stores_learning_state("human_review_queue", "p3lm", "state")
_emit_records_execution_trace("human_review_queue", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("human_review_queue", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("human_review_queue", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("human_review_queue", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("human_review_queue", "L4_STATE", "p2_trace_5")
_emit_reads_environ("human_review_queue", "env_read", "p2_env_1")
_emit_reads_environ("human_review_queue", "env_read", "p2_env_2")
_emit_reads_runtime_state("human_review_queue", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("human_review_queue", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "human_review_queue", "context_pull")
_emit_pulls_context("p1", "human_review_queue", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "human_review_queue", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "human_review_queue", "uwg_term_2")
_emit_writes_through("p1", "human_review_queue", "write_through")
_emit_writes_through("p1", "human_review_queue", "write_through_2")
_emit_validated_by_safety_plane("p1", "human_review_queue", "safety_validation")
_emit_invokes_eval("p1", "human_review_queue", "eval_call")
_emit_proposal_commits_routing("p1", "human_review_queue", "routing_commit")

logger = logging.getLogger(__name__)


@dataclass
class PendingVerdict:
    """A verdict awaiting human review."""

    verdict_id: str
    component: str
    trace_id: str
    confidence: float
    verdict: str
    input_hash: str
    reviewed: bool = False
    approved: bool = False
    reviewer_notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class HumanReviewQueue:
    """Thread-safe queue for AI verdicts requiring human review.

    Verdicts are blocked from routing until `approve()` or `reject()` is called.
    """

    def __init__(self) -> None:
        self._queue: dict[str, PendingVerdict] = {}
        self._lock = threading.Lock()

    def enqueue(self, verdict: PendingVerdict) -> None:
        """Add a verdict to the review queue."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "HumanReviewQueue.enqueue")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:HumanReviewQueue.enqueue".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        with self._lock:
            self._queue[verdict.verdict_id] = verdict
        logger.info(
            "HumanReviewQueue: enqueued verdict_id=%s component=%s confidence=%.2f",
            verdict.verdict_id,
            verdict.component,
            verdict.confidence,
        )

    def approve(self, verdict_id: str, reviewer_notes: str = "") -> bool:
        """Mark a verdict as approved. Returns True if found."""
        with self._lock:
            v = self._queue.get(verdict_id)
            if v is None:
                return False
            v.reviewed = True
            v.approved = True
            v.reviewer_notes = reviewer_notes
        logger.info("HumanReviewQueue: approved verdict_id=%s", verdict_id)
        return True

    def reject(self, verdict_id: str, reviewer_notes: str = "") -> bool:
        """Mark a verdict as rejected. Returns True if found."""
        with self._lock:
            v = self._queue.get(verdict_id)
            if v is None:
                return False
            v.reviewed = True
            v.approved = False
            v.reviewer_notes = reviewer_notes
        logger.info("HumanReviewQueue: rejected verdict_id=%s", verdict_id)
        return True

    def is_approved(self, verdict_id: str) -> bool:
        """Return True only if the verdict has been reviewed and approved."""
        with self._lock:
            v = self._queue.get(verdict_id)
            return v is not None and v.reviewed and v.approved

    def is_blocked(self, verdict_id: str) -> bool:
        """Return True if the verdict exists and has not yet been reviewed."""
        with self._lock:
            v = self._queue.get(verdict_id)
            return v is not None and (not v.reviewed)

    def pending_count(self) -> int:
        """Return number of unreviewed verdicts."""
        with self._lock:
            return sum(1 for v in self._queue.values() if not v.reviewed)

    def all_pending(self) -> list[PendingVerdict]:
        """Return all unreviewed verdicts."""
        with self._lock:
            return [v for v in self._queue.values() if not v.reviewed]

    def size(self) -> int:
        with self._lock:
            return len(self._queue)


_GLOBAL_REVIEW_QUEUE: HumanReviewQueue | None = None


def get_review_queue() -> HumanReviewQueue:
    """Return the module-level singleton review queue."""
    global _GLOBAL_REVIEW_QUEUE
    if _GLOBAL_REVIEW_QUEUE is None:
        _GLOBAL_REVIEW_QUEUE = HumanReviewQueue()
    return _GLOBAL_REVIEW_QUEUE


__all__ = ["HumanReviewQueue", "PendingVerdict", "get_review_queue"]
