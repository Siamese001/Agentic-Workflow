"""Test ProvenancePatternTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestProvenancePatternTypesAdg:
    """Test ProvenancePatternTypesAdg functionality."""

    def test_provenance_pattern_types_adg_imports(self):
        """Test provenance_pattern_types_adg module imports."""
        from agentic_core import provenance_pattern_types_adg
        assert provenance_pattern_types_adg is not None

    def test_provenance_pattern_types_adg_class(self):
        """Test ProvenancePatternTypesAdg class exists."""
        from agentic_core import ProvenancePatternTypesAdg
        assert ProvenancePatternTypesAdg is not None

    def test_provenance_pattern_types_adg_callable(self):
        """Test provenance_pattern_types_adg functions are callable."""
        from agentic_core import validate_provenance_pattern_types_adg
        assert callable(validate_provenance_pattern_types_adg)
