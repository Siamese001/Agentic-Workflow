"""Tests for FeatureFlagManager."""

import os

from agentic_core.utils.feature_flags import FeatureFlag, FeatureFlagManager


class TestFeatureFlag:
    """Tests for FeatureFlag dataclass."""

    def test_create_flag(self):
        """Test creating a feature flag."""
        flag = FeatureFlag(
            name="TEST_FLAG",
            default=False,
            description="Test flag",
            required_for_healing=True,
        )
        assert flag.name == "TEST_FLAG"
        assert flag.default is False
        assert flag.description == "Test flag"
        assert flag.required_for_healing is True

    def test_create_flag_defaults(self):
        """Test feature flag default values."""
        flag = FeatureFlag(name="TEST_FLAG")
        assert flag.default is False
        assert flag.description == ""
        assert flag.required_for_healing is False


class TestFeatureFlagManager:
    """Tests for FeatureFlagManager."""

    def setup_method(self):
        """Clear overrides before each test."""
        FeatureFlagManager.clear_all_overrides()

    def teardown_method(self):
        """Clear overrides and env vars after each test."""
        FeatureFlagManager.clear_all_overrides()
        # Clean up any test env vars
        for key in list(os.environ.keys()):
            if key.startswith("ENABLE_") or key == "TEST_FLAG":
                del os.environ[key]

    def test_is_enabled_default_false(self):
        """Test that flags default to False."""
        result = FeatureFlagManager.is_enabled("ENABLE_META_LEARNING")
        assert result is False

    def test_is_enabled_unknown_flag(self):
        """Test that unknown flags return False."""
        result = FeatureFlagManager.is_enabled("UNKNOWN_FLAG")
        assert result is False

    def test_is_enabled_from_env_true(self):
        """Test enabling flag via environment variable."""
        os.environ["ENABLE_META_LEARNING"] = "true"
        result = FeatureFlagManager.is_enabled("ENABLE_META_LEARNING")
        assert result is True

    def test_is_enabled_from_env_various_true_values(self):
        """Test various true values for env var."""
        for value in ["true", "1", "yes", "on", "TRUE", "True", "YES"]:
            os.environ["ENABLE_META_LEARNING"] = value
            FeatureFlagManager.clear_all_overrides()  # Clear cache
            result = FeatureFlagManager.is_enabled("ENABLE_META_LEARNING")
            assert result is True, f"Expected True for '{value}'"

    def test_is_enabled_from_env_false_values(self):
        """Test various false values for env var."""
        for value in ["false", "0", "no", "off", "FALSE", "anything_else"]:
            os.environ["ENABLE_META_LEARNING"] = value
            FeatureFlagManager.clear_all_overrides()  # Clear cache
            result = FeatureFlagManager.is_enabled("ENABLE_META_LEARNING")
            assert result is False, f"Expected False for '{value}'"

    def test_set_override(self):
        """Test setting a runtime override."""
        FeatureFlagManager.set_override("ENABLE_META_LEARNING", True)
        result = FeatureFlagManager.is_enabled("ENABLE_META_LEARNING")
        assert result is True

    def test_set_override_overrides_env(self):
        """Test that override takes precedence over env var."""
        os.environ["ENABLE_META_LEARNING"] = "false"
        FeatureFlagManager.set_override("ENABLE_META_LEARNING", True)
        result = FeatureFlagManager.is_enabled("ENABLE_META_LEARNING")
        assert result is True

    def test_clear_override(self):
        """Test clearing a specific override."""
        FeatureFlagManager.set_override("ENABLE_META_LEARNING", True)
        FeatureFlagManager.clear_override("ENABLE_META_LEARNING")
        result = FeatureFlagManager.is_enabled("ENABLE_META_LEARNING")
        assert result is False  # Back to default

    def test_clear_all_overrides(self):
        """Test clearing all overrides."""
        FeatureFlagManager.set_override("ENABLE_META_LEARNING", True)
        FeatureFlagManager.set_override("ENABLE_AUDIT_TRAIL", True)
        FeatureFlagManager.clear_all_overrides()

        assert FeatureFlagManager.is_enabled("ENABLE_META_LEARNING") is False
        assert FeatureFlagManager.is_enabled("ENABLE_AUDIT_TRAIL") is False

    def test_required_for_healing(self):
        """Test checking if flag is required for healing."""
        assert FeatureFlagManager.required_for_healing("ENABLE_AUDIT_TRAIL") is True
        assert FeatureFlagManager.required_for_healing("ENABLE_META_LEARNING") is False
        assert FeatureFlagManager.required_for_healing("UNKNOWN") is False

    def test_get_all_flags(self):
        """Test getting all flag states."""
        flags = FeatureFlagManager.get_all_flags()
        assert isinstance(flags, dict)
        assert "ENABLE_META_LEARNING" in flags
        assert "ENABLE_AUDIT_TRAIL" in flags
        assert "ENABLE_VERIFICATION_GATE" in flags

    def test_get_healing_required_flags(self):
        """Test getting healing-required flags."""
        flags = FeatureFlagManager.get_healing_required_flags()
        assert isinstance(flags, dict)
        # These should be in the healing required set
        assert "ENABLE_AUDIT_TRAIL" in flags
        assert "ENABLE_VERIFICATION_GATE" in flags
        assert "ENABLE_HITL_WORKFLOW" in flags
        # This should NOT be in healing required
        assert "ENABLE_META_LEARNING" not in flags

    def test_validate_healing_flags_all_disabled(self):
        """Test validation when all healing flags are disabled."""
        all_enabled, disabled = FeatureFlagManager.validate_healing_flags("TestAgent")
        assert all_enabled is False
        assert len(disabled) > 0
        assert "ENABLE_AUDIT_TRAIL" in disabled
        assert "ENABLE_VERIFICATION_GATE" in disabled

    def test_validate_healing_flags_all_enabled(self):
        """Test validation when all healing flags are enabled."""
        # Enable all healing-required flags
        for name, flag in FeatureFlagManager.FLAGS.items():
            if flag.required_for_healing:
                FeatureFlagManager.set_override(name, True)

        all_enabled, disabled = FeatureFlagManager.validate_healing_flags("TestAgent")
        assert all_enabled is True
        assert len(disabled) == 0

    def test_register_flag(self):
        """Test registering a new flag."""
        new_flag = FeatureFlag(
            name="TEST_CUSTOM_FLAG",
            default=True,
            description="Custom test flag",
            required_for_healing=False,
        )
        FeatureFlagManager.register_flag(new_flag)

        assert "TEST_CUSTOM_FLAG" in FeatureFlagManager.FLAGS
        # Note: default is True but env var takes precedence if not set
        info = FeatureFlagManager.get_flag_info("TEST_CUSTOM_FLAG")
        assert info is not None
        assert info["default"] is True

        # Cleanup
        del FeatureFlagManager.FLAGS["TEST_CUSTOM_FLAG"]

    def test_get_flag_info(self):
        """Test getting flag information."""
        info = FeatureFlagManager.get_flag_info("ENABLE_META_LEARNING")
        assert info is not None
        assert info["name"] == "ENABLE_META_LEARNING"
        assert info["default"] is False
        assert info["required_for_healing"] is False
        assert "current_value" in info
        assert "has_override" in info

    def test_get_flag_info_unknown(self):
        """Test getting info for unknown flag."""
        info = FeatureFlagManager.get_flag_info("UNKNOWN_FLAG")
        assert info is None

    def test_get_flag_info_with_override(self):
        """Test flag info shows override status."""
        info = FeatureFlagManager.get_flag_info("ENABLE_META_LEARNING")
        assert info["has_override"] is False

        FeatureFlagManager.set_override("ENABLE_META_LEARNING", True)
        info = FeatureFlagManager.get_flag_info("ENABLE_META_LEARNING")
        assert info["has_override"] is True
        assert info["current_value"] is True

    def test_is_enabled_with_agent_name(self):
        """Test is_enabled logs agent name."""
        # This should not raise an exception
        result = FeatureFlagManager.is_enabled("ENABLE_META_LEARNING", "TestAgent")
        assert result is False


class TestFeatureFlagManagerPredefinedFlags:
    """Tests for predefined flags in FeatureFlagManager."""

    def test_predefined_flags_exist(self):
        """Test that all expected predefined flags exist."""
        expected_flags = [
            "ENABLE_META_LEARNING",
            "ENABLE_AUDIT_TRAIL",
            "ENABLE_COST_GUARDRAIL",
            "ENABLE_HITL_WORKFLOW",
            "ENABLE_VERIFICATION_GATE",
            "ENABLE_DETECTION_SIGNAL",
        ]
        for flag_name in expected_flags:
            assert flag_name in FeatureFlagManager.FLAGS, f"Missing flag: {flag_name}"

    def test_healing_required_flags_correct(self):
        """Test that healing-required flags are correctly marked."""
        healing_required = [
            "ENABLE_AUDIT_TRAIL",
            "ENABLE_COST_GUARDRAIL",
            "ENABLE_HITL_WORKFLOW",
            "ENABLE_VERIFICATION_GATE",
        ]
        not_healing_required = [
            "ENABLE_META_LEARNING",
            "ENABLE_DETECTION_SIGNAL",
        ]

        for name in healing_required:
            flag = FeatureFlagManager.FLAGS.get(name)
            assert flag is not None, f"Missing flag: {name}"
            assert flag.required_for_healing is True, f"{name} should be healing-required"

        for name in not_healing_required:
            flag = FeatureFlagManager.FLAGS.get(name)
            assert flag is not None, f"Missing flag: {name}"
            assert flag.required_for_healing is False, f"{name} should NOT be healing-required"
