"""Test DpoBatchBuilderAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestDpoBatchBuilderAdg:
    """Test DpoBatchBuilderAdg functionality."""

    def test_dpo_batch_builder_adg_imports(self):
        """Test dpo_batch_builder_adg module imports."""
        from agentic_core import dpo_batch_builder_adg

        assert dpo_batch_builder_adg is not None

    def test_dpo_batch_builder_adg_class(self):
        """Test DpoBatchBuilderAdg class exists."""
        from agentic_core import DpoBatchBuilderAdg

        assert DpoBatchBuilderAdg is not None

    def test_dpo_batch_builder_adg_callable(self):
        """Test dpo_batch_builder_adg functions are callable."""
        from agentic_core import validate_dpo_batch_builder_adg

        assert callable(validate_dpo_batch_builder_adg)
