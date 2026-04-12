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
