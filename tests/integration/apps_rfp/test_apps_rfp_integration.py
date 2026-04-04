"""
End-to-End Integration Tests — apps_rfp

Validates full integration with agentic_core and structure blueprint.
"""

from __future__ import annotations

import pytest

from apps_rfp.config.agent_spec_config import load_rfp_specs
from apps_rfp.reasoning import (
    ComplianceMappingAgent,
    RequirementAnalysisAgent,
    RfpOrchestrator,
)
from apps_rfp.services import (
    ComplianceCheckerService,
    ProposalArchitectService,
    RequirementParserService,
)


class TestAppsRfpIntegration:
    """Integration tests for apps_rfp."""

    def test_config_loading(self) -> None:
        """Test that config loads with lifecycle trace integration."""
        specs = load_rfp_specs()
        assert specs is not None
        assert specs.version == "1.0.0"
        assert len(specs.sections) > 0
        assert len(specs.industries) > 0

    def test_config_has_trace_integration(self) -> None:
        """Verify config has lifecycle trace contract integration."""
        from apps_rfp.config import agent_spec_config

        assert hasattr(agent_spec_config, "_emit_applies_guardrail")
        assert hasattr(agent_spec_config, "RfpAgentSpecs")

    def test_requirement_parser_service_init(self) -> None:
        """Test RequirementParserService initialization."""
        service = RequirementParserService()
        assert service is not None
        assert hasattr(service, "parse_document")

    def test_compliance_checker_service_init(self) -> None:
        """Test ComplianceCheckerService initialization."""
        service = ComplianceCheckerService()
        assert service is not None
        assert hasattr(service, "check_compliance")

    def test_proposal_architect_service_init(self) -> None:
        """Test ProposalArchitectService initialization."""
        service = ProposalArchitectService()
        assert service is not None

    def test_requirement_analysis_agent_init(self) -> None:
        """Test RequirementAnalysisAgent initialization."""
        agent = RequirementAnalysisAgent()
        assert agent is not None

    @pytest.mark.asyncio
    async def test_requirement_analysis_agent_execution(self) -> None:
        """Test RequirementAnalysisAgent execution."""
        agent = RequirementAnalysisAgent()
        rfp_content = """
        The vendor must provide AI governance capabilities.
        The solution shall support compliance monitoring.
        Preferred: Cloud-native architecture.
        """
        result = await agent.analyze_requirements(rfp_content=rfp_content)
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert "requirements" in result

    def test_compliance_mapping_agent_init(self) -> None:
        """Test ComplianceMappingAgent initialization."""
        agent = ComplianceMappingAgent()
        assert agent is not None

    @pytest.mark.asyncio
    async def test_compliance_mapping_agent_execution(self) -> None:
        """Test ComplianceMappingAgent execution."""
        agent = ComplianceMappingAgent()
        requirements = [
            {"req_id": "r1", "text": "Must support AI governance", "priority": "mandatory"},
            {"req_id": "r2", "text": "Should be cloud-native", "priority": "preferred"},
        ]
        proposal_sections = [
            {"section_id": "s1", "content": "Our solution provides AI governance capabilities."},
        ]
        result = await agent.map_compliance(
            requirements=requirements,
            proposal_sections=proposal_sections,
            strict_mode=False,
        )
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert "compliance" in result

    def test_orchestrator_init(self) -> None:
        """Test RfpOrchestrator initialization."""
        orchestrator = RfpOrchestrator()
        assert orchestrator is not None
