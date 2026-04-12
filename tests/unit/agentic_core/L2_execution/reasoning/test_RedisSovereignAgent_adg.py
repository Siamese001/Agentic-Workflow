"""Test RedissovereignagentAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRedissovereignagentAdg:
    """Test RedissovereignagentAdg functionality."""

    def test_RedisSovereignAgent_adg_imports(self):
        """Test RedisSovereignAgent_adg module imports."""
        from agentic_core import RedisSovereignAgent_adg

        assert RedisSovereignAgent_adg is not None

    def test_RedisSovereignAgent_adg_class(self):
        """Test RedissovereignagentAdg class exists."""
        from agentic_core import RedissovereignagentAdg

        assert RedissovereignagentAdg is not None

    def test_RedisSovereignAgent_adg_callable(self):
        """Test RedisSovereignAgent_adg functions are callable."""
        from agentic_core import validate_RedisSovereignAgent_adg

        assert callable(validate_RedisSovereignAgent_adg)
