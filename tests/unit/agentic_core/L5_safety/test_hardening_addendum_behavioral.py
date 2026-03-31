"""Test HardeningAddendumBehavioral functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestHardeningAddendumBehavioral:
    """Test HardeningAddendumBehavioral functionality."""

    def test_hardening_addendum_behavioral_imports(self):
        """Test hardening_addendum_behavioral module imports."""
        from agentic_core import hardening_addendum_behavioral
        assert hardening_addendum_behavioral is not None

    def test_hardening_addendum_behavioral_class(self):
        """Test HardeningAddendumBehavioral class exists."""
        from agentic_core import HardeningAddendumBehavioral
        assert HardeningAddendumBehavioral is not None

    def test_hardening_addendum_behavioral_callable(self):
        """Test hardening_addendum_behavioral functions are callable."""
        from agentic_core import validate_hardening_addendum_behavioral
        assert callable(validate_hardening_addendum_behavioral)
