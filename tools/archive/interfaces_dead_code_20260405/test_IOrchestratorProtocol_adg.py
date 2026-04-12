"""Test IorchestratorprotocolAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestIorchestratorprotocolAdg:
    """Test IorchestratorprotocolAdg functionality."""

    def test_IOrchestratorProtocol_adg_imports(self):
        """Test IOrchestratorProtocol_adg module imports."""
        from agentic_core import IOrchestratorProtocol_adg

        assert IOrchestratorProtocol_adg is not None

    def test_IOrchestratorProtocol_adg_class(self):
        """Test IorchestratorprotocolAdg class exists."""
        from agentic_core import IorchestratorprotocolAdg

        assert IorchestratorprotocolAdg is not None

    def test_IOrchestratorProtocol_adg_callable(self):
        """Test IOrchestratorProtocol_adg functions are callable."""
        from agentic_core import validate_IOrchestratorProtocol_adg

        assert callable(validate_IOrchestratorProtocol_adg)
