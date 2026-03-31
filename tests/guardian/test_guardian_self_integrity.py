"""Test GuardianSelfIntegrity functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGuardianSelfIntegrity:
    """Test GuardianSelfIntegrity functionality."""

    def test_guardian_self_integrity_imports(self):
        """Test guardian_self_integrity module imports."""
        from agentic_core import guardian_self_integrity
        assert guardian_self_integrity is not None

    def test_guardian_self_integrity_class(self):
        """Test GuardianSelfIntegrity class exists."""
        from agentic_core import GuardianSelfIntegrity
        assert GuardianSelfIntegrity is not None

    def test_guardian_self_integrity_callable(self):
        """Test guardian_self_integrity functions are callable."""
        from agentic_core import validate_guardian_self_integrity
        assert callable(validate_guardian_self_integrity)
