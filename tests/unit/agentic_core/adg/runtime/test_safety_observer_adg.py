"""Test SafetyObserverAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSafetyObserverAdg:
    """Test SafetyObserverAdg functionality."""

    def test_safety_observer_adg_imports(self):
        """Test safety_observer_adg module imports."""
        from agentic_core import safety_observer_adg
        assert safety_observer_adg is not None

    def test_safety_observer_adg_class(self):
        """Test SafetyObserverAdg class exists."""
        from agentic_core import SafetyObserverAdg
        assert SafetyObserverAdg is not None

    def test_safety_observer_adg_callable(self):
        """Test safety_observer_adg functions are callable."""
        from agentic_core import validate_safety_observer_adg
        assert callable(validate_safety_observer_adg)
