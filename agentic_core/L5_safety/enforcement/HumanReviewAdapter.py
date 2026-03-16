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

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "HumanReviewAdapter")
emit_determinism_digest("p0", "HumanReviewAdapter")

_emit_dispatches_healing_run("p1", "HumanReviewAdapter", "L5")
_emit_routes_through("p1", "HumanReviewAdapter", "L5")
_emit_escalates_to_human("p1", "HumanReviewAdapter", "L5")
_emit_reads_policy_state("p1", "HumanReviewAdapter", "L5")
_emit_authorize_and_execute("p2", "HumanReviewAdapter", "execution_auth")
_emit_validates_capability("p2", "HumanReviewAdapter", "capability_check")
_emit_routes_to_capability("p2", "HumanReviewAdapter", "capability_route")
_emit_writes_via_uwg("p2", "HumanReviewAdapter", "uwg_write")
_emit_blocks_direct_write("p2", "HumanReviewAdapter", "direct_write_block")
_emit_records_tool_invocation("p2", "HumanReviewAdapter", "tool_invocation")
_emit_captures_execution_output("p2", "HumanReviewAdapter", "exec_output")
_emit_dispatches_agent("p3", "HumanReviewAdapter", "agent_dispatch")
_emit_coordinates_agents("p3", "HumanReviewAdapter", "agent_coordination")
_emit_records_workflow_lineage("p3", "HumanReviewAdapter", "workflow_lineage")
_emit_records_healing_outcome("p3", "HumanReviewAdapter", "healing_outcome")
_emit_escalates_failure("p3", "HumanReviewAdapter", "failure_escalation")
_emit_orchestrates_workflow("p3", "HumanReviewAdapter", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "HumanReviewAdapter", "healing_dispatch")
_emit_invokes_evaluation("p3", "HumanReviewAdapter", "evaluation_signal")
_emit_records_telemetry_event("p4", "HumanReviewAdapter", "telemetry_event")
_emit_captures_evaluation_metric("p4", "HumanReviewAdapter", "eval_metric")
_emit_stores_embedding("p4", "HumanReviewAdapter", "embedding_store")
_emit_updates_meta_learning_state("p4", "HumanReviewAdapter", "meta_learning")
_emit_links_execution_to_snapshot("p4", "HumanReviewAdapter", "exec_snapshot_link")

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

        _emit_snapshots_state(str(_uuid.uuid4()), "ReviewRequest.to_dict", "state_snapshot")
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ReviewRequest.to_dict", "p0_governance")
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
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "HumanReviewAdapter.submit_for_review"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:HumanReviewAdapter.submit_for_review".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
