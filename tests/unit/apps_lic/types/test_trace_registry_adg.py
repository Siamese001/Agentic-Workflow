"""Test TraceRegistryAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestTraceRegistryAdg:
    """Test TraceRegistryAdg functionality."""

    def test_trace_registry_adg_imports(self):
        """Test trace_registry_adg module imports."""
        from agentic_core import trace_registry_adg
        assert trace_registry_adg is not None

    def test_trace_registry_adg_class(self):
        """Test TraceRegistryAdg class exists."""
        from agentic_core import TraceRegistryAdg
        assert TraceRegistryAdg is not None

    def test_trace_registry_adg_callable(self):
        """Test trace_registry_adg functions are callable."""
        from agentic_core import validate_trace_registry_adg
        assert callable(validate_trace_registry_adg)
