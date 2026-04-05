"""
Human Review Protocol for HITL (Human-in-the-Loop) workflows.

This protocol standardizes how agents submit high-risk operations for
human review before execution.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from agentic_core.config.constants_config import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

# Configuration constants

class ReviewStatus(Enum):
    """Status of a review request."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


@dataclass
class ReviewRequest:
    """Request for human review."""

    request_id: str
    agent_name: str
    action_type: str
    target_file: str
    description: str
    risk_level: str
    context_bundle: dict[str, Any] | None = field(default_factory=dict)
    timeout_seconds: int = 3600  # 1 hour default

    def __post_init__(self) -> None:
        if self.context_bundle is None:
            self.context_bundle = {}


@dataclass
class ReviewResult:
    """Result of human review."""

    request_id: str
    status: ReviewStatus
    reviewer: str | None = None
    reason: str | None = None
    approved_at: str | None = None
    metadata: dict[str, Any] | None = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}

    def is_approved(self) -> bool:
        """Check if request was approved."""
        return self.status == ReviewStatus.APPROVED

    def is_terminal(self) -> bool:
        """Check if review is in terminal state."""
        return self.status in (
            ReviewStatus.APPROVED,
            ReviewStatus.REJECTED,
            ReviewStatus.EXPIRED,
            ReviewStatus.CANCELLED,
        )


class HumanReviewProtocol(ABC):
    """Protocol for human review queue implementations.

    Implementations must provide a way to submit high-risk operations
    for human review and track their approval status.
    """

    @abstractmethod
    def submit_for_review(self, request: ReviewRequest) -> ReviewResult:
        """Submit an operation for human review.

        Args:
            request: Review request with context

        Returns:
            ReviewResult with request_id and initial status
        """
        pass

    @abstractmethod
    def check_status(self, request_id: str) -> ReviewResult:
        """Check status of a review request.

        Args:
            request_id: ID of the review request

        Returns:
            Current ReviewResult
        """
        pass

    @abstractmethod
    def get_pending_reviews(
        self,
        agent_name: str | None = None,
        limit: int = 50,
    ) -> list[ReviewRequest]:
        """Get pending review requests."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if review queue is available."""
        pass

    @abstractmethod
    def get_queue_depth(self) -> int:
        """Get number of pending reviews in queue."""
        pass
