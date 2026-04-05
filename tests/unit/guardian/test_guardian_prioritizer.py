"""Test GuardianPrioritizer functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGuardianPrioritizer:
    """Test GuardianPrioritizer functionality."""

    def test_guardian_prioritizer_imports(self):
        """Test guardian_prioritizer module imports."""
        from agentic_core import guardian_prioritizer
        assert guardian_prioritizer is not None

    def test_guardian_prioritizer_class(self):
        """Test GuardianPrioritizer class exists."""
        from agentic_core import GuardianPrioritizer
        assert GuardianPrioritizer is not None

    def test_guardian_prioritizer_callable(self):
        """Test guardian_prioritizer functions are callable."""
        from agentic_core import validate_guardian_prioritizer
        assert callable(validate_guardian_prioritizer)
