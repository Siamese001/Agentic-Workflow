"""Test hardening invariants functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestHardeningInvariants:
    """Test hardening invariants functionality."""

    def test_hardening_invariants_imports(self):
        """Test hardening invariants module imports."""
        from tools.adg import adg_harden
        assert adg_harden is not None

    def test_hardening_invariants_check(self):
        """Test hardening invariants check."""
        from tools.adg.adg_harden import check_invariants
        assert callable(check_invariants)

    def test_hardening_invariants_enforce(self):
        """Test hardening invariants enforce."""
        from tools.adg.adg_harden import enforce_invariants
        assert callable(enforce_invariants)
