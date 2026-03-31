"""Test Phase2DispositionProcessor functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestPhase2DispositionProcessor:
    """Test Phase2DispositionProcessor functionality."""

    def test_phase2_disposition_processor_imports(self):
        """Test phase2_disposition_processor module imports."""
        from agentic_core import phase2_disposition_processor
        assert phase2_disposition_processor is not None

    def test_phase2_disposition_processor_class(self):
        """Test Phase2DispositionProcessor class exists."""
        from agentic_core import Phase2DispositionProcessor
        assert Phase2DispositionProcessor is not None

    def test_phase2_disposition_processor_callable(self):
        """Test phase2_disposition_processor functions are callable."""
        from agentic_core import validate_phase2_disposition_processor
        assert callable(validate_phase2_disposition_processor)
