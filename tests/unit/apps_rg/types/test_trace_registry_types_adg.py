"""Test TraceRegistryTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestTraceRegistryTypesAdg:
    """Test TraceRegistryTypesAdg functionality."""

    def test_trace_registry_types_adg_imports(self):
        """Test trace_registry_types_adg module imports."""
        from agentic_core import trace_registry_types_adg
        assert trace_registry_types_adg is not None

    def test_trace_registry_types_adg_class(self):
        """Test TraceRegistryTypesAdg class exists."""
        from agentic_core import TraceRegistryTypesAdg
        assert TraceRegistryTypesAdg is not None

    def test_trace_registry_types_adg_callable(self):
        """Test trace_registry_types_adg functions are callable."""
        from agentic_core import validate_trace_registry_types_adg
        assert callable(validate_trace_registry_types_adg)
