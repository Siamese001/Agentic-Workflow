"""
Human Review Adapter - Protocol-compliant wrapper for legacy HumanReviewQueue.

Wraps the existing HumanReviewQueue to conform to HumanReviewProtocol,
enabling integration with the new feature-flagged agent system.
"""

import logging
import uuid
from typing import Any, Dict, List, Optional

from agentic_core.interfaces.review_protocol import (
    HumanReviewProtocol,
    ReviewRequest,
    ReviewResult,
    ReviewStatus,
)
from agentic_core.primitives.feature_flags import FeatureFlagManager

logger = logging.getLogger(__name__)


class HumanReviewAdapter(HumanReviewProtocol):
    """Protocol-compliant adapter for legacy HumanReviewQueue.

    This adapter wraps the existing HumanReviewQueue implementation to
    conform to the HumanReviewProtocol interface, enabling seamless
    integration with the FeatureFlaggedAgentMixin.
    """

    def __init__(self, legacy_queue: Optional[Any] = None):
        """Initialize adapter with optional legacy queue.

        Args:
            legacy_queue: Optional existing HumanReviewQueue instance
        """
        self._legacy_queue = legacy_queue
        self._available = True
        self._pending_reviews: Dict[str, ReviewRequest] = {}
        self._review_results: Dict[str, ReviewResult] = {}

        if legacy_queue is None:
            self._initialize_legacy_queue()

    def _initialize_legacy_queue(self) -> None:
        """Lazy-load the legacy HumanReviewQueue."""
        try:
            from agentic_core.L5_safety.human_review.review_queue import (
                HumanReviewQueue,
            )

            self._legacy_queue = HumanReviewQueue()
            logger.debug("HumanReviewAdapter: Initialized legacy queue")
        except ImportError as e:
            logger.warning(f"HumanReviewAdapter: Failed to load legacy queue: {e}")
            self._available = False

    def submit_for_review(self, request: ReviewRequest) -> ReviewResult:
        """Submit an operation for human review.

        Args:
            request: Review request with context

        Returns:
            ReviewResult with request_id and initial status
        """
        # Check feature flag first
        if not FeatureFlagManager.is_enabled("ENABLE_HITL_WORKFLOW"):
            return ReviewResult(
                request_id=request.request_id,
                status=ReviewStatus.APPROVED,
                reason="hitl_disabled",
                metadata={"flag": "ENABLE_HITL_WORKFLOW", "status": "disabled"},
            )

        # Store pending review
        self._pending_reviews[request.request_id] = request

        # Try legacy queue if available
        if self._legacy_queue is not None:
            try:
                # Attempt to use legacy queue
                legacy_result = self._submit_to_legacy(request)
                if legacy_result:
                    return legacy_result
            except Exception as e:
                logger.warning(f"HumanReviewAdapter: Legacy queue error: {e}")

        # Create pending result
        result = ReviewResult(
            request_id=request.request_id,
            status=ReviewStatus.PENDING,
            metadata={
                "agent": request.agent_name,
                "action": request.action_type,
                "target": request.target_file,
                "risk_level": request.risk_level,
            },
        )

        self._review_results[request.request_id] = result
        logger.info(
            f"HumanReviewAdapter: Submitted review {request.request_id} "
            f"for {request.agent_name}"
        )

        return result

    def _submit_to_legacy(self, request: ReviewRequest) -> Optional[ReviewResult]:
        """Submit to legacy queue if compatible."""
        # Legacy queue may have different interface
        # For now, return None to use adapter's internal tracking
        return None

    def check_status(self, request_id: str) -> ReviewResult:
        """Check status of a review request.

        Args:
            request_id: ID of the review request

        Returns:
            Current ReviewResult
        """
        if not FeatureFlagManager.is_enabled("ENABLE_HITL_WORKFLOW"):
            return ReviewResult(
                request_id=request_id,
                status=ReviewStatus.APPROVED,
                reason="hitl_disabled",
            )

        if request_id in self._review_results:
            return self._review_results[request_id]

        return ReviewResult(
            request_id=request_id,
            status=ReviewStatus.CANCELLED,
            reason="not_found",
        )

    def get_pending_reviews(
        self,
        agent_name: Optional[str] = None,
        limit: int = 50,
    ) -> List[ReviewRequest]:
        """Get pending review requests.

        Args:
            agent_name: Optional filter by agent name
            limit: Maximum number of results

        Returns:
            List of pending ReviewRequests
        """
        pending = []
        for request_id, request in self._pending_reviews.items():
            result = self._review_results.get(request_id)
            if result and result.status == ReviewStatus.PENDING:
                if agent_name is None or request.agent_name == agent_name:
                    pending.append(request)

        return pending[:limit]

    def is_available(self) -> bool:
        """Check if review queue is available."""
        return self._available

    def get_queue_depth(self) -> int:
        """Get number of pending reviews in queue."""
        return len(
            [r for r in self._review_results.values() if r.status == ReviewStatus.PENDING]
        )

    def approve(self, request_id: str, reviewer: str, reason: Optional[str] = None) -> ReviewResult:
        """Approve a pending review.

        Args:
            request_id: ID of the review to approve
            reviewer: Identifier of the reviewer
            reason: Optional approval reason

        Returns:
            Updated ReviewResult
        """
        import datetime

        if request_id not in self._review_results:
            return ReviewResult(
                request_id=request_id,
                status=ReviewStatus.CANCELLED,
                reason="not_found",
            )

        result = ReviewResult(
            request_id=request_id,
            status=ReviewStatus.APPROVED,
            reviewer=reviewer,
            reason=reason or "approved",
            approved_at=datetime.datetime.now().isoformat(),
        )

        self._review_results[request_id] = result
        logger.info(f"HumanReviewAdapter: Approved review {request_id} by {reviewer}")

        return result

    def reject(self, request_id: str, reviewer: str, reason: str) -> ReviewResult:
        """Reject a pending review.

        Args:
            request_id: ID of the review to reject
            reviewer: Identifier of the reviewer
            reason: Rejection reason

        Returns:
            Updated ReviewResult
        """
        if request_id not in self._review_results:
            return ReviewResult(
                request_id=request_id,
                status=ReviewStatus.CANCELLED,
                reason="not_found",
            )

        result = ReviewResult(
            request_id=request_id,
            status=ReviewStatus.REJECTED,
            reviewer=reviewer,
            reason=reason,
        )

        self._review_results[request_id] = result
        logger.info(f"HumanReviewAdapter: Rejected review {request_id} by {reviewer}")

        return result

    def clear_expired(self, max_age_seconds: int = 3600) -> int:
        """Clear expired pending reviews.

        Args:
            max_age_seconds: Maximum age for pending reviews

        Returns:
            Number of reviews expired
        """
        # For now, just return 0 - full implementation would track timestamps
        return 0
