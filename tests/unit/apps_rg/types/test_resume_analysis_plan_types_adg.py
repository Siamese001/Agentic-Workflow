"""Test ResumeAnalysisPlanTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestResumeAnalysisPlanTypesAdg:
    """Test ResumeAnalysisPlanTypesAdg functionality."""

    def test_resume_analysis_plan_types_adg_imports(self):
        """Test resume_analysis_plan_types_adg module imports."""
        from agentic_core import resume_analysis_plan_types_adg
        assert resume_analysis_plan_types_adg is not None

    def test_resume_analysis_plan_types_adg_class(self):
        """Test ResumeAnalysisPlanTypesAdg class exists."""
        from agentic_core import ResumeAnalysisPlanTypesAdg
        assert ResumeAnalysisPlanTypesAdg is not None

    def test_resume_analysis_plan_types_adg_callable(self):
        """Test resume_analysis_plan_types_adg functions are callable."""
        from agentic_core import validate_resume_analysis_plan_types_adg
        assert callable(validate_resume_analysis_plan_types_adg)
