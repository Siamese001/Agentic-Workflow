"""Test CompletenessScorerAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCompletenessScorerAdg:
    """Test CompletenessScorerAdg functionality."""

    def test_completeness_scorer_adg_imports(self):
        """Test completeness_scorer_adg module imports."""
        from agentic_core import completeness_scorer_adg

        assert completeness_scorer_adg is not None

    def test_completeness_scorer_adg_class(self):
        """Test CompletenessScorerAdg class exists."""
        from agentic_core import CompletenessScorerAdg

        assert CompletenessScorerAdg is not None

    def test_completeness_scorer_adg_callable(self):
        """Test completeness_scorer_adg functions are callable."""
        from agentic_core import validate_completeness_scorer_adg

        assert callable(validate_completeness_scorer_adg)
