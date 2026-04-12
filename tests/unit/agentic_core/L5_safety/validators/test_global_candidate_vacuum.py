"""Test GlobalCandidateVacuum functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGlobalCandidateVacuum:
    """Test GlobalCandidateVacuum functionality."""

    def test_global_candidate_vacuum_imports(self):
        """Test global_candidate_vacuum module imports."""
        from agentic_core import global_candidate_vacuum

        assert global_candidate_vacuum is not None

    def test_global_candidate_vacuum_class(self):
        """Test GlobalCandidateVacuum class exists."""
        from agentic_core import GlobalCandidateVacuum

        assert GlobalCandidateVacuum is not None

    def test_global_candidate_vacuum_callable(self):
        """Test global_candidate_vacuum functions are callable."""
        from agentic_core import validate_global_candidate_vacuum

        assert callable(validate_global_candidate_vacuum)
