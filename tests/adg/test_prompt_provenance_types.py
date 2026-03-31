"""Test prompt provenance types functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestPromptProvenanceTypes:
    """Test prompt provenance types functionality."""

    def test_prompt_provenance_types_imports(self):
        """Test prompt provenance types module imports."""
        from system_learning.provenance import types
        assert types is not None

    def test_prompt_provenance_event_type(self):
        """Test prompt provenance event type exists."""
        from system_learning.provenance.types import PromptProvenanceEvent
        assert PromptProvenanceEvent is not None

    def test_prompt_provenance_record_type(self):
        """Test prompt provenance record type exists."""
        from system_learning.provenance.types import PromptProvenanceRecord
        assert PromptProvenanceRecord is not None
