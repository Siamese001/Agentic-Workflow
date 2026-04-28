"""
End-to-End Integration Tests — apps_exec

Validates full integration with agentic_core and structure blueprint.
"""

from __future__ import annotations

import pytest

from apps_exec.config.agent_spec_config import load_exec_specs
from apps_exec.reasoning import (
    BriefAssemblyAgent,
    ExecOrchestrator,
    SourceIngestionAgent,
    StyleComplianceAgent,
)
from apps_exec.services import (
    BriefAssemblerService,
    CapabilityExtractorService,
    DocumentIngestionService,
)


class TestAppsExecIntegration:
    """Integration tests for apps_exec."""

    def test_config_loading(self) -> None:
        """Test that config loads with lifecycle trace integration."""
        specs = load_exec_specs()
        assert specs is not None
        assert specs.version == "1.0.0"
        assert len(specs.personas) > 0
        assert "recruiter" in specs.personas

    def test_document_ingestion_service_init(self) -> None:
        """Test DocumentIngestionService initialization."""
        service = DocumentIngestionService()
        assert service is not None
        assert hasattr(service, "ingest_directory")
        assert hasattr(service, "ingest_file")

    def test_brief_assembler_service_init(self) -> None:
        """Test BriefAssemblerService initialization."""
        service = BriefAssemblerService()
        assert service is not None
        assert hasattr(service, "assemble_brief")

    def test_capability_extractor_service_init(self) -> None:
        """Test CapabilityExtractorService initialization."""
        service = CapabilityExtractorService()
        assert service is not None

    def test_source_ingestion_agent_init(self) -> None:
        """Test SourceIngestionAgent initialization."""
        agent = SourceIngestionAgent()
        assert agent is not None

    @pytest.mark.asyncio
    async def test_source_ingestion_agent_execution(self) -> None:
        """Test SourceIngestionAgent execution."""
        agent = SourceIngestionAgent()
        result = await agent.ingest_sources(
            source_dirs=["docs/architecture"],
            extensions=[".md"],
        )
        assert isinstance(result, dict)
        assert "success" in result

    def test_brief_assembly_agent_init(self) -> None:
        """Test BriefAssemblyAgent initialization."""
        agent = BriefAssemblyAgent()
        assert agent is not None

    @pytest.mark.asyncio
    async def test_brief_assembly_agent_execution(self) -> None:
        """Test BriefAssemblyAgent execution."""
        agent = BriefAssemblyAgent()
        content_sections = [
            {"heading": "Summary", "content": "Executive summary content here."},
            {"heading": "Capabilities", "content": "Key capabilities content here."},
        ]
        result = await agent.assemble_brief(
            content_sections=content_sections,
            persona_id="recruiter",
            target_word_count=500,
        )
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert "brief" in result

    def test_style_compliance_agent_init(self) -> None:
        """Test StyleComplianceAgent initialization."""
        agent = StyleComplianceAgent()
        assert agent is not None

    @pytest.mark.asyncio
    async def test_style_compliance_agent_execution(self) -> None:
        """Test StyleComplianceAgent execution."""
        agent = StyleComplianceAgent()
        result = await agent.validate_style(
            brief_content="Executive summary with no forbidden phrases.",
            persona_id="recruiter",
        )
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert result.get("compliant") is True

    def test_orchestrator_init(self) -> None:
        """Test ExecOrchestrator initialization."""
        orchestrator = ExecOrchestrator()
        assert orchestrator is not None
