"""Test AnalysisOpsUtilAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestAnalysisOpsUtilAdg:
    """Test AnalysisOpsUtilAdg functionality."""

    def test_analysis_ops_util_adg_imports(self):
        """Test analysis_ops_util_adg module imports."""
        from agentic_core import analysis_ops_util_adg

        assert analysis_ops_util_adg is not None

    def test_analysis_ops_util_adg_class(self):
        """Test AnalysisOpsUtilAdg class exists."""
        from agentic_core import AnalysisOpsUtilAdg

        assert AnalysisOpsUtilAdg is not None

    def test_analysis_ops_util_adg_callable(self):
        """Test analysis_ops_util_adg functions are callable."""
        from agentic_core import validate_analysis_ops_util_adg

        assert callable(validate_analysis_ops_util_adg)
