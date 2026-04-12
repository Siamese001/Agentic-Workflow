"""Test BaseExecEngineMixins functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestBaseExecEngineMixins:
    """Test BaseExecEngineMixins functionality."""

    def test_base_exec_engine_mixins_imports(self):
        """Test base_exec_engine_mixins module imports."""
        from agentic_core import base_exec_engine_mixins

        assert base_exec_engine_mixins is not None

    def test_base_exec_engine_mixins_class(self):
        """Test BaseExecEngineMixins class exists."""
        from agentic_core import BaseExecEngineMixins

        assert BaseExecEngineMixins is not None

    def test_base_exec_engine_mixins_callable(self):
        """Test base_exec_engine_mixins functions are callable."""
        from agentic_core import validate_base_exec_engine_mixins

        assert callable(validate_base_exec_engine_mixins)
