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
        """Test brand_compliance_agent module imports as module type."""
        import types

        from apps_rg.reasoning import BrandComplianceAgent as brand_compliance_agent_module

        assert brand_compliance_agent_module is not None
        assert isinstance(brand_compliance_agent_module, types.ModuleType)

    def test_brand_compliance_agent_class(self):
        """Test BrandComplianceAgent class exists and is RGValidationExecutor."""
        from apps_rg.reasoning.BrandComplianceAgent import BrandComplianceAgent

        from apps_rg.reasoning.RGValidationExecutor import RGValidationExecutor

        assert BrandComplianceAgent is not None
        assert BrandComplianceAgent == RGValidationExecutor

    def test_brand_compliance_agent_instantiation(self):
        """Test BrandComplianceAgent can be instantiated with rule_set."""
        from apps_rg.reasoning.BrandComplianceAgent import BrandComplianceAgent

        agent = BrandComplianceAgent(rule_set="brand_compliance")
        assert agent is not None
        assert agent.rule_set == "brand_compliance"

    def test_brand_compliance_agent_execute(self):
        """Test BrandComplianceAgent execute method returns validation result."""
        from apps_rg.reasoning.BrandComplianceAgent import BrandComplianceAgent

        agent = BrandComplianceAgent(rule_set="brand_compliance")
        result = agent.execute(resume_data={"tone": "professional"})
        assert isinstance(result, dict)
        assert "issues" in result
        assert "passed" in result
