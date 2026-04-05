"""Test GenerateResumeAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGenerateResumeAdg:
    """Test GenerateResumeAdg functionality."""

    def test_generate_resume_adg_imports(self):
        """Test generate_resume_adg module imports."""
        from agentic_core import generate_resume_adg
        assert generate_resume_adg is not None

    def test_generate_resume_adg_class(self):
        """Test GenerateResumeAdg class exists."""
        from agentic_core import GenerateResumeAdg
        assert GenerateResumeAdg is not None

    def test_generate_resume_adg_callable(self):
        """Test generate_resume_adg functions are callable."""
        from agentic_core import validate_generate_resume_adg
        assert callable(validate_generate_resume_adg)
