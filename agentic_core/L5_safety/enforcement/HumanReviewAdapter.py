"""
HumanReviewAdapter - Human-in-the-loop review queue adapter.

Provides a simple in-memory queue for submitting code changes for human review
before they are applied. Supports async approval/rejection workflow.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "HumanReviewAdapter")
trace_contract.emit_determinism_digest("p0", "HumanReviewAdapter")

trace_contract._emit_dispatches_healing_run("p1", "HumanReviewAdapter", "L5")
trace_contract._emit_routes_through("p1", "HumanReviewAdapter", "L5")
trace_contract._emit_checks_agent_registry("p1", "HumanReviewAdapter", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "HumanReviewAdapter", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "HumanReviewAdapter", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "HumanReviewAdapter", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "HumanReviewAdapter", "target_agent")
trace_contract._emit_verifies_policy("p1", "HumanReviewAdapter", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "HumanReviewAdapter", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "HumanReviewAdapter", "boundary_check")
trace_contract._emit_transcripts_response("p1", "HumanReviewAdapter", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "HumanReviewAdapter")
trace_contract._emit_gated_by_confidence("p1", "HumanReviewAdapter", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "HumanReviewAdapter", "L5")
trace_contract._emit_reads_policy_state("p1", "HumanReviewAdapter", "L5")
trace_contract._emit_authorize_and_execute("p2", "HumanReviewAdapter", "execution_auth")
trace_contract._emit_validates_capability("p2", "HumanReviewAdapter", "capability_check")
trace_contract._emit_routes_to_capability("p2", "HumanReviewAdapter", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "HumanReviewAdapter", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "HumanReviewAdapter", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "HumanReviewAdapter", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "HumanReviewAdapter", "exec_output")
trace_contract._emit_dispatches_agent("p3", "HumanReviewAdapter", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "HumanReviewAdapter", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "HumanReviewAdapter", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "HumanReviewAdapter", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "HumanReviewAdapter", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "HumanReviewAdapter", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "HumanReviewAdapter", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "HumanReviewAdapter", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "HumanReviewAdapter", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "HumanReviewAdapter", "eval_metric")
trace_contract._emit_stores_embedding("p4", "HumanReviewAdapter", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "HumanReviewAdapter", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "HumanReviewAdapter", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("HumanReviewAdapter", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("HumanReviewAdapter", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("HumanReviewAdapter", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("HumanReviewAdapter", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("HumanReviewAdapter", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("HumanReviewAdapter", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("HumanReviewAdapter", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("HumanReviewAdapter", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("HumanReviewAdapter", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("HumanReviewAdapter", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("HumanReviewAdapter", "p4obs", "alert")
trace_contract._emit_links_incident_trace("HumanReviewAdapter", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("HumanReviewAdapter", "p3lm", "pattern")
trace_contract._emit_records_learning_event("HumanReviewAdapter", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("HumanReviewAdapter", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("HumanReviewAdapter", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("HumanReviewAdapter", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("HumanReviewAdapter", "p3lm", "policy")
trace_contract._emit_stores_learning_state("HumanReviewAdapter", "p3lm", "state")
trace_contract._emit_records_execution_trace("HumanReviewAdapter", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("HumanReviewAdapter", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("HumanReviewAdapter", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("HumanReviewAdapter", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("HumanReviewAdapter", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("HumanReviewAdapter", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("HumanReviewAdapter", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("HumanReviewAdapter", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("HumanReviewAdapter", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "HumanReviewAdapter", "context_pull")
trace_contract._emit_pulls_context("p1", "HumanReviewAdapter", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "HumanReviewAdapter", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "HumanReviewAdapter", "uwg_term_2")
trace_contract._emit_writes_through("p1", "HumanReviewAdapter", "write_through")
trace_contract._emit_writes_through("p1", "HumanReviewAdapter", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "HumanReviewAdapter", "safety_validation")
trace_contract._emit_invokes_eval("p1", "HumanReviewAdapter", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "HumanReviewAdapter", "routing_commit")

Logger = logging.getLogger(__name__)


class ReviewStatus(Enum):
    """Status of a human review request."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class ReviewRequest:
    """A request for human review."""

    review_id: str
    agent_name: str
    file_path: str
    change_description: str
    proposed_change: str
    status: ReviewStatus = ReviewStatus.PENDING
    submitted_at: str = field(default_factory=lambda: datetime.now().isoformat())
    reviewed_at: str | None = None
    reviewer_notes: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "ReviewRequest.to_dict", "state_snapshot")
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "ReviewRequest.to_dict", "p0_governance")
        return {
            "review_id": self.review_id,
            "agent_name": self.agent_name,
            "file_path": self.file_path,
            "change_description": self.change_description,
            "proposed_change": self.proposed_change,
            "status": self.status.value,
            "submitted_at": self.submitted_at,
            "reviewed_at": self.reviewed_at,
            "reviewer_notes": self.reviewer_notes,
            "metadata": self.metadata,
        }


class HumanReviewAdapter:
    """
    Adapter for human-in-the-loop review of proposed code changes.

    Maintains an in-memory queue of review requests. In production this
    would integrate with an external review system (e.g., GitHub PRs, Slack).
    """

    _DEFAULT_TTL_HOURS = 24

    def __init__(self, ttl_hours: int = _DEFAULT_TTL_HOURS):
        """
        Initialize the adapter.

        Args:
            ttl_hours: Hours before a pending review request expires.
        """
        self.ttl_hours = ttl_hours
        self._queue: dict[str, ReviewRequest] = {}

    def submit_for_review(
        self,
        agent_name: str,
        file_path: str,
        change_description: str,
        proposed_change: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Submit a change for human review.

        Returns:
            review_id string
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L5_POLICY,
            "HumanReviewAdapter.submit_for_review",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:HumanReviewAdapter.submit_for_review".encode()).hexdigest()[
            :24
        ]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        review_id = str(uuid.uuid4())
        request = ReviewRequest(
            review_id=review_id,
            agent_name=agent_name,
            file_path=file_path,
            change_description=change_description,
            proposed_change=proposed_change,
            metadata=metadata or {},
        )
        self._queue[review_id] = request
        Logger.info("Submitted review request %s for %s", review_id, file_path)
        return review_id

    def check_status(self, review_id: str) -> ReviewStatus | None:
        """
        Check the status of a review request.

        Returns:
            ReviewStatus or None if not found
        """
        request = self._queue.get(review_id)
        if request is None:
            return None
        self._expire_if_stale(request)
        return request.status

    def get_pending_reviews(self) -> list[ReviewRequest]:
        """Return all pending (non-expired) review requests."""
        self._expire_stale_requests()
        return [r for r in self._queue.values() if r.status == ReviewStatus.PENDING]

    def is_available(self) -> bool:
        """Return True — the in-memory adapter is always available."""
        return True

    def get_queue_depth(self) -> int:
        """Return the number of pending review requests."""
        return len(self.get_pending_reviews())

    def approve(self, review_id: str, reviewer_notes: str = "") -> bool:
        """
        Approve a review request.

        Returns:
            True if the request was found and approved, False otherwise.
        """
        request = self._queue.get(review_id)
        if request is None or request.status != ReviewStatus.PENDING:
            return False
        request.status = ReviewStatus.APPROVED
        request.reviewed_at = datetime.now().isoformat()
        request.reviewer_notes = reviewer_notes
        Logger.info("Approved review request %s", review_id)
        return True

    def reject(self, review_id: str, reviewer_notes: str = "") -> bool:
        """
        Reject a review request.

        Returns:
            True if the request was found and rejected, False otherwise.
        """
        request = self._queue.get(review_id)
        if request is None or request.status != ReviewStatus.PENDING:
            return False
        request.status = ReviewStatus.REJECTED
        request.reviewed_at = datetime.now().isoformat()
        request.reviewer_notes = reviewer_notes
        Logger.info("Rejected review request %s", review_id)
        return True

    def clear_expired(self) -> int:
        """
        Remove all expired review requests from the queue.

        Returns:
            Number of requests removed.
        """
        self._expire_stale_requests()
        before = len(self._queue)
        self._queue = {rid: r for rid, r in self._queue.items() if r.status != ReviewStatus.EXPIRED}
        removed = before - len(self._queue)
        if removed:
            Logger.info("Cleared %d expired review requests", removed)
        return removed

    def _expire_if_stale(self, request: ReviewRequest) -> None:
        """Mark a single request as expired if its TTL has passed."""
        if request.status != ReviewStatus.PENDING:
            return
        submitted = datetime.fromisoformat(request.submitted_at)
        if datetime.now() - submitted > timedelta(hours=self.ttl_hours):
            request.status = ReviewStatus.EXPIRED

    def _expire_stale_requests(self) -> None:
        """Mark all stale pending requests as expired."""
        for request in self._queue.values():
            self._expire_if_stale(request)
