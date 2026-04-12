"""Test JitContextAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestJitContextAdg:
    """Test JitContextAdg functionality."""

    def test_jit_context_adg_imports(self):
        """Test jit_context_adg module imports."""
        from agentic_core import jit_context_adg

        assert jit_context_adg is not None

    def test_jit_context_adg_class(self):
        """Test JitContextAdg class exists."""
        from agentic_core import JitContextAdg

        assert JitContextAdg is not None

    def test_jit_context_adg_callable(self):
        """Test jit_context_adg functions are callable."""
        from agentic_core import validate_jit_context_adg

        assert callable(validate_jit_context_adg)
