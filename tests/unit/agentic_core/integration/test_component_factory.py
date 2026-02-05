"""Tests for ComponentFactory."""

from agentic_core.utils.component_factory import (
    ComponentFactory,
    get_detection_emitter,
    get_human_review_queue,
    get_meta_learning_service,
    get_verification_gate,
)
from agentic_core.utils.feature_flags import FeatureFlagManager


class TestComponentFactory:
    """Tests for ComponentFactory."""

    def setup_method(self):
        """Clear state before each test."""
        FeatureFlagManager.clear_all_overrides()
        ComponentFactory.clear_instances()

    def teardown_method(self):
        """Clear state after each test."""
        FeatureFlagManager.clear_all_overrides()
        ComponentFactory.clear_instances()

    def test_get_verification_gate_disabled(self):
        """Test returns None when flag disabled."""
        result = ComponentFactory.get_verification_gate()
        assert result is None

    def test_get_verification_gate_enabled(self):
        """Test returns instance when flag enabled."""
        FeatureFlagManager.set_override("ENABLE_VERIFICATION_GATE", True)
        result = ComponentFactory.get_verification_gate()
        assert result is not None

    def test_get_verification_gate_caches_instance(self):
        """Test that instances are cached."""
        FeatureFlagManager.set_override("ENABLE_VERIFICATION_GATE", True)
        result1 = ComponentFactory.get_verification_gate()
        result2 = ComponentFactory.get_verification_gate()
        assert result1 is result2

    def test_get_human_review_queue_disabled(self):
        """Test returns None when flag disabled."""
        result = ComponentFactory.get_human_review_queue()
        assert result is None

    def test_get_human_review_queue_enabled(self):
        """Test returns instance when flag enabled."""
        FeatureFlagManager.set_override("ENABLE_HITL_WORKFLOW", True)
        result = ComponentFactory.get_human_review_queue()
        assert result is not None

    def test_get_human_review_queue_caches_instance(self):
        """Test that instances are cached."""
        FeatureFlagManager.set_override("ENABLE_HITL_WORKFLOW", True)
        result1 = ComponentFactory.get_human_review_queue()
        result2 = ComponentFactory.get_human_review_queue()
        assert result1 is result2

    def test_get_detection_emitter_disabled(self):
        """Test returns None when flag disabled."""
        result = ComponentFactory.get_detection_emitter()
        assert result is None

    def test_get_meta_learning_service_disabled(self):
        """Test returns None when flag disabled."""
        result = ComponentFactory.get_meta_learning_service()
        assert result is None

    def test_clear_instances(self):
        """Test clearing cached instances."""
        FeatureFlagManager.set_override("ENABLE_VERIFICATION_GATE", True)
        ComponentFactory.get_verification_gate()
        assert "verification_gate" in ComponentFactory._instances

        ComponentFactory.clear_instances()
        assert len(ComponentFactory._instances) == 0

    def test_get_component_status(self):
        """Test getting component status."""
        status = ComponentFactory.get_component_status()

        assert "verification_gate" in status
        assert "human_review" in status
        assert "detection_emitter" in status
        assert "meta_learning" in status

        for component_status in status.values():
            assert "flag_enabled" in component_status
            assert "instance_cached" in component_status

    def test_get_component_status_reflects_flags(self):
        """Test that status reflects flag states."""
        FeatureFlagManager.set_override("ENABLE_VERIFICATION_GATE", True)
        status = ComponentFactory.get_component_status()

        assert status["verification_gate"]["flag_enabled"] is True
        assert status["human_review"]["flag_enabled"] is False

    def test_get_component_status_reflects_cache(self):
        """Test that status reflects cache state."""
        FeatureFlagManager.set_override("ENABLE_VERIFICATION_GATE", True)
        ComponentFactory.get_verification_gate()
        status = ComponentFactory.get_component_status()

        assert status["verification_gate"]["instance_cached"] is True
        assert status["human_review"]["instance_cached"] is False


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def setup_method(self):
        """Clear state before each test."""
        FeatureFlagManager.clear_all_overrides()
        ComponentFactory.clear_instances()

    def teardown_method(self):
        """Clear state after each test."""
        FeatureFlagManager.clear_all_overrides()
        ComponentFactory.clear_instances()

    def test_get_verification_gate_function(self):
        """Test convenience function."""
        result = get_verification_gate()
        assert result is None

        FeatureFlagManager.set_override("ENABLE_VERIFICATION_GATE", True)
        result = get_verification_gate()
        assert result is not None

    def test_get_human_review_queue_function(self):
        """Test convenience function."""
        result = get_human_review_queue()
        assert result is None

        FeatureFlagManager.set_override("ENABLE_HITL_WORKFLOW", True)
        result = get_human_review_queue()
        assert result is not None

    def test_get_detection_emitter_function(self):
        """Test convenience function."""
        result = get_detection_emitter()
        assert result is None

    def test_get_meta_learning_service_function(self):
        """Test convenience function."""
        result = get_meta_learning_service()
        assert result is None
