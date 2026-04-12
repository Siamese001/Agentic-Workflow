"""Test C0AuthorityLeak functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestC0AuthorityLeak:
    """Test C0AuthorityLeak functionality."""

    def test_c0_authority_leak_imports(self):
        """Test c0_authority_leak module imports."""
        from agentic_core import c0_authority_leak

        assert c0_authority_leak is not None

    def test_c0_authority_leak_class(self):
        """Test C0AuthorityLeak class exists."""
        from agentic_core import C0AuthorityLeak

        assert C0AuthorityLeak is not None

    def test_c0_authority_leak_callable(self):
        """Test c0_authority_leak functions are callable."""
        from agentic_core import validate_c0_authority_leak

        assert callable(validate_c0_authority_leak)
