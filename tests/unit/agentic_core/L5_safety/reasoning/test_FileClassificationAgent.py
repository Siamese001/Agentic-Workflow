"""Test Fileclassificationagent functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestFileclassificationagent:
    """Test Fileclassificationagent functionality."""

    def test_FileClassificationAgent_imports(self):
        """Test FileClassificationAgent module imports."""
        from agentic_core import FileClassificationAgent

        assert FileClassificationAgent is not None

    def test_FileClassificationAgent_class(self):
        """Test Fileclassificationagent class exists."""
        from agentic_core import Fileclassificationagent

        assert Fileclassificationagent is not None

    def test_FileClassificationAgent_callable(self):
        """Test FileClassificationAgent functions are callable."""
        from agentic_core import validate_FileClassificationAgent

        assert callable(validate_FileClassificationAgent)
