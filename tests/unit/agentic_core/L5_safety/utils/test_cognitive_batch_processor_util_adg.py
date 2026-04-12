"""Test CognitiveBatchProcessorUtilAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCognitiveBatchProcessorUtilAdg:
    """Test CognitiveBatchProcessorUtilAdg functionality."""

    def test_cognitive_batch_processor_util_adg_imports(self):
        """Test cognitive_batch_processor_util_adg module imports."""
        from agentic_core import cognitive_batch_processor_util_adg

        assert cognitive_batch_processor_util_adg is not None

    def test_cognitive_batch_processor_util_adg_class(self):
        """Test CognitiveBatchProcessorUtilAdg class exists."""
        from agentic_core import CognitiveBatchProcessorUtilAdg

        assert CognitiveBatchProcessorUtilAdg is not None

    def test_cognitive_batch_processor_util_adg_callable(self):
        """Test cognitive_batch_processor_util_adg functions are callable."""
        from agentic_core import validate_cognitive_batch_processor_util_adg

        assert callable(validate_cognitive_batch_processor_util_adg)
