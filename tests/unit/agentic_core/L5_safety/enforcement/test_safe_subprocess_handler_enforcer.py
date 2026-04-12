"""Test SafeSubprocessHandlerEnforcer functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSafeSubprocessHandlerEnforcer:
    """Test SafeSubprocessHandlerEnforcer functionality."""

    def test_safe_subprocess_handler_enforcer_imports(self):
        """Test safe_subprocess_handler_enforcer module imports."""
        from agentic_core import safe_subprocess_handler_enforcer

        assert safe_subprocess_handler_enforcer is not None

    def test_safe_subprocess_handler_enforcer_class(self):
        """Test SafeSubprocessHandlerEnforcer class exists."""
        from agentic_core import SafeSubprocessHandlerEnforcer

        assert SafeSubprocessHandlerEnforcer is not None

    def test_safe_subprocess_handler_enforcer_callable(self):
        """Test safe_subprocess_handler_enforcer functions are callable."""
        from agentic_core import validate_safe_subprocess_handler_enforcer

        assert callable(validate_safe_subprocess_handler_enforcer)
