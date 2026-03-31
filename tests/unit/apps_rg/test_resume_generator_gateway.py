"""Test ResumeGeneratorGateway functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestResumeGeneratorGateway:
    """Test ResumeGeneratorGateway functionality."""

    def test_resume_generator_gateway_imports(self):
        """Test resume_generator_gateway module imports."""
        from agentic_core import resume_generator_gateway
        assert resume_generator_gateway is not None

    def test_resume_generator_gateway_class(self):
        """Test ResumeGeneratorGateway class exists."""
        from agentic_core import ResumeGeneratorGateway
        assert ResumeGeneratorGateway is not None

    def test_resume_generator_gateway_callable(self):
        """Test resume_generator_gateway functions are callable."""
        from agentic_core import validate_resume_generator_gateway
        assert callable(validate_resume_generator_gateway)
