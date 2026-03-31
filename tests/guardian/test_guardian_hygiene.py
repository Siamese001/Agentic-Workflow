"""Test GuardianHygiene functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGuardianHygiene:
    """Test GuardianHygiene functionality."""

    def test_guardian_hygiene_imports(self):
        """Test guardian_hygiene module imports."""
        from agentic_core import guardian_hygiene
        assert guardian_hygiene is not None

    def test_guardian_hygiene_class(self):
        """Test GuardianHygiene class exists."""
        from agentic_core import GuardianHygiene
        assert GuardianHygiene is not None

    def test_guardian_hygiene_callable(self):
        """Test guardian_hygiene functions are callable."""
        from agentic_core import validate_guardian_hygiene
        assert callable(validate_guardian_hygiene)
