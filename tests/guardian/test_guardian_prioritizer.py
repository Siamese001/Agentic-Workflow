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
        import importlib

        mod = importlib.import_module("agentic_core.adg.applications.guardian_prioritizer")
        assert mod is not None

    def test_guardian_prioritizer_class(self):
        """Test GuardianPrioritizer class exists."""
        import importlib

        mod = importlib.import_module("agentic_core.adg.applications.guardian_prioritizer")
        assert hasattr(mod, "GuardianPrioritizer")

    def test_guardian_prioritizer_callable(self):
        """Test guardian_prioritizer functions are callable."""
        import importlib

        mod = importlib.import_module("agentic_core.adg.applications.guardian_prioritizer")
        assert callable(mod.GuardianPrioritizer)
