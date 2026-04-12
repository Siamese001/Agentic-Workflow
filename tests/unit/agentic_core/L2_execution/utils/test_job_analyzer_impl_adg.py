"""Test JobAnalyzerImplAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestJobAnalyzerImplAdg:
    """Test JobAnalyzerImplAdg functionality."""

    def test_job_analyzer_impl_adg_imports(self):
        """Test job_analyzer_impl_adg module imports."""
        from agentic_core import job_analyzer_impl_adg

        assert job_analyzer_impl_adg is not None

    def test_job_analyzer_impl_adg_class(self):
        """Test JobAnalyzerImplAdg class exists."""
        from agentic_core import JobAnalyzerImplAdg

        assert JobAnalyzerImplAdg is not None

    def test_job_analyzer_impl_adg_callable(self):
        """Test job_analyzer_impl_adg functions are callable."""
        from agentic_core import validate_job_analyzer_impl_adg

        assert callable(validate_job_analyzer_impl_adg)
