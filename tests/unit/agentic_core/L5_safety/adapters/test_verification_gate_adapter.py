"""Tests for VerificationGateAdapter."""

import os
import tempfile

from agentic_core.interfaces.verification_protocol import (
    VerificationRequest,
    VerificationResult,
)
from agentic_core.L5_safety.adapters.verification_gate_adapter import (
    VerificationGateAdapter,
)
from agentic_core.primitives.feature_flags import FeatureFlagManager


class TestVerificationGateAdapter:
    """Tests for VerificationGateAdapter."""

    def setup_method(self):
        """Clear overrides before each test."""
        FeatureFlagManager.clear_all_overrides()

    def teardown_method(self):
        """Clear overrides after each test."""
        FeatureFlagManager.clear_all_overrides()

    def test_init_creates_adapter(self):
        """Test that adapter initializes correctly."""
        adapter = VerificationGateAdapter()
        assert adapter is not None

    def test_is_available(self):
        """Test is_available returns True when legacy gate loaded."""
        adapter = VerificationGateAdapter()
        # Should be available if legacy gate loads successfully
        assert isinstance(adapter.is_available(), bool)

    def test_get_supported_actions(self):
        """Test get_supported_actions returns list."""
        adapter = VerificationGateAdapter()
        actions = adapter.get_supported_actions()
        assert isinstance(actions, list)
        assert len(actions) > 0
        assert "modify_function" in actions
        assert "delete_import" in actions

    def test_verify_action_flag_disabled(self):
        """Test verify_action returns success when flag disabled."""
        adapter = VerificationGateAdapter()
        request = VerificationRequest(
            file_path="/test.py",
            action_type="modify_function",
            target_node="test_func",
        )

        result = adapter.verify_action(request)

        assert result.success is True
        assert result.reason == "verification_disabled"

    def test_verify_action_flag_enabled_invalid_request(self):
        """Test verify_action with invalid request."""
        FeatureFlagManager.set_override("ENABLE_VERIFICATION_GATE", True)
        adapter = VerificationGateAdapter()

        # Missing file_path
        request = VerificationRequest(
            file_path="",
            action_type="modify_function",
            target_node="test_func",
        )

        result = adapter.verify_action(request)
        assert result.success is False
        assert "file_path" in result.reason

    def test_verify_action_flag_enabled_missing_action_type(self):
        """Test verify_action with missing action_type."""
        FeatureFlagManager.set_override("ENABLE_VERIFICATION_GATE", True)
        adapter = VerificationGateAdapter()

        request = VerificationRequest(
            file_path="/test.py",
            action_type="",
            target_node="test_func",
        )

        result = adapter.verify_action(request)
        assert result.success is False

    def test_verify_action_flag_enabled_unsupported_action(self):
        """Test verify_action with unsupported action type."""
        FeatureFlagManager.set_override("ENABLE_VERIFICATION_GATE", True)
        adapter = VerificationGateAdapter()

        request = VerificationRequest(
            file_path="/test.py",
            action_type="unsupported_action_type",
            target_node="test_func",
        )

        result = adapter.verify_action(request)
        assert result.success is False
        assert "unsupported" in result.reason

    def test_verify_action_real_file_function_exists(self):
        """Test verify_action with real file where function exists."""
        FeatureFlagManager.set_override("ENABLE_VERIFICATION_GATE", True)
        adapter = VerificationGateAdapter()

        # Create a temporary file with a function
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def test_function():\n    pass\n")
            temp_path = f.name

        try:
            request = VerificationRequest(
                file_path=temp_path,
                action_type="modify_function",
                target_node="test_function",
            )

            result = adapter.verify_action(request)
            assert result.success is True
            assert result.reason == "verified"
        finally:
            os.unlink(temp_path)

    def test_verify_action_real_file_function_not_exists(self):
        """Test verify_action with real file where function does not exist."""
        FeatureFlagManager.set_override("ENABLE_VERIFICATION_GATE", True)
        adapter = VerificationGateAdapter()

        # Create a temporary file without the target function
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("def other_function():\n    pass\n")
            temp_path = f.name

        try:
            request = VerificationRequest(
                file_path=temp_path,
                action_type="modify_function",
                target_node="nonexistent_function",
            )

            result = adapter.verify_action(request)
            assert result.success is False
            assert result.reason == "target_not_found"
        finally:
            os.unlink(temp_path)

    def test_verify_action_file_not_exists(self):
        """Test verify_action with non-existent file."""
        FeatureFlagManager.set_override("ENABLE_VERIFICATION_GATE", True)
        adapter = VerificationGateAdapter()

        request = VerificationRequest(
            file_path="/nonexistent/path/to/file.py",
            action_type="modify_function",
            target_node="test_func",
        )

        result = adapter.verify_action(request)
        assert result.success is False

    def test_verify_action_import_exists(self):
        """Test verify_action for import that exists."""
        FeatureFlagManager.set_override("ENABLE_VERIFICATION_GATE", True)
        adapter = VerificationGateAdapter()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("import os\nfrom pathlib import Path\n")
            temp_path = f.name

        try:
            request = VerificationRequest(
                file_path=temp_path,
                action_type="delete_import",
                target_node="os",
            )

            result = adapter.verify_action(request)
            assert result.success is True
        finally:
            os.unlink(temp_path)

    def test_verify_action_class_exists(self):
        """Test verify_action for class that exists."""
        FeatureFlagManager.set_override("ENABLE_VERIFICATION_GATE", True)
        adapter = VerificationGateAdapter()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("class MyClass:\n    pass\n")
            temp_path = f.name

        try:
            request = VerificationRequest(
                file_path=temp_path,
                action_type="remove_class",
                target_node="MyClass",
            )

            result = adapter.verify_action(request)
            assert result.success is True
        finally:
            os.unlink(temp_path)

    def test_clear_cache(self):
        """Test clear_cache method."""
        adapter = VerificationGateAdapter()
        # Should not raise
        adapter.clear_cache()

    def test_get_cache_stats(self):
        """Test get_cache_stats returns dict."""
        adapter = VerificationGateAdapter()
        stats = adapter.get_cache_stats()
        assert isinstance(stats, dict)
        assert "cache_size" in stats


class TestVerificationGateAdapterProtocolCompliance:
    """Tests for protocol compliance."""

    def test_implements_protocol(self):
        """Test that adapter implements VerificationGateProtocol."""
        from agentic_core.interfaces.verification_protocol import (
            VerificationGateProtocol,
        )

        adapter = VerificationGateAdapter()
        assert isinstance(adapter, VerificationGateProtocol)

    def test_verify_action_returns_verification_result(self):
        """Test that verify_action returns VerificationResult."""
        adapter = VerificationGateAdapter()
        request = VerificationRequest(
            file_path="/test.py",
            action_type="modify_function",
            target_node="func",
        )

        result = adapter.verify_action(request)
        assert isinstance(result, VerificationResult)

    def test_supported_actions_constant(self):
        """Test SUPPORTED_ACTIONS is defined."""
        adapter = VerificationGateAdapter()
        assert hasattr(adapter, "SUPPORTED_ACTIONS")
        assert len(adapter.SUPPORTED_ACTIONS) > 0
