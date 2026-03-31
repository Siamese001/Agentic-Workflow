"""Test Phase3IntelligentDisposition functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestPhase3IntelligentDisposition:
    """Test Phase3IntelligentDisposition functionality."""

    def test_phase3_intelligent_disposition_imports(self):
        """Test phase3_intelligent_disposition module imports."""
        from agentic_core import phase3_intelligent_disposition
        assert phase3_intelligent_disposition is not None

    def test_phase3_intelligent_disposition_class(self):
        """Test Phase3IntelligentDisposition class exists."""
        from agentic_core import Phase3IntelligentDisposition
        assert Phase3IntelligentDisposition is not None

    def test_phase3_intelligent_disposition_callable(self):
        """Test phase3_intelligent_disposition functions are callable."""
        from agentic_core import validate_phase3_intelligent_disposition
        assert callable(validate_phase3_intelligent_disposition)
