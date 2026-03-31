"""Test BaseRfpEngineMixins functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestBaseRfpEngineMixins:
    """Test BaseRfpEngineMixins functionality."""

    def test_base_rfp_engine_mixins_imports(self):
        """Test base_rfp_engine_mixins module imports."""
        from agentic_core import base_rfp_engine_mixins
        assert base_rfp_engine_mixins is not None

    def test_base_rfp_engine_mixins_class(self):
        """Test BaseRfpEngineMixins class exists."""
        from agentic_core import BaseRfpEngineMixins
        assert BaseRfpEngineMixins is not None

    def test_base_rfp_engine_mixins_callable(self):
        """Test base_rfp_engine_mixins functions are callable."""
        from agentic_core import validate_base_rfp_engine_mixins
        assert callable(validate_base_rfp_engine_mixins)
