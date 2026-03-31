"""Test Phase2DispositionProcessorSimple functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestPhase2DispositionProcessorSimple:
    """Test Phase2DispositionProcessorSimple functionality."""

    def test_phase2_disposition_processor_simple_imports(self):
        """Test phase2_disposition_processor_simple module imports."""
        from agentic_core import phase2_disposition_processor_simple
        assert phase2_disposition_processor_simple is not None

    def test_phase2_disposition_processor_simple_class(self):
        """Test Phase2DispositionProcessorSimple class exists."""
        from agentic_core import Phase2DispositionProcessorSimple
        assert Phase2DispositionProcessorSimple is not None

    def test_phase2_disposition_processor_simple_callable(self):
        """Test phase2_disposition_processor_simple functions are callable."""
        from agentic_core import validate_phase2_disposition_processor_simple
        assert callable(validate_phase2_disposition_processor_simple)
