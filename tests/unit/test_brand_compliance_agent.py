"""Test BrandComplianceAgent functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestBrandComplianceAgent:
    """Test BrandComplianceAgent functionality."""

    def test_brand_compliance_agent_imports(self):
        """Test brand_compliance_agent module imports."""
        from agentic_core import brand_compliance_agent
        assert brand_compliance_agent is not None

    def test_brand_compliance_agent_class(self):
        """Test BrandComplianceAgent class exists."""
        from agentic_core import BrandComplianceAgent
        assert BrandComplianceAgent is not None

    def test_brand_compliance_agent_callable(self):
        """Test brand_compliance_agent functions are callable."""
        from agentic_core import validate_brand_compliance_agent
        assert callable(validate_brand_compliance_agent)
