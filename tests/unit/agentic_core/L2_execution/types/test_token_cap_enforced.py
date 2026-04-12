"""Test TokenCapEnforced functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestTokenCapEnforced:
    """Test TokenCapEnforced functionality."""

    def test_token_cap_enforced_imports(self):
        """Test token_cap_enforced module imports."""
        from agentic_core import token_cap_enforced

        assert token_cap_enforced is not None

    def test_token_cap_enforced_class(self):
        """Test TokenCapEnforced class exists."""
        from agentic_core import TokenCapEnforced

        assert TokenCapEnforced is not None

    def test_token_cap_enforced_callable(self):
        """Test token_cap_enforced functions are callable."""
        from agentic_core import validate_token_cap_enforced

        assert callable(validate_token_cap_enforced)
