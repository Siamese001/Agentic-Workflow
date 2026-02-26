"""Tests for HumanReviewAdapter."""

# from agentic_core.L5_safety.reasoning.human_review_adapter import HumanReviewAdapter  # TODO: Fix import
# from agentic_core.utils.feature_flags import FeatureFlagManager  # TODO: Fix import
# from agentic_core.utils.review_protocol_util import (
#     ReviewRequest,
#     ReviewResult,
#     ReviewStatus,
# )


class TestHumanReviewAdapter:
    """Tests for HumanReviewAdapter."""

    def setup_method(self):
        """Clear overrides before each test."""
        FeatureFlagManager.clear_all_overrides()

    def teardown_method(self):
        """Clear overrides after each test."""
        FeatureFlagManager.clear_all_overrides()

    def test_init_creates_adapter(self):
        """Test that adapter initializes correctly."""
        adapter = HumanReviewAdapter()
        assert adapter is not None

    def test_is_available(self):
        """Test is_available returns True."""
        adapter = HumanReviewAdapter()
        assert adapter.is_available() is True

    def test_get_queue_depth_empty(self):
        """Test get_queue_depth returns 0 when empty."""
        adapter = HumanReviewAdapter()
        assert adapter.get_queue_depth() == 0

    def test_submit_for_review_flag_disabled(self):
        """Test submit_for_review auto-approves when flag disabled."""
        adapter = HumanReviewAdapter()
        request = ReviewRequest(
            request_id="REQ-001",
            agent_name="TestAgent",
            action_type="heal_file",
            target_file="/test.py",
            description="Test fix",
            risk_level="high",
        )

        result = adapter.submit_for_review(request)

        assert result.status == ReviewStatus.APPROVED
        assert result.reason == "hitl_disabled"

    def test_submit_for_review_flag_enabled(self):
        """Test submit_for_review creates pending review when flag enabled."""
        FeatureFlagManager.set_override("ENABLE_HITL_WORKFLOW", True)
        adapter = HumanReviewAdapter()

        request = ReviewRequest(
            request_id="REQ-001",
            agent_name="TestAgent",
            action_type="heal_file",
            target_file="/test.py",
            description="Test fix",
            risk_level="high",
        )

        result = adapter.submit_for_review(request)

        assert result.status == ReviewStatus.PENDING
        assert result.request_id == "REQ-001"

    def test_submit_for_review_increments_queue_depth(self):
        """Test that submitting reviews increases queue depth."""
        FeatureFlagManager.set_override("ENABLE_HITL_WORKFLOW", True)
        adapter = HumanReviewAdapter()

        assert adapter.get_queue_depth() == 0

        for i in range(3):
            request = ReviewRequest(
                request_id=f"REQ-{i:03d}",
                agent_name="TestAgent",
                action_type="heal_file",
                target_file=f"/test{i}.py",
                description="Test fix",
                risk_level="high",
            )
            adapter.submit_for_review(request)

        assert adapter.get_queue_depth() == 3

    def test_check_status_flag_disabled(self):
        """Test check_status returns approved when flag disabled."""
        adapter = HumanReviewAdapter()

        result = adapter.check_status("REQ-001")

        assert result.status == ReviewStatus.APPROVED
        assert result.reason == "hitl_disabled"

    def test_check_status_not_found(self):
        """Test check_status returns cancelled when not found."""
        FeatureFlagManager.set_override("ENABLE_HITL_WORKFLOW", True)
        adapter = HumanReviewAdapter()

        result = adapter.check_status("NONEXISTENT")

        assert result.status == ReviewStatus.CANCELLED
        assert result.reason == "not_found"

    def test_check_status_pending(self):
        """Test check_status returns pending for submitted request."""
        FeatureFlagManager.set_override("ENABLE_HITL_WORKFLOW", True)
        adapter = HumanReviewAdapter()

        request = ReviewRequest(
            request_id="REQ-001",
            agent_name="TestAgent",
            action_type="heal_file",
            target_file="/test.py",
            description="Test fix",
            risk_level="high",
        )
        adapter.submit_for_review(request)

        result = adapter.check_status("REQ-001")

        assert result.status == ReviewStatus.PENDING

    def test_get_pending_reviews_empty(self):
        """Test get_pending_reviews returns empty list when no reviews."""
        adapter = HumanReviewAdapter()
        pending = adapter.get_pending_reviews()
        assert len(pending) == 0

    def test_get_pending_reviews_returns_pending(self):
        """Test get_pending_reviews returns pending requests."""
        FeatureFlagManager.set_override("ENABLE_HITL_WORKFLOW", True)
        adapter = HumanReviewAdapter()

        for i in range(3):
            request = ReviewRequest(
                request_id=f"REQ-{i:03d}",
                agent_name="TestAgent",
                action_type="heal_file",
                target_file=f"/test{i}.py",
                description="Test fix",
                risk_level="high",
            )
            adapter.submit_for_review(request)

        pending = adapter.get_pending_reviews()
        assert len(pending) == 3

    def test_get_pending_reviews_filter_by_agent(self):
        """Test get_pending_reviews filters by agent name."""
        FeatureFlagManager.set_override("ENABLE_HITL_WORKFLOW", True)
        adapter = HumanReviewAdapter()

        adapter.submit_for_review(
            ReviewRequest(
                request_id="REQ-001",
                agent_name="Agent1",
                action_type="heal",
                target_file="/test.py",
                description="test",
                risk_level="high",
            ),
        )
        adapter.submit_for_review(
            ReviewRequest(
                request_id="REQ-002",
                agent_name="Agent2",
                action_type="heal",
                target_file="/test.py",
                description="test",
                risk_level="high",
            ),
        )

        pending = adapter.get_pending_reviews(agent_name="Agent1")
        assert len(pending) == 1
        assert pending[0].agent_name == "Agent1"

    def test_get_pending_reviews_limit(self):
        """Test get_pending_reviews respects limit."""
        FeatureFlagManager.set_override("ENABLE_HITL_WORKFLOW", True)
        adapter = HumanReviewAdapter()

        for i in range(10):
            adapter.submit_for_review(
                ReviewRequest(
                    request_id=f"REQ-{i:03d}",
                    agent_name="TestAgent",
                    action_type="heal",
                    target_file=f"/test{i}.py",
                    description="test",
                    risk_level="high",
                ),
            )

        pending = adapter.get_pending_reviews(limit=5)
        assert len(pending) == 5

    def test_approve(self):
        """Test approve changes status to APPROVED."""
        FeatureFlagManager.set_override("ENABLE_HITL_WORKFLOW", True)
        adapter = HumanReviewAdapter()

        adapter.submit_for_review(
            ReviewRequest(
                request_id="REQ-001",
                agent_name="TestAgent",
                action_type="heal",
                target_file="/test.py",
                description="test",
                risk_level="high",
            ),
        )

        result = adapter.approve("REQ-001", "admin@example.com")

        assert result.status == ReviewStatus.APPROVED
        assert result.reviewer == "admin@example.com"
        assert result.approved_at is not None

    def test_approve_decreases_queue_depth(self):
        """Test approve decreases queue depth."""
        FeatureFlagManager.set_override("ENABLE_HITL_WORKFLOW", True)
        adapter = HumanReviewAdapter()

        adapter.submit_for_review(
            ReviewRequest(
                request_id="REQ-001",
                agent_name="TestAgent",
                action_type="heal",
                target_file="/test.py",
                description="test",
                risk_level="high",
            ),
        )

        assert adapter.get_queue_depth() == 1

        adapter.approve("REQ-001", "admin")

        assert adapter.get_queue_depth() == 0

    def test_approve_not_found(self):
        """Test approve returns cancelled when not found."""
        adapter = HumanReviewAdapter()
        result = adapter.approve("NONEXISTENT", "admin")
        assert result.status == ReviewStatus.CANCELLED
        assert result.reason == "not_found"

    def test_reject(self):
        """Test reject changes status to REJECTED."""
        FeatureFlagManager.set_override("ENABLE_HITL_WORKFLOW", True)
        adapter = HumanReviewAdapter()

        adapter.submit_for_review(
            ReviewRequest(
                request_id="REQ-001",
                agent_name="TestAgent",
                action_type="heal",
                target_file="/test.py",
                description="test",
                risk_level="high",
            ),
        )

        result = adapter.reject("REQ-001", "admin@example.com", "Too risky")

        assert result.status == ReviewStatus.REJECTED
        assert result.reviewer == "admin@example.com"
        assert result.reason == "Too risky"

    def test_reject_not_found(self):
        """Test reject returns cancelled when not found."""
        adapter = HumanReviewAdapter()
        result = adapter.reject("NONEXISTENT", "admin", "reason")
        assert result.status == ReviewStatus.CANCELLED
        assert result.reason == "not_found"

    def test_clear_expired(self):
        """Test clear_expired returns count."""
        adapter = HumanReviewAdapter()
        count = adapter.clear_expired()
        assert count == 0


class TestHumanReviewAdapterProtocolCompliance:
    """Tests for protocol compliance."""

    def test_implements_protocol(self):
        """Test that adapter implements HumanReviewProtocol."""
        from agentic_core.utils.review_protocol_util import HumanReviewProtocol

        adapter = HumanReviewAdapter()
        assert isinstance(adapter, HumanReviewProtocol)

    def test_submit_for_review_returns_review_result(self):
        """Test that submit_for_review returns ReviewResult."""
        adapter = HumanReviewAdapter()
        request = ReviewRequest(
            request_id="REQ-001",
            agent_name="TestAgent",
            action_type="heal",
            target_file="/test.py",
            description="test",
            risk_level="high",
        )

        result = adapter.submit_for_review(request)
        assert isinstance(result, ReviewResult)

    def test_check_status_returns_review_result(self):
        """Test that check_status returns ReviewResult."""
        adapter = HumanReviewAdapter()
        result = adapter.check_status("REQ-001")
        assert isinstance(result, ReviewResult)

    def test_get_pending_reviews_returns_list(self):
        """Test that get_pending_reviews returns list."""
        adapter = HumanReviewAdapter()
        pending = adapter.get_pending_reviews()
        assert isinstance(pending, list)
