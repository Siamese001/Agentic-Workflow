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

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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
