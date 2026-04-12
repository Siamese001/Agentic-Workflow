"""Test SystemEnforcer functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSystemEnforcer:
    """Test SystemEnforcer functionality."""

    def test_system_enforcer_imports(self):
        """Test system_enforcer module imports."""
        from agentic_core import system_enforcer

        assert system_enforcer is not None

    def test_system_enforcer_class(self):
        """Test SystemEnforcer class exists."""
        from agentic_core import SystemEnforcer

        assert SystemEnforcer is not None

    def test_system_enforcer_callable(self):
        """Test system_enforcer functions are callable."""
        from agentic_core import validate_system_enforcer

        assert callable(validate_system_enforcer)
