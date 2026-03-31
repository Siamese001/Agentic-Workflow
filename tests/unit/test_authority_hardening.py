"""Test AuthorityHardening functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAuthorityHardening:
    """Test AuthorityHardening functionality."""

    def test_authority_hardening_imports(self):
        """Test authority hardening module imports."""
        from agentic_core.L5_safety import authority_hardening
        assert authority_hardening is not None

    def test_authority_hardening_class(self):
        """Test authority hardening class exists."""
        from agentic_core.L5_safety.authority_hardening import AuthorityHardening
        assert AuthorityHardening is not None

    def test_harden_authority(self):
        """Test harden authority function."""
        from agentic_core.L5_safety.authority_hardening import harden_authority
        assert callable(harden_authority)
