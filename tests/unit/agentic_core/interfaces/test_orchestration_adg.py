"""Test OrchestrationAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestOrchestrationAdg:
    """Test OrchestrationAdg functionality."""

    def test_orchestration_adg_imports(self):
        """Test orchestration_adg module imports."""
        from agentic_core import orchestration_adg

        assert orchestration_adg is not None

    def test_orchestration_adg_class(self):
        """Test OrchestrationAdg class exists."""
        from agentic_core import OrchestrationAdg

        assert OrchestrationAdg is not None

    def test_orchestration_adg_callable(self):
        """Test orchestration_adg functions are callable."""
        from agentic_core import validate_orchestration_adg

        assert callable(validate_orchestration_adg)
