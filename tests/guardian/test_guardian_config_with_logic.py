"""Test GuardianConfigWithLogic functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGuardianConfigWithLogic:
    """Test GuardianConfigWithLogic functionality."""

    def test_guardian_config_with_logic_imports(self):
        """Test guardian_config_with_logic module imports."""
        from agentic_core import guardian_config_with_logic
        assert guardian_config_with_logic is not None

    def test_guardian_config_with_logic_class(self):
        """Test GuardianConfigWithLogic class exists."""
        from agentic_core import GuardianConfigWithLogic
        assert GuardianConfigWithLogic is not None

    def test_guardian_config_with_logic_callable(self):
        """Test guardian_config_with_logic functions are callable."""
        from agentic_core import validate_guardian_config_with_logic
        assert callable(validate_guardian_config_with_logic)
