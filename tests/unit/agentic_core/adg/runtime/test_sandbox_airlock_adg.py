"""Test SandboxAirlockAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSandboxAirlockAdg:
    """Test SandboxAirlockAdg functionality."""

    def test_sandbox_airlock_adg_imports(self):
        """Test sandbox_airlock_adg module imports."""
        from agentic_core import sandbox_airlock_adg

        assert sandbox_airlock_adg is not None

    def test_sandbox_airlock_adg_class(self):
        """Test SandboxAirlockAdg class exists."""
        from agentic_core import SandboxAirlockAdg

        assert SandboxAirlockAdg is not None

    def test_sandbox_airlock_adg_callable(self):
        """Test sandbox_airlock_adg functions are callable."""
        from agentic_core import validate_sandbox_airlock_adg

        assert callable(validate_sandbox_airlock_adg)
