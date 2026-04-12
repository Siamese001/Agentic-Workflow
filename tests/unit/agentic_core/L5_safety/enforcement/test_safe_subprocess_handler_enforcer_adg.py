"""Test SafeSubprocessHandlerEnforcerAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSafeSubprocessHandlerEnforcerAdg:
    """Test SafeSubprocessHandlerEnforcerAdg functionality."""

    def test_safe_subprocess_handler_enforcer_adg_imports(self):
        """Test safe_subprocess_handler_enforcer_adg module imports."""
        from agentic_core import safe_subprocess_handler_enforcer_adg

        assert safe_subprocess_handler_enforcer_adg is not None

    def test_safe_subprocess_handler_enforcer_adg_class(self):
        """Test SafeSubprocessHandlerEnforcerAdg class exists."""
        from agentic_core import SafeSubprocessHandlerEnforcerAdg

        assert SafeSubprocessHandlerEnforcerAdg is not None

    def test_safe_subprocess_handler_enforcer_adg_callable(self):
        """Test safe_subprocess_handler_enforcer_adg functions are callable."""
        from agentic_core import validate_safe_subprocess_handler_enforcer_adg

        assert callable(validate_safe_subprocess_handler_enforcer_adg)
