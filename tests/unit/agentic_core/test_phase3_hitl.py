"""
Phase 3 Test Suite: HITL Integration, Approval Workflows, Human Escalation

Tests for:
- HITLMixin: Approval workflows, escalation, audit trails
- Integration with other Phase mixins
"""

from __future__ import annotations

import pytest
import time

from agentic_core.base_agents.hitl_mixin import (
    HITLMixin,
    ApprovalRequest,
    ApprovalStatus,
    RiskLevel,
    ApprovalRequiredError,
)


# =============================================================================
# Test Fixtures
# =============================================================================


class MockHITLAgent(HITLMixin):
    """Mock agent for testing HITLMixin."""

    def __init__(self):
        super().__init__()


@pytest.fixture
def hitl_agent():
    """Create a fresh HITL agent for each test."""
    return MockHITLAgent()


# =============================================================================
# HITLMixin Initialization Tests
# =============================================================================


class TestHITLInitialization:
    """Test HITLMixin initialization."""

    def test_initialization_flag_set(self, hitl_agent):
        """Verify initialization flag is set."""
        assert hitl_agent._hitl_initialized is True

    def test_default_config(self, hitl_agent):
        """Verify default configuration."""
        config = hitl_agent._hitl_config
        assert config.enabled is True
        assert config.default_timeout_seconds == 300.0
        assert config.auto_approve_low_risk is True

    def test_empty_state_on_init(self, hitl_agent):
        """Verify empty state on initialization."""
        assert hitl_agent._pending_approvals == {}
        assert hitl_agent._approval_history == []
        assert hitl_agent._sensitive_operations == {}


class TestHITLConfiguration:
    """Test HITL configuration methods."""

    def test_configure_hitl_partial(self, hitl_agent):
        """Test partial HITL configuration."""
        hitl_agent.configure_hitl(default_timeout_seconds=600.0)
        assert hitl_agent._hitl_config.default_timeout_seconds == 600.0
        assert hitl_agent._hitl_config.enabled is True  # Unchanged

    def test_configure_hitl_full(self, hitl_agent):
        """Test full HITL configuration."""
        hitl_agent.configure_hitl(
            enabled=False,
            default_timeout_seconds=120.0,
            auto_approve_low_risk=False,
            require_notes_on_rejection=False,
            escalation_timeout_seconds=300.0,
            max_escalation_levels=5,
            default_escalation_chain=["l1", "l2", "l3"],
        )
        config = hitl_agent._hitl_config
        assert config.enabled is False
        assert config.default_timeout_seconds == 120.0
        assert config.auto_approve_low_risk is False
        assert config.require_notes_on_rejection is False
        assert config.escalation_timeout_seconds == 300.0
        assert config.max_escalation_levels == 5
        assert config.default_escalation_chain == ["l1", "l2", "l3"]

    def test_disable_hitl(self, hitl_agent):
        """Test disabling HITL."""
        hitl_agent.configure_hitl(enabled=False)
        assert hitl_agent._hitl_config.enabled is False


class TestSensitiveOperationRegistration:
    """Test sensitive operation registration."""

    def test_register_basic_operation(self, hitl_agent):
        """Test registering a basic sensitive operation."""
        hitl_agent.register_sensitive_operation(
            "delete_files", RiskLevel.HIGH, "Delete files from repository"
        )
        assert "delete_files" in hitl_agent._sensitive_operations
        op = hitl_agent._sensitive_operations["delete_files"]
        assert op["risk_level"] == RiskLevel.HIGH
        assert op["description"] == "Delete files from repository"

    def test_register_with_custom_escalation(self, hitl_agent):
        """Test registering with custom escalation chain."""
        hitl_agent.register_sensitive_operation(
            "deploy_production",
            RiskLevel.CRITICAL,
            escalation_chain=["devops", "cto", "ceo"],
        )
        op = hitl_agent._sensitive_operations["deploy_production"]
        assert op["escalation_chain"] == ["devops", "cto", "ceo"]

    def test_register_with_custom_timeout(self, hitl_agent):
        """Test registering with custom timeout."""
        hitl_agent.register_sensitive_operation(
            "backup_database", RiskLevel.MEDIUM, timeout_seconds=60.0
        )
        op = hitl_agent._sensitive_operations["backup_database"]
        assert op["timeout_seconds"] == 60.0


class TestApprovalRequestCreation:
    """Test approval request creation."""

    def test_create_basic_request(self, hitl_agent):
        """Test creating a basic approval request."""
        hitl_agent.register_sensitive_operation("test_op", RiskLevel.HIGH)
        request = hitl_agent.create_approval_request("test_op")

        assert isinstance(request, ApprovalRequest)
        assert request.operation_name == "test_op"
        assert request.status == ApprovalStatus.PENDING
        assert request.request_id in hitl_agent._pending_approvals

    def test_create_request_with_context(self, hitl_agent):
        """Test creating request with context."""
        hitl_agent.register_sensitive_operation("test_op", RiskLevel.HIGH)
        request = hitl_agent.create_approval_request(
            "test_op", context={"files": ["a.py", "b.py"], "count": 2}
        )

        assert request.context["files"] == ["a.py", "b.py"]
        assert request.context["count"] == 2

    def test_request_has_unique_id(self, hitl_agent):
        """Test that requests have unique IDs."""
        hitl_agent.register_sensitive_operation("test_op", RiskLevel.HIGH)
        req1 = hitl_agent.create_approval_request("test_op")
        req2 = hitl_agent.create_approval_request("test_op")

        assert req1.request_id != req2.request_id


class TestApprovalRequired:
    """Test approval requirement checking."""

    def test_check_approval_required_high_risk(self, hitl_agent):
        """Test approval required for HIGH risk."""
        hitl_agent.register_sensitive_operation("high_risk_op", RiskLevel.HIGH)
        assert hitl_agent.check_approval_required("high_risk_op") is True

    def test_check_approval_not_required_low_risk(self, hitl_agent):
        """Test approval not required for LOW risk with auto-approve."""
        hitl_agent.register_sensitive_operation("low_risk_op", RiskLevel.LOW)
        assert hitl_agent.check_approval_required("low_risk_op") is False

    def test_check_approval_required_low_risk_no_auto(self, hitl_agent):
        """Test approval required for LOW risk without auto-approve."""
        hitl_agent.configure_hitl(auto_approve_low_risk=False)
        hitl_agent.register_sensitive_operation("low_risk_op", RiskLevel.LOW)
        # LOW risk is still below MEDIUM threshold
        assert hitl_agent.check_approval_required("low_risk_op") is False

    def test_check_approval_not_required_unregistered(self, hitl_agent):
        """Test approval not required for unregistered operation."""
        assert hitl_agent.check_approval_required("unknown_op") is False

    def test_check_approval_not_required_disabled(self, hitl_agent):
        """Test approval not required when HITL disabled."""
        hitl_agent.configure_hitl(enabled=False)
        hitl_agent.register_sensitive_operation("high_risk_op", RiskLevel.HIGH)
        assert hitl_agent.check_approval_required("high_risk_op") is False


class TestRequireApproval:
    """Test require_approval method."""

    def test_require_approval_raises_for_high_risk(self, hitl_agent):
        """Test require_approval raises for HIGH risk."""
        hitl_agent.register_sensitive_operation("high_risk_op", RiskLevel.HIGH)

        with pytest.raises(ApprovalRequiredError) as exc_info:
            hitl_agent.require_approval("high_risk_op")

        assert exc_info.value.request.operation_name == "high_risk_op"

    def test_require_approval_auto_approves_low_risk(self, hitl_agent):
        """Test require_approval auto-approves LOW risk."""
        hitl_agent.register_sensitive_operation("low_risk_op", RiskLevel.LOW)

        request = hitl_agent.require_approval("low_risk_op")

        assert request.status == ApprovalStatus.APPROVED
        assert request.resolved_by == "system"

    def test_require_approval_non_blocking(self, hitl_agent):
        """Test require_approval non-blocking mode."""
        hitl_agent.register_sensitive_operation("high_risk_op", RiskLevel.HIGH)

        request = hitl_agent.require_approval("high_risk_op", blocking=False)

        assert request.status == ApprovalStatus.PENDING
        assert request.request_id in hitl_agent._pending_approvals


class TestApprovalWorkflow:
    """Test approval workflow methods."""

    def test_approve_request(self, hitl_agent):
        """Test approving a request."""
        hitl_agent.register_sensitive_operation("test_op", RiskLevel.HIGH)
        request = hitl_agent.create_approval_request("test_op")

        result = hitl_agent.approve(request.request_id, "admin", "Looks good")

        assert result.status == ApprovalStatus.APPROVED
        assert result.resolved_by == "admin"
        assert result.resolution_notes == "Looks good"
        assert request.request_id not in hitl_agent._pending_approvals
        assert result in hitl_agent._approval_history

    def test_reject_request(self, hitl_agent):
        """Test rejecting a request."""
        hitl_agent.register_sensitive_operation("test_op", RiskLevel.HIGH)
        request = hitl_agent.create_approval_request("test_op")

        result = hitl_agent.reject(request.request_id, "admin", "Too risky")

        assert result.status == ApprovalStatus.REJECTED
        assert result.resolved_by == "admin"
        assert result.resolution_notes == "Too risky"

    def test_reject_requires_notes(self, hitl_agent):
        """Test rejection requires notes when configured."""
        hitl_agent.configure_hitl(require_notes_on_rejection=True)
        hitl_agent.register_sensitive_operation("test_op", RiskLevel.HIGH)
        request = hitl_agent.create_approval_request("test_op")

        with pytest.raises(ValueError, match="Rejection notes are required"):
            hitl_agent.reject(request.request_id, "admin", "")

    def test_approve_nonexistent_request(self, hitl_agent):
        """Test approving nonexistent request raises error."""
        with pytest.raises(ValueError, match="not found"):
            hitl_agent.approve("nonexistent-id", "admin")

    def test_approve_already_resolved(self, hitl_agent):
        """Test approving already resolved request raises error."""
        hitl_agent.register_sensitive_operation("test_op", RiskLevel.HIGH)
        request = hitl_agent.create_approval_request("test_op")
        hitl_agent.approve(request.request_id, "admin")

        # After approval, request is moved to history, so it's "not found"
        with pytest.raises(ValueError, match="not found"):
            hitl_agent.approve(request.request_id, "admin2")


class TestEscalation:
    """Test escalation functionality."""

    def test_escalate_request(self, hitl_agent):
        """Test escalating a request."""
        hitl_agent.register_sensitive_operation(
            "test_op",
            RiskLevel.HIGH,
            escalation_chain=["l1", "l2", "l3"],
        )
        request = hitl_agent.create_approval_request("test_op")

        result = hitl_agent.escalate(request.request_id)

        assert result.status == ApprovalStatus.ESCALATED
        assert result.current_escalation_level == 1

    def test_escalate_multiple_levels(self, hitl_agent):
        """Test escalating through multiple levels."""
        hitl_agent.register_sensitive_operation(
            "test_op",
            RiskLevel.HIGH,
            escalation_chain=["l1", "l2", "l3"],
        )
        request = hitl_agent.create_approval_request("test_op")

        hitl_agent.escalate(request.request_id)
        result = hitl_agent.escalate(request.request_id)

        assert result.current_escalation_level == 2

    def test_escalate_max_level_raises(self, hitl_agent):
        """Test escalating beyond max level raises error."""
        hitl_agent.register_sensitive_operation(
            "test_op",
            RiskLevel.HIGH,
            escalation_chain=["l1", "l2"],
        )
        request = hitl_agent.create_approval_request("test_op")

        hitl_agent.escalate(request.request_id)  # Level 1

        with pytest.raises(ValueError, match="Maximum escalation"):
            hitl_agent.escalate(request.request_id)


class TestApprovalTimeout:
    """Test approval timeout functionality."""

    def test_request_expires(self, hitl_agent):
        """Test request expires after timeout."""
        hitl_agent.register_sensitive_operation("test_op", RiskLevel.HIGH, timeout_seconds=0.01)
        request = hitl_agent.create_approval_request("test_op")

        time.sleep(0.02)

        assert request.is_expired() is True

    def test_expired_requests_moved_to_history(self, hitl_agent):
        """Test expired requests are moved to history."""
        hitl_agent.register_sensitive_operation("test_op", RiskLevel.HIGH, timeout_seconds=0.01)
        hitl_agent.create_approval_request("test_op")

        time.sleep(0.02)

        # Getting pending approvals triggers expiration check
        pending = hitl_agent.get_pending_approvals()

        assert len(pending) == 0
        assert len(hitl_agent._approval_history) == 1
        assert hitl_agent._approval_history[0].status == ApprovalStatus.TIMEOUT


class TestApprovalHistory:
    """Test approval history functionality."""

    def test_get_approval_history(self, hitl_agent):
        """Test getting approval history."""
        hitl_agent.register_sensitive_operation("test_op", RiskLevel.HIGH)

        # Create and approve multiple requests
        for i in range(3):
            request = hitl_agent.create_approval_request("test_op")
            hitl_agent.approve(request.request_id, f"admin_{i}")

        history = hitl_agent.get_approval_history()

        assert len(history) == 3
        # Most recent first
        assert history[0]["resolved_by"] == "admin_2"

    def test_get_approval_history_with_limit(self, hitl_agent):
        """Test getting approval history with limit."""
        hitl_agent.register_sensitive_operation("test_op", RiskLevel.HIGH)

        for i in range(5):
            request = hitl_agent.create_approval_request("test_op")
            hitl_agent.approve(request.request_id, f"admin_{i}")

        history = hitl_agent.get_approval_history(limit=2)

        assert len(history) == 2

    def test_get_approval_history_by_operation(self, hitl_agent):
        """Test filtering history by operation name."""
        hitl_agent.register_sensitive_operation("op1", RiskLevel.HIGH)
        hitl_agent.register_sensitive_operation("op2", RiskLevel.HIGH)

        req1 = hitl_agent.create_approval_request("op1")
        req2 = hitl_agent.create_approval_request("op2")
        hitl_agent.approve(req1.request_id, "admin")
        hitl_agent.approve(req2.request_id, "admin")

        history = hitl_agent.get_approval_history(operation_name="op1")

        assert len(history) == 1
        assert history[0]["operation_name"] == "op1"


class TestApprovalCallbacks:
    """Test approval callback functionality."""

    def test_register_callback(self, hitl_agent):
        """Test registering an approval callback."""
        callback_called = []

        def callback(request):
            callback_called.append(request.request_id)

        hitl_agent.register_approval_callback("test_op", callback)
        hitl_agent.register_sensitive_operation("test_op", RiskLevel.HIGH)

        request = hitl_agent.create_approval_request("test_op")
        hitl_agent.approve(request.request_id, "admin")

        assert request.request_id in callback_called

    def test_callback_not_called_on_rejection(self, hitl_agent):
        """Test callback not called on rejection."""
        callback_called = []

        def callback(request):
            callback_called.append(request.request_id)

        hitl_agent.register_approval_callback("test_op", callback)
        hitl_agent.register_sensitive_operation("test_op", RiskLevel.HIGH)

        request = hitl_agent.create_approval_request("test_op")
        hitl_agent.reject(request.request_id, "admin", "Rejected")

        assert len(callback_called) == 0


class TestHITLStatus:
    """Test HITL status reporting."""

    def test_get_hitl_status(self, hitl_agent):
        """Test getting HITL status."""
        hitl_agent.register_sensitive_operation("op1", RiskLevel.HIGH)
        hitl_agent.register_sensitive_operation("op2", RiskLevel.MEDIUM)

        status = hitl_agent.get_hitl_status()

        assert status["enabled"] is True
        assert "op1" in status["registered_operations"]
        assert "op2" in status["registered_operations"]
        assert status["pending_count"] == 0

    def test_get_pending_approvals(self, hitl_agent):
        """Test getting pending approvals."""
        hitl_agent.register_sensitive_operation("test_op", RiskLevel.HIGH)

        hitl_agent.create_approval_request("test_op")
        hitl_agent.create_approval_request("test_op")

        pending = hitl_agent.get_pending_approvals()

        assert len(pending) == 2


class TestApprovalRequestSerialization:
    """Test ApprovalRequest serialization."""

    def test_to_dict(self):
        """Test ApprovalRequest to_dict method."""
        request = ApprovalRequest(
            request_id="test-123",
            operation_name="test_op",
            description="Test operation",
            risk_level=RiskLevel.HIGH,
            context={"key": "value"},
        )

        data = request.to_dict()

        assert data["request_id"] == "test-123"
        assert data["operation_name"] == "test_op"
        assert data["risk_level"] == "HIGH"
        assert data["context"]["key"] == "value"
        assert data["status"] == "pending"


class TestRiskLevels:
    """Test risk level ordering."""

    def test_risk_level_ordering(self):
        """Test risk levels are properly ordered."""
        assert RiskLevel.LOW.value < RiskLevel.MEDIUM.value
        assert RiskLevel.MEDIUM.value < RiskLevel.HIGH.value
        assert RiskLevel.HIGH.value < RiskLevel.CRITICAL.value

    def test_critical_requires_approval(self, hitl_agent):
        """Test CRITICAL risk requires approval."""
        hitl_agent.register_sensitive_operation("critical_op", RiskLevel.CRITICAL)
        assert hitl_agent.check_approval_required("critical_op") is True


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_thread_safety(self, hitl_agent):
        """Test thread safety of HITL operations."""
        import threading

        hitl_agent.register_sensitive_operation("test_op", RiskLevel.HIGH)
        errors = []
        requests_created = []

        def create_and_approve():
            try:
                request = hitl_agent.create_approval_request("test_op")
                requests_created.append(request.request_id)
                hitl_agent.approve(request.request_id, "admin")
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=create_and_approve) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(hitl_agent._approval_history) == 10

    def test_callback_error_handling(self, hitl_agent):
        """Test callback errors don't break approval."""

        def bad_callback(request):
            raise ValueError("Callback error")

        hitl_agent.register_approval_callback("test_op", bad_callback)
        hitl_agent.register_sensitive_operation("test_op", RiskLevel.HIGH)

        request = hitl_agent.create_approval_request("test_op")

        # Should not raise despite callback error
        result = hitl_agent.approve(request.request_id, "admin")
        assert result.status == ApprovalStatus.APPROVED
