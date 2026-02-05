"""Tests for FeatureFlaggedAgentMixin."""

from agentic_core.base_agents.feature_flagged_agent_mixin import FeatureFlaggedAgentMixin
from agentic_core.interfaces.review_protocol import ReviewStatus
from agentic_core.primitives.feature_flags import FeatureFlagManager


class MockAgent(FeatureFlaggedAgentMixin):
    """Mock agent for testing the mixin."""

    def __init__(self):
        super().__init__()
        self.heal_called = False

    def heal_repository(self, violation):
        self.heal_called = True
        return {
            "status": "success",
            "violations_found": 1,
            "violations_fixed": 1,
            "errors": [],
            "skipped": [],
        }


class TestFeatureFlaggedAgentMixin:
    """Tests for FeatureFlaggedAgentMixin."""

    def setup_method(self):
        """Clear overrides before each test."""
        FeatureFlagManager.clear_all_overrides()

    def teardown_method(self):
        """Clear overrides after each test."""
        FeatureFlagManager.clear_all_overrides()

    def test_init_creates_none_instances(self):
        """Test that __init__ creates None placeholders."""
        agent = MockAgent()
        assert agent._verification_gate is None
        assert agent._detection_emitter is None
        assert agent._review_queue is None
        assert agent._meta_learning is None

    def test_is_flag_enabled_default_false(self):
        """Test that flags default to False."""
        agent = MockAgent()
        assert agent._is_flag_enabled("ENABLE_META_LEARNING") is False
        assert agent._is_flag_enabled("ENABLE_VERIFICATION_GATE") is False

    def test_is_flag_enabled_with_override(self):
        """Test that flags can be overridden."""
        FeatureFlagManager.set_override("ENABLE_META_LEARNING", True)
        agent = MockAgent()
        assert agent._is_flag_enabled("ENABLE_META_LEARNING") is True

    def test_validate_healing_flags_all_disabled(self):
        """Test validation when all healing flags are disabled."""
        agent = MockAgent()
        valid, missing = agent._validate_healing_flags()
        assert valid is False
        assert len(missing) > 0

    def test_validate_healing_flags_all_enabled(self):
        """Test validation when all healing flags are enabled."""
        # Enable all healing flags
        for name, flag in FeatureFlagManager.FLAGS.items():
            if flag.required_for_healing:
                FeatureFlagManager.set_override(name, True)

        agent = MockAgent()
        valid, missing = agent._validate_healing_flags()
        assert valid is True
        assert len(missing) == 0

    def test_execute_with_flag_enabled(self):
        """Test _execute_with_flag when flag is enabled."""
        FeatureFlagManager.set_override("ENABLE_META_LEARNING", True)
        agent = MockAgent()

        enabled_called = []
        disabled_called = []

        def enabled_fn():
            enabled_called.append(True)
            return "enabled"

        def disabled_fn():
            disabled_called.append(True)
            return "disabled"

        result = agent._execute_with_flag("ENABLE_META_LEARNING", enabled_fn, disabled_fn)

        assert result == "enabled"
        assert len(enabled_called) == 1
        assert len(disabled_called) == 0

    def test_execute_with_flag_disabled(self):
        """Test _execute_with_flag when flag is disabled."""
        agent = MockAgent()

        enabled_called = []
        disabled_called = []

        def enabled_fn():
            enabled_called.append(True)
            return "enabled"

        def disabled_fn():
            disabled_called.append(True)
            return "disabled"

        result = agent._execute_with_flag("ENABLE_META_LEARNING", enabled_fn, disabled_fn)

        assert result == "disabled"
        assert len(enabled_called) == 0
        assert len(disabled_called) == 1

    def test_execute_with_flag_disabled_no_fallback(self):
        """Test _execute_with_flag when flag disabled and no fallback."""
        agent = MockAgent()

        def enabled_fn():
            return "enabled"

        result = agent._execute_with_flag("ENABLE_META_LEARNING", enabled_fn)
        assert result is None


class TestVerificationGate:
    """Tests for verification gate integration."""

    def setup_method(self):
        FeatureFlagManager.clear_all_overrides()

    def teardown_method(self):
        FeatureFlagManager.clear_all_overrides()

    def test_verification_gate_disabled(self):
        """Test that verification gate returns None when disabled."""
        agent = MockAgent()
        assert agent.verification_gate is None

    def test_verify_action_disabled_returns_success(self):
        """Test that verify_action returns success when disabled."""
        agent = MockAgent()
        result = agent.verify_action(
            file_path="/test.py",
            action_type="modify_function",
            target_node="test_func",
        )
        assert result.success is True
        assert result.reason == "verification_disabled"

    def test_verify_action_enabled_no_implementation(self):
        """Test verify_action when enabled but implementation signature differs."""
        FeatureFlagManager.set_override("ENABLE_VERIFICATION_GATE", True)
        agent = MockAgent()

        result = agent.verify_action(
            file_path="/test.py",
            action_type="modify_function",
            target_node="test_func",
        )
        # Should return success - graceful degradation
        assert result.success is True
        # Reason can be various: verification_unavailable, verification_error, legacy_implementation
        assert result.reason in (
            "verification_unavailable",
            "verification_error",
            "legacy_implementation",
        )


class TestDetectionSignal:
    """Tests for detection signal integration."""

    def setup_method(self):
        FeatureFlagManager.clear_all_overrides()

    def teardown_method(self):
        FeatureFlagManager.clear_all_overrides()

    def test_emit_detection_signal_disabled(self):
        """Test that emit returns None when disabled."""
        agent = MockAgent()
        from agentic_core.interfaces.detection_protocol import Severity

        result = agent.emit_detection_signal(
            detection_type="test",
            file_path="/test.py",
            message="Test message",
            severity=Severity.LOW,
        )
        assert result is None

    def test_emit_detection_signal_enabled_no_implementation(self):
        """Test emit when enabled but no implementation available."""
        FeatureFlagManager.set_override("ENABLE_DETECTION_SIGNAL", True)
        agent = MockAgent()
        from agentic_core.interfaces.detection_protocol import Severity

        result = agent.emit_detection_signal(
            detection_type="test",
            file_path="/test.py",
            message="Test message",
            severity=Severity.LOW,
        )
        # Should return None since no implementation available
        assert result is None


class TestHumanReview:
    """Tests for human review integration."""

    def setup_method(self):
        FeatureFlagManager.clear_all_overrides()

    def teardown_method(self):
        FeatureFlagManager.clear_all_overrides()

    def test_submit_for_review_disabled(self):
        """Test that submit returns auto-approved when disabled."""
        agent = MockAgent()
        result = agent.submit_for_review(
            action_type="heal",
            target_file="/test.py",
            description="Test action",
        )
        assert result.status == ReviewStatus.APPROVED
        assert result.reason == "hitl_disabled"

    def test_check_review_status_disabled(self):
        """Test that check_status returns approved when disabled."""
        agent = MockAgent()
        result = agent.check_review_status("req-123")
        assert result.status == ReviewStatus.APPROVED
        assert result.reason == "hitl_disabled"

    def test_submit_for_review_enabled_no_implementation(self):
        """Test submit when enabled but implementation signature differs."""
        FeatureFlagManager.set_override("ENABLE_HITL_WORKFLOW", True)
        agent = MockAgent()

        result = agent.submit_for_review(
            action_type="heal",
            target_file="/test.py",
            description="Test action",
        )
        # Should auto-approve - graceful degradation
        assert result.status == ReviewStatus.APPROVED
        # Reason can be various: queue_unavailable or legacy_implementation
        assert result.reason in ("queue_unavailable", "legacy_implementation")


class TestMetaLearning:
    """Tests for meta-learning integration."""

    def setup_method(self):
        FeatureFlagManager.clear_all_overrides()

    def teardown_method(self):
        FeatureFlagManager.clear_all_overrides()

    def test_recall_or_execute_disabled(self):
        """Test that recall_or_execute executes directly when disabled."""
        agent = MockAgent()

        executed = []

        def execution_fn():
            executed.append(True)
            return "result"

        result = agent.flagged_recall_or_execute(
            context_key="test",
            operation_type="classify",
            input_hash="abc123",
            execution_fn=execution_fn,
        )

        assert result.success is True
        assert result.from_cache is False
        assert result.result == "result"
        assert len(executed) == 1

    def test_recall_or_execute_disabled_handles_error(self):
        """Test that recall_or_execute handles errors when disabled."""
        agent = MockAgent()

        def failing_fn():
            raise ValueError("test error")

        result = agent.flagged_recall_or_execute(
            context_key="test",
            operation_type="classify",
            input_hash="abc123",
            execution_fn=failing_fn,
        )

        assert result.success is False
        assert result.from_cache is False
        assert "error" in result.metadata

    def test_recall_or_execute_enabled_no_implementation(self):
        """Test recall_or_execute when enabled but no implementation."""
        FeatureFlagManager.set_override("ENABLE_META_LEARNING", True)
        agent = MockAgent()

        executed = []

        def execution_fn():
            executed.append(True)
            return "result"

        result = agent.flagged_recall_or_execute(
            context_key="test",
            operation_type="classify",
            input_hash="abc123",
            execution_fn=execution_fn,
        )

        # Should execute directly when ML unavailable
        assert result.success is True
        assert result.from_cache is False
        assert result.result == "result"
        assert len(executed) == 1


class TestAuditTrail:
    """Tests for audit trail integration."""

    def setup_method(self):
        FeatureFlagManager.clear_all_overrides()

    def teardown_method(self):
        FeatureFlagManager.clear_all_overrides()

    def test_log_audit_event_disabled(self):
        """Test that log_audit_event returns None when disabled."""
        agent = MockAgent()
        result = agent.log_audit_event("test_event", {"key": "value"})
        assert result is None

    def test_log_audit_event_enabled(self):
        """Test that log_audit_event returns event ID when enabled."""
        FeatureFlagManager.set_override("ENABLE_AUDIT_TRAIL", True)
        agent = MockAgent()

        result = agent.log_audit_event("test_event", {"key": "value"})
        assert result is not None
        assert result.startswith("AUDIT-")


class TestHealWithVerification:
    """Tests for heal_with_verification integration."""

    def setup_method(self):
        FeatureFlagManager.clear_all_overrides()

    def teardown_method(self):
        FeatureFlagManager.clear_all_overrides()

    def test_heal_all_flags_disabled(self):
        """Test healing when all flags are disabled."""
        agent = MockAgent()

        violation = {
            "file_path": "/test.py",
            "fix_type": "modify_function",
            "target": "test_func",
            "severity": "low",
            "message": "Test violation",
        }

        def heal_fn(v):
            return {
                "status": "success",
                "violations_found": 1,
                "violations_fixed": 1,
                "errors": [],
                "skipped": [],
            }

        result = agent.heal_with_verification(violation, heal_fn)

        # Should succeed with flags disabled
        assert result["status"] == "success"
        assert result["violations_fixed"] == 1

    def test_heal_verification_enabled(self):
        """Test healing with verification gate enabled."""
        FeatureFlagManager.set_override("ENABLE_VERIFICATION_GATE", True)
        agent = MockAgent()

        violation = {
            "file_path": "/test.py",
            "fix_type": "modify_function",
            "target": "test_func",
            "severity": "low",
            "message": "Test violation",
        }

        def heal_fn(v):
            return {
                "status": "success",
                "violations_found": 1,
                "violations_fixed": 1,
                "errors": [],
                "skipped": [],
            }

        result = agent.heal_with_verification(violation, heal_fn)

        # Should still succeed (verification unavailable -> allowed)
        assert result["status"] == "success"

    def test_heal_high_risk_hitl_disabled(self):
        """Test high-risk healing when HITL is disabled."""
        agent = MockAgent()

        violation = {
            "file_path": "/test.py",
            "fix_type": "modify_function",
            "target": "test_func",
            "severity": "critical",  # High risk
            "message": "Critical violation",
        }

        def heal_fn(v):
            return {
                "status": "success",
                "violations_found": 1,
                "violations_fixed": 1,
                "errors": [],
                "skipped": [],
            }

        result = agent.heal_with_verification(violation, heal_fn)

        # Should proceed without review when HITL disabled
        assert result["status"] == "success"

    def test_classify_violation_risk(self):
        """Test risk classification."""
        agent = MockAgent()

        assert agent._classify_violation_risk({"severity": "critical"}) == "high"
        assert agent._classify_violation_risk({"severity": "high"}) == "high"
        assert agent._classify_violation_risk({"severity": "medium"}) == "medium"
        assert agent._classify_violation_risk({"severity": "low"}) == "low"
        assert agent._classify_violation_risk({}) == "medium"  # default


class TestCapabilityReporting:
    """Tests for capability reporting."""

    def setup_method(self):
        FeatureFlagManager.clear_all_overrides()

    def teardown_method(self):
        FeatureFlagManager.clear_all_overrides()

    def test_get_feature_flag_status(self):
        """Test getting feature flag status."""
        agent = MockAgent()
        status = agent.get_feature_flag_status()

        assert status["agent"] == "MockAgent"
        assert "flags" in status
        assert "healing_enabled" in status
        assert "missing_healing_flags" in status
        assert "verification_gate_available" in status

    def test_get_feature_flag_status_with_flags_enabled(self):
        """Test status when flags are enabled."""
        FeatureFlagManager.set_override("ENABLE_VERIFICATION_GATE", True)
        agent = MockAgent()
        status = agent.get_feature_flag_status()

        assert status["flags"]["ENABLE_VERIFICATION_GATE"] is True
