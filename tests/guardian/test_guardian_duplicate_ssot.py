"""Test GuardianDuplicateSsot functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGuardianDuplicateSsot:
    """Test GuardianDuplicateSsot functionality."""

    def test_guardian_duplicate_ssot_imports(self):
        """Test guardian_duplicate_ssot module imports."""
        from agentic_core import guardian_duplicate_ssot
        assert guardian_duplicate_ssot is not None

    def test_guardian_duplicate_ssot_class(self):
        """Test GuardianDuplicateSsot class exists."""
        from agentic_core import GuardianDuplicateSsot
        assert GuardianDuplicateSsot is not None

    def test_guardian_duplicate_ssot_callable(self):
        """Test guardian_duplicate_ssot functions are callable."""
        from agentic_core import validate_guardian_duplicate_ssot
        assert callable(validate_guardian_duplicate_ssot)
