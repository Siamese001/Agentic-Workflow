"""Test ConstantsQuarantineInvariant functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestConstantsQuarantineInvariant:
    """Test ConstantsQuarantineInvariant functionality."""

    def test_constants_quarantine_invariant_imports(self):
        """Test constants_quarantine_invariant module imports."""
        from agentic_core import constants_quarantine_invariant

        assert constants_quarantine_invariant is not None

    def test_constants_quarantine_invariant_class(self):
        """Test ConstantsQuarantineInvariant class exists."""
        from agentic_core import ConstantsQuarantineInvariant

        assert ConstantsQuarantineInvariant is not None

    def test_constants_quarantine_invariant_callable(self):
        """Test constants_quarantine_invariant functions are callable."""
        from agentic_core import validate_constants_quarantine_invariant

        assert callable(validate_constants_quarantine_invariant)
