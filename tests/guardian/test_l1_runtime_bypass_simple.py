"""Test L1RuntimeBypassSimple functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestL1RuntimeBypassSimple:
    """Test L1RuntimeBypassSimple functionality."""

    def test_l1_runtime_bypass_simple_imports(self):
        """Test l1_runtime_bypass_simple module imports."""
        from agentic_core import l1_runtime_bypass_simple
        assert l1_runtime_bypass_simple is not None

    def test_l1_runtime_bypass_simple_class(self):
        """Test L1RuntimeBypassSimple class exists."""
        from agentic_core import L1RuntimeBypassSimple
        assert L1RuntimeBypassSimple is not None

    def test_l1_runtime_bypass_simple_callable(self):
        """Test l1_runtime_bypass_simple functions are callable."""
        from agentic_core import validate_l1_runtime_bypass_simple
        assert callable(validate_l1_runtime_bypass_simple)
