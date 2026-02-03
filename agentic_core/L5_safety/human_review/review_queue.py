#!/usr/bin/env python3
"""Human Review Queue - Approval workflow for high-risk fixes.

Implements the HUMAN REVIEW GATE component from target state architecture.
Provides approval queue with rich context bundles including detection signal,
diff, rationale, simulated outcome, risk score, and past cases.

Target State Reference:
- Approval Queue with Rich Context Bundle
- Detection signal, diff, rationale, simulated outcome
- Risk score, past cases
- Escalation workflow
"""

from __future__ import annotations

import difflib
import logging
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

Logger = logging.getLogger(__name__)


class ReviewStatus(Enum):
    """Status of a review request."""

    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    EXPIRED = "expired"


@dataclass
class ProposedDiff:
    """Proposed code change for review."""

    file_path: Path
    original_content: str
    proposed_content: str
    change_summary: str
    lines_added: int = 0
    lines_removed: int = 0

    def to_unified_diff(self) -> str:
        """Generate unified diff format."""
        original_lines = self.original_content.splitlines(keepends=True)
        proposed_lines = self.proposed_content.splitlines(keepends=True)
        diff = difflib.unified_diff(
            original_lines,
            proposed_lines,
            fromfile=f"a/{self.file_path}",
            tofile=f"b/{self.file_path}",
        )
        return "".join(diff)


@dataclass
class SimulatedOutcome:
    """Simulated outcome of applying the proposed fix."""

    success_probability: float = 0.9  # 0.0 to 1.0
    expected_side_effects: list[str] = field(default_factory=list)
    regression_risk: str = "low"  # low, medium, high
    test_results: dict[str, bool] = field(default_factory=dict)
    rollback_complexity: str = "simple"  # simple, moderate, complex


@dataclass
class ContextBundle:
    """Rich context bundle for human review.

    Contains all information needed for informed human decision:
    - Detection signal details
    - Proposed diff
    - AI rationale
    - Simulated outcome
    - Risk assessment
    - Historical similar cases
    """

    detection_signal: dict[str, Any]  # Serialized DetectionSignal
    proposed_diff: ProposedDiff
    ai_rationale: str
    simulated_outcome: SimulatedOutcome
    risk_assessment: dict[str, Any]  # Serialized RiskAssessment
    similar_past_cases: list[dict[str, Any]] = field(default_factory=list)
    additional_context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "detection_signal": self.detection_signal,
            "proposed_diff": {
                "file_path": str(self.proposed_diff.file_path),
                "change_summary": self.proposed_diff.change_summary,
                "unified_diff": self.proposed_diff.to_unified_diff(),
            },
            "ai_rationale": self.ai_rationale,
            "simulated_outcome": {
                "success_probability": self.simulated_outcome.success_probability,
                "expected_side_effects": self.simulated_outcome.expected_side_effects,
                "regression_risk": self.simulated_outcome.regression_risk,
            },
            "risk_assessment": self.risk_assessment,
            "similar_past_cases": self.similar_past_cases,
        }


@dataclass
class ReviewRequest:
    """Human review request with full context."""

    request_id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: ReviewStatus = ReviewStatus.PENDING
    context_bundle: Optional[ContextBundle] = None

    # Review metadata
    reviewer_id: Optional[str] = None
    review_started_at: Optional[datetime] = None
    review_completed_at: Optional[datetime] = None
    review_notes: str = ""

    # Escalation tracking
    escalation_level: int = 0
    escalation_chain: list[str] = field(
        default_factory=lambda: ["team_lead", "manager", "director"]
    )

    # Timeout configuration
    timeout_seconds: int = 3600  # 1 hour default

    def is_expired(self) -> bool:
        """Check if request has timed out."""
        elapsed = (datetime.utcnow() - self.created_at).total_seconds()
        return elapsed > self.timeout_seconds

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "created_at": self.created_at.isoformat(),
            "status": self.status.value,
            "context_bundle": self.context_bundle.to_dict() if self.context_bundle else None,
            "reviewer_id": self.reviewer_id,
            "escalation_level": self.escalation_level,
            "is_expired": self.is_expired(),
        }


class HumanReviewQueue:
    """Approval queue for high-risk fixes requiring human review.

    Implements the HUMAN REVIEW GATE from target state architecture.
    Thread-safe queue management with escalation support.

    Features:
    - Rich context bundles for informed decisions
    - Escalation workflow
    - Timeout handling
    - Callback support for async workflows
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self._pending_requests: dict[str, ReviewRequest] = {}
        self._completed_requests: list[ReviewRequest] = []
        self._lock = threading.RLock()
        self._callbacks: dict[str, Callable] = {}

        # Configuration
        self.max_pending = self.config.get("max_pending", 100)
        self.default_timeout = self.config.get("default_timeout_seconds", 3600)
        self.auto_escalate_after = self.config.get("auto_escalate_after_seconds", 1800)

    def submit_for_review(
        self,
        context_bundle: ContextBundle,
        timeout_seconds: Optional[int] = None,
    ) -> ReviewRequest:
        """Submit a change for human review.

        Args:
            context_bundle: Full context for review decision
            timeout_seconds: Custom timeout for this request

        Returns:
            ReviewRequest tracking the submission
        """
        request = ReviewRequest(
            context_bundle=context_bundle,
            timeout_seconds=timeout_seconds
            if timeout_seconds is not None
            else self.default_timeout,
        )

        with self._lock:
            # Evict oldest if at capacity
            if len(self._pending_requests) >= self.max_pending:
                self._evict_oldest()

            self._pending_requests[request.request_id] = request

        Logger.info(
            f"[REVIEW_QUEUE] Submitted review request {request.request_id} "
            f"for {context_bundle.proposed_diff.file_path}"
        )

        return request

    def approve(
        self,
        request_id: str,
        reviewer_id: str,
        notes: str = "",
    ) -> ReviewRequest:
        """Approve a pending review request."""
        with self._lock:
            request = self._pending_requests.get(request_id)
            if not request:
                raise ValueError(f"Review request not found: {request_id}")

            request.status = ReviewStatus.APPROVED
            request.reviewer_id = reviewer_id
            request.review_completed_at = datetime.utcnow()
            request.review_notes = notes

            del self._pending_requests[request_id]
            self._completed_requests.append(request)

        Logger.info(f"[REVIEW_QUEUE] Request {request_id} APPROVED by {reviewer_id}")
        self._trigger_callback(request_id, "approved")

        return request

    def reject(
        self,
        request_id: str,
        reviewer_id: str,
        notes: str,
    ) -> ReviewRequest:
        """Reject a pending review request."""
        if not notes:
            raise ValueError("Rejection notes are required")

        with self._lock:
            request = self._pending_requests.get(request_id)
            if not request:
                raise ValueError(f"Review request not found: {request_id}")

            request.status = ReviewStatus.REJECTED
            request.reviewer_id = reviewer_id
            request.review_completed_at = datetime.utcnow()
            request.review_notes = notes

            del self._pending_requests[request_id]
            self._completed_requests.append(request)

        Logger.info(f"[REVIEW_QUEUE] Request {request_id} REJECTED by {reviewer_id}: {notes}")
        self._trigger_callback(request_id, "rejected")

        return request

    def escalate(self, request_id: str, reason: str = "") -> ReviewRequest:
        """Escalate request to next level in escalation chain."""
        with self._lock:
            request = self._pending_requests.get(request_id)
            if not request:
                raise ValueError(f"Review request not found: {request_id}")

            if request.escalation_level >= len(request.escalation_chain) - 1:
                raise ValueError("Maximum escalation level reached")

            request.escalation_level += 1
            request.status = ReviewStatus.ESCALATED

            current_approver = request.escalation_chain[request.escalation_level]

        Logger.warning(
            f"[REVIEW_QUEUE] Request {request_id} ESCALATED to {current_approver}: {reason}"
        )

        return request

    def get_pending_requests(self) -> list[dict[str, Any]]:
        """Get all pending review requests."""
        with self._lock:
            # Check for expired requests
            self._process_expired()
            return [r.to_dict() for r in self._pending_requests.values()]

    def get_request_status(self, request_id: str) -> Optional[ReviewStatus]:
        """Get status of a specific request."""
        with self._lock:
            if request_id in self._pending_requests:
                return self._pending_requests[request_id].status
            for r in self._completed_requests:
                if r.request_id == request_id:
                    return r.status
        return None

    def register_callback(
        self,
        request_id: str,
        callback: Callable[[str, str], None],
    ) -> None:
        """Register callback for when request is resolved."""
        self._callbacks[request_id] = callback

    def _evict_oldest(self) -> None:
        """Evict oldest pending request."""
        oldest_id = min(
            self._pending_requests.keys(),
            key=lambda k: self._pending_requests[k].created_at,
        )
        oldest = self._pending_requests.pop(oldest_id)
        oldest.status = ReviewStatus.EXPIRED
        self._completed_requests.append(oldest)
        Logger.warning(f"[REVIEW_QUEUE] Evicted expired request {oldest_id}")

    def _process_expired(self) -> None:
        """Process expired requests."""
        expired_ids = [rid for rid, r in self._pending_requests.items() if r.is_expired()]
        for rid in expired_ids:
            request = self._pending_requests.pop(rid)
            request.status = ReviewStatus.EXPIRED
            self._completed_requests.append(request)
            Logger.warning(f"[REVIEW_QUEUE] Request {rid} EXPIRED")

    def _trigger_callback(self, request_id: str, action: str) -> None:
        """Trigger registered callback."""
        callback = self._callbacks.pop(request_id, None)
        if callback:
            try:
                callback(request_id, action)
            except Exception as e:
                Logger.error(f"[REVIEW_QUEUE] Callback error: {e}")

    def get_queue_stats(self) -> dict[str, Any]:
        """Get queue statistics for observability."""
        with self._lock:
            return {
                "pending_count": len(self._pending_requests),
                "completed_count": len(self._completed_requests),
                "max_pending": self.max_pending,
                "default_timeout_seconds": self.default_timeout,
            }


__all__ = [
    "HumanReviewQueue",
    "ReviewRequest",
    "ReviewStatus",
    "ContextBundle",
    "ProposedDiff",
    "SimulatedOutcome",
]
