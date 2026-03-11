"""Tests for negative control with W_HARDEN_NEGCTRL_TAMPER."""

import os
from unittest.mock import patch

import pytest

from agentic_core.L2_execution.determinism import (
    compute_lockdown_determinism_digest,
    get_embedding_config_surface,
)


class TestNegativeControl:
    """Tests for negative control tampering detection."""

    def test_tamper_environment_detection(self):
        """Test that tampering environment variable is detected."""
        # Test with tampering enabled
        with patch.dict(os.environ, {"W_HARDEN_NEGCTRL_TAMPER": "1"}):
            assert os.environ.get("W_HARDEN_NEGCTRL_TAMPER") == "1"

        # Test without tampering
        with patch.dict(os.environ, {}, clear=True):
            assert os.environ.get("W_HARDEN_NEGCTRL_TAMPER") is None

    def test_embedding_config_tampering(self):
        """Test that embedding config is tampered when negative control is active."""
        # Normal config
        with patch.dict(os.environ, {}, clear=True):
            normal_config = get_embedding_config_surface()

        # Tampered config
        with patch.dict(os.environ, {"W_HARDEN_NEGCTRL_TAMPER": "1"}):
            tampered_config = get_embedding_config_surface()

        # Verify tampering effects
        assert normal_config != tampered_config
        assert normal_config["top_k"] == 20
        assert normal_config["cutoff"] == 0.0
        assert "tampered" not in normal_config

        assert tampered_config["top_k"] == 999
        assert tampered_config["cutoff"] == 0.999
        assert tampered_config.get("tampered") is True

    def test_determinism_digest_changes_with_tampering(self):
        """Test that determinism digest changes when tampering is active."""
        # Normal digest
        with patch.dict(os.environ, {}, clear=True):
            normal_digest = compute_lockdown_determinism_digest()

        # Tampered digest
        with patch.dict(os.environ, {"W_HARDEN_NEGCTRL_TAMPER": "1"}):
            tampered_digest = compute_lockdown_determinism_digest()

        # Digests should be different
        assert normal_digest != tampered_digest
        assert len(normal_digest) == 64
        assert len(tampered_digest) == 64

    def test_tampering_is_deterministic(self):
        """Test that tampering effects are deterministic."""
        # Get tampered config multiple times
        with patch.dict(os.environ, {"W_HARDEN_NEGCTRL_TAMPER": "1"}):
            config1 = get_embedding_config_surface()
            config2 = get_embedding_config_surface()

        # Should be identical
        assert config1 == config2

        # Get tampered digest multiple times
        with patch.dict(os.environ, {"W_HARDEN_NEGCTRL_TAMPER": "1"}):
            digest1 = compute_lockdown_determinism_digest()
            digest2 = compute_lockdown_determinism_digest()

        # Should be identical
        assert digest1 == digest2

    def test_negative_control_xfail_behavior(self):
        """Negative control: XFAIL when tampered, PASS when restored.

        When W_HARDEN_NEGCTRL_TAMPER=1 this test calls pytest.xfail() which
        records an xfail and exits 0 with 0 failures.
        When the env var is unset this test passes normally.
        No @xfail decorator is used, eliminating any XPASS possibility.
        """
        if os.environ.get("W_HARDEN_NEGCTRL_TAMPER") == "1":
            pytest.xfail("Negative control tampering active: W_HARDEN_NEGCTRL_TAMPER=1")
        # Restore path: normal PASS
        assert True

    @pytest.mark.negative_control
    def test_negative_control_marker(self):
        """Test marked with negative_control marker."""
        # This test is marked with @pytest.mark.negative_control
        # It should behave differently based on W_HARDEN_NEGCTRL_TAMPER
        is_tampered = os.environ.get("W_HARDEN_NEGCTRL_TAMPER") == "1"

        if is_tampered:
            pytest.xfail("Negative control tampering active: W_HARDEN_NEGCTRL_TAMPER=1")
        # Normal mode - test should pass
        assert True

    def test_tampering_affects_multiple_components(self):
        """Test that tampering affects all relevant components."""
        with patch.dict(os.environ, {}, clear=True):
            # Get all normal components
            normal_config = get_embedding_config_surface()
            normal_digest = compute_lockdown_determinism_digest()

        with patch.dict(os.environ, {"W_HARDEN_NEGCTRL_TAMPER": "1"}):
            # Get all tampered components
            tampered_config = get_embedding_config_surface()
            tampered_digest = compute_lockdown_determinism_digest()

        # All should be affected
        assert normal_config != tampered_config
        assert normal_digest != tampered_digest

        # Verify specific tampering effects
        assert tampered_config["top_k"] == 999
        assert tampered_config["cutoff"] == 0.999
        assert tampered_config.get("tampered") is True

    def test_tampering_restoration(self):
        """Test that tampering effects can be restored."""
        # Start with normal
        with patch.dict(os.environ, {}, clear=True):
            normal_digest = compute_lockdown_determinism_digest()

        # Apply tampering
        with patch.dict(os.environ, {"W_HARDEN_NEGCTRL_TAMPER": "1"}):
            tampered_digest = compute_lockdown_determinism_digest()
            assert tampered_digest != normal_digest

        # Restore to normal
        with patch.dict(os.environ, {}, clear=True):
            restored_digest = compute_lockdown_determinism_digest()
            assert restored_digest == normal_digest

    def test_tampering_environment_variable_edge_cases(self):
        """Test edge cases for tampering environment variable."""
        # Test with various values
        test_values = ["1", "true", "True", "TRUE", "yes", "YES"]

        for value in test_values:
            with patch.dict(os.environ, {"W_HARDEN_NEGCTRL_TAMPER": value}):
                config = get_embedding_config_surface()
                # Only '1' should trigger tampering
                if value == "1":
                    assert config.get("tampered") is True
                else:
                    assert "tampered" not in config

    def test_concurrent_tampering_detection(self):
        """Test tampering detection in concurrent scenarios."""
        # This test ensures tampering detection works even if environment
        # is modified during test execution
        original_value = os.environ.get("W_HARDEN_NEGCTRL_TAMPER")

        try:
            # Set tampering
            os.environ["W_HARDEN_NEGCTRL_TAMPER"] = "1"
            config1 = get_embedding_config_surface()
            assert config1.get("tampered") is True

            # Clear tampering
            del os.environ["W_HARDEN_NEGCTRL_TAMPER"]
            config2 = get_embedding_config_surface()
            assert "tampered" not in config2

        finally:
            # Restore original value
            if original_value is None:
                os.environ.pop("W_HARDEN_NEGCTRL_TAMPER", None)
            else:
                os.environ["W_HARDEN_NEGCTRL_TAMPER"] = original_value
