"""Test FileHealthScoreTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestFileHealthScoreTypesAdg:
    """Test FileHealthScoreTypesAdg functionality."""

    def test_file_health_score_types_adg_imports(self):
        """Test file_health_score_types_adg module imports."""
        from agentic_core import file_health_score_types_adg

        assert file_health_score_types_adg is not None

    def test_file_health_score_types_adg_class(self):
        """Test FileHealthScoreTypesAdg class exists."""
        from agentic_core import FileHealthScoreTypesAdg

        assert FileHealthScoreTypesAdg is not None

    def test_file_health_score_types_adg_callable(self):
        """Test file_health_score_types_adg functions are callable."""
        from agentic_core import validate_file_health_score_types_adg

        assert callable(validate_file_health_score_types_adg)
