"""Test VllmBackpressureTypes functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestVllmBackpressureTypes:
    """Test VllmBackpressureTypes functionality."""

    def test_vllm_backpressure_types_imports(self):
        """Test vllm_backpressure_types module imports."""
        from agentic_core import vllm_backpressure_types

        assert vllm_backpressure_types is not None

    def test_vllm_backpressure_types_class(self):
        """Test VllmBackpressureTypes class exists."""
        from agentic_core import VllmBackpressureTypes

        assert VllmBackpressureTypes is not None

    def test_vllm_backpressure_types_callable(self):
        """Test vllm_backpressure_types functions are callable."""
        from agentic_core import validate_vllm_backpressure_types

        assert callable(validate_vllm_backpressure_types)
