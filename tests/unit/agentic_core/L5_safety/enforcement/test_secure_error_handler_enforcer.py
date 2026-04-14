"""Test SecureErrorHandlerEnforcer functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSecureErrorHandlerEnforcer:
    """Test SecureErrorHandlerEnforcer functionality."""

    def test_secure_error_handler_enforcer_imports(self):
        """Test secure_error_handler_enforcer module imports."""
        from agentic_core import secure_error_handler_enforcer

        assert secure_error_handler_enforcer is not None

    def test_secure_error_handler_enforcer_class(self):
        """Test SecureErrorHandlerEnforcer class exists."""
        from agentic_core import SecureErrorHandlerEnforcer

        assert SecureErrorHandlerEnforcer is not None

    def test_secure_error_handler_enforcer_callable(self):
        """Test secure_error_handler_enforcer functions are callable."""
        from agentic_core import validate_secure_error_handler_enforcer

        assert callable(validate_secure_error_handler_enforcer)

    def test_build_sanitized_context_no_sanitize_returns_empty(self):
        """sanitize_args=False must return {} without inspecting arguments."""
        from agentic_core.L5_safety.enforcement.secure_error_handler_enforcer import _build_sanitized_context

        def fn(name: str) -> None:
            pass

        result = _build_sanitized_context(fn, ("Alice",), {}, sanitize_args=False)
        assert result == {}

    def test_build_sanitized_context_with_sanitize_produces_keys(self):
        """sanitize_args=True must produce arg_<name> keys for string params."""
        from agentic_core.L5_safety.enforcement.secure_error_handler_enforcer import _build_sanitized_context

        def fn(username: str) -> None:
            pass

        result = _build_sanitized_context(fn, ("bob",), {}, sanitize_args=True)
        assert "arg_username" in result

    def test_build_sanitized_context_bind_failure_returns_fallback(self):
        """When inspect.signature fails (e.g. None), fallback key must be returned."""
        from agentic_core.L5_safety.enforcement.secure_error_handler_enforcer import _build_sanitized_context

        result = _build_sanitized_context(None, (), {}, sanitize_args=True)
        assert result == {"arg_binding": "<sanitized>"}
