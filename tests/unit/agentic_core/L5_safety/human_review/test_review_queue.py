#!/usr/bin/env python3
"""Tests for HumanReviewQueue approval workflow."""

from pathlib import Path

import pytest

from agentic_core.L5_safety.human_review.review_queue import (
    ContextBundle,
    HumanReviewQueue,
    ProposedDiff,
    ReviewStatus,
    SimulatedOutcome,
)


@pytest.fixture
def sample_context_bundle():
    """Create sample context bundle for testing."""
    return ContextBundle(
        detection_signal={"signal_id": "test-001", "severity": "HIGH"},
        proposed_diff=ProposedDiff(
            file_path=Path("agentic_core/test.py"),
            original_content="def old_func(): pass",
            proposed_content="def new_func(): pass",
            change_summary="Rename function",
        ),
        ai_rationale="Function name violates naming convention",
        simulated_outcome=SimulatedOutcome(
            success_probability=0.95,
            expected_side_effects=[],
            regression_risk="low",
        ),
        risk_assessment={"risk_level": "HIGH", "confidence": 0.9},
    )


class TestHumanReviewQueue:
    """Test suite for HumanReviewQueue."""

    def test_submit_for_review(self, sample_context_bundle):
        """Test submitting request for review."""
        queue = HumanReviewQueue()
        request = queue.submit_for_review(sample_context_bundle)

        assert request.request_id is not None
        assert request.status == ReviewStatus.PENDING
        assert request.context_bundle is not None

    def test_approve_request(self, sample_context_bundle):
        """Test approving a review request."""
        queue = HumanReviewQueue()
        request = queue.submit_for_review(sample_context_bundle)

        approved = queue.approve(
            request.request_id,
            reviewer_id="reviewer_001",
            notes="Looks good",
        )

        assert approved.status == ReviewStatus.APPROVED
        assert approved.reviewer_id == "reviewer_001"
        assert approved.review_completed_at is not None

    def test_reject_request_requires_notes(self, sample_context_bundle):
        """Test that rejection requires notes."""
        queue = HumanReviewQueue()
        request = queue.submit_for_review(sample_context_bundle)

        with pytest.raises(ValueError, match="notes are required"):
            queue.reject(request.request_id, "reviewer_001", "")

    def test_reject_request_with_notes(self, sample_context_bundle):
        """Test rejecting with valid notes."""
        queue = HumanReviewQueue()
        request = queue.submit_for_review(sample_context_bundle)

        rejected = queue.reject(
            request.request_id,
            reviewer_id="reviewer_001",
            notes="Change would break downstream dependencies",
        )

        assert rejected.status == ReviewStatus.REJECTED
        assert "downstream" in rejected.review_notes

    def test_escalation(self, sample_context_bundle):
        """Test escalating review request."""
        queue = HumanReviewQueue()
        request = queue.submit_for_review(sample_context_bundle)

        escalated = queue.escalate(request.request_id, "Timeout reached")

        assert escalated.status == ReviewStatus.ESCALATED
        assert escalated.escalation_level == 1

    def test_max_escalation_level(self, sample_context_bundle):
        """Test maximum escalation level enforcement."""
        queue = HumanReviewQueue()
        request = queue.submit_for_review(sample_context_bundle)

        # Escalate to max level
        for _ in range(len(request.escalation_chain) - 1):
            queue.escalate(request.request_id)

        # Next escalation should fail
        with pytest.raises(ValueError, match="Maximum escalation"):
            queue.escalate(request.request_id)

    def test_get_pending_requests(self, sample_context_bundle):
        """Test retrieving pending requests."""
        queue = HumanReviewQueue()
        queue.submit_for_review(sample_context_bundle)
        queue.submit_for_review(sample_context_bundle)

        pending = queue.get_pending_requests()

        assert len(pending) == 2

    def test_request_timeout(self, sample_context_bundle):
        """Test request expiration."""
        queue = HumanReviewQueue()
        request = queue.submit_for_review(
            sample_context_bundle,
            timeout_seconds=0,  # Immediate timeout
        )

        # Manually set created_at to past to ensure expiration
        # Must modify the actual request in the queue's internal dict
        from datetime import timedelta

        queue._pending_requests[request.request_id].created_at = request.created_at - timedelta(
            seconds=10
        )

        pending = queue.get_pending_requests()

        assert len(pending) == 0
        assert queue.get_request_status(request.request_id) == ReviewStatus.EXPIRED

    def test_context_bundle_serialization(self, sample_context_bundle):
        """Test context bundle to_dict serialization."""
        data = sample_context_bundle.to_dict()

        assert "detection_signal" in data
        assert "proposed_diff" in data
        assert "ai_rationale" in data
        assert "simulated_outcome" in data
        assert "risk_assessment" in data

    def test_proposed_diff_unified_format(self):
        """Test unified diff generation."""
        diff = ProposedDiff(
            file_path=Path("test.py"),
            original_content="line1\nline2",
            proposed_content="line1\nline2_modified",
            change_summary="Modified line 2",
        )

        unified = diff.to_unified_diff()

        assert "---" in unified
        assert "+++" in unified

    def test_callback_on_approval(self, sample_context_bundle):
        """Test callback triggered on approval."""
        queue = HumanReviewQueue()
        request = queue.submit_for_review(sample_context_bundle)

        callback_called = []

        def on_resolved(req_id, action):
            callback_called.append((req_id, action))

        queue.register_callback(request.request_id, on_resolved)
        queue.approve(request.request_id, "reviewer")

        assert len(callback_called) == 1
        assert callback_called[0][1] == "approved"

    def test_queue_stats(self, sample_context_bundle):
        """Test queue statistics."""
        queue = HumanReviewQueue()
        queue.submit_for_review(sample_context_bundle)

        stats = queue.get_queue_stats()

        assert stats["pending_count"] == 1
        assert "max_pending" in stats

    def test_request_not_found(self):
        """Test error on non-existent request."""
        queue = HumanReviewQueue()

        with pytest.raises(ValueError, match="not found"):
            queue.approve("nonexistent", "reviewer")


class TestProposedDiff:
    """Test suite for ProposedDiff."""

    def test_line_counting(self):
        """Test line addition/removal counting."""
        diff = ProposedDiff(
            file_path=Path("test.py"),
            original_content="a\nb\nc",
            proposed_content="a\nb\nc\nd",
            change_summary="Added line",
            lines_added=1,
            lines_removed=0,
        )

        assert diff.lines_added == 1
        assert diff.lines_removed == 0


class TestSimulatedOutcome:
    """Test suite for SimulatedOutcome."""

    def test_default_values(self):
        """Test default simulation outcome values."""
        outcome = SimulatedOutcome()

        assert outcome.success_probability == 0.9
        assert outcome.regression_risk == "low"
        assert outcome.rollback_complexity == "simple"

    def test_side_effects_tracking(self):
        """Test expected side effects."""
        outcome = SimulatedOutcome(
            expected_side_effects=["May affect imports", "Test coverage change"],
        )

        assert len(outcome.expected_side_effects) == 2
