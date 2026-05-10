"""
End-to-End Integration Tests — apps_research

Validates full integration with agentic_core and structure blueprint.
"""

from __future__ import annotations

import pytest

from apps_research.config.agent_spec_config import load_research_specs
from apps_research.reasoning import (
    InsightExtractionAgent,
    KnowledgeSynthesisAgent,
    ResearchOrchestrator,
    SourceDiscoveryAgent,
)
from apps_research.services import (
    ContentHarvesterService,
    SourceDiscoveryService,
    SynthesisEngineService,
)


class TestAppsResearchIntegration:
    """Integration tests for apps_research."""

    def test_config_loading(self) -> None:
        """Test that config loads with lifecycle trace integration."""
        specs = load_research_specs()
        assert specs is not None
        assert specs.version == "1.0.0"
        assert len(specs.artifact_modes) > 0

    def test_config_has_trace_integration(self) -> None:
        """Verify config has lifecycle trace contract integration."""
        from apps_research.config import agent_spec_config

        assert hasattr(agent_spec_config, "_emit_applies_guardrail")
        assert hasattr(agent_spec_config, "ResearchAgentSpecs")

    def test_source_discovery_service_init(self) -> None:
        """Test SourceDiscoveryService initialization."""
        service = SourceDiscoveryService()
        assert service is not None
        assert hasattr(service, "discover_from_query")
        assert hasattr(service, "discover_from_seed_list")

    def test_synthesis_engine_service_init(self) -> None:
        """Test SynthesisEngineService initialization."""
        service = SynthesisEngineService()
        assert service is not None
        assert hasattr(service, "synthesize_findings")

    def test_content_harvester_service_init(self) -> None:
        """Test ContentHarvesterService initialization."""
        service = ContentHarvesterService()
        assert service is not None

    def test_source_discovery_agent_init(self) -> None:
        """Test SourceDiscoveryAgent initialization."""
        agent = SourceDiscoveryAgent()
        assert agent is not None

    @pytest.mark.asyncio
    async def test_source_discovery_agent_execution(self) -> None:
        """Test SourceDiscoveryAgent execution."""
        agent = SourceDiscoveryAgent()
        result = await agent.discover_sources(
            research_topic="AI governance frameworks",
            source_types=["article", "paper"],
            max_sources=10,
        )
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert "sources" in result

    def test_insight_extraction_agent_init(self) -> None:
        """Test InsightExtractionAgent initialization."""
        agent = InsightExtractionAgent()
        assert agent is not None

    @pytest.mark.asyncio
    async def test_insight_extraction_agent_execution(self) -> None:
        """Test InsightExtractionAgent execution."""
        agent = InsightExtractionAgent()
        sources = [
            {"source_id": "s1", "title": "Source 1", "relevance_score": 0.9},
            {"source_id": "s2", "title": "Source 2", "relevance_score": 0.8},
        ]
        result = await agent.extract_insights(sources=sources)
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert result.get("insights_extracted") == 2

    def test_knowledge_synthesis_agent_init(self) -> None:
        """Test KnowledgeSynthesisAgent initialization."""
        agent = KnowledgeSynthesisAgent()
        assert agent is not None

    @pytest.mark.asyncio
    async def test_knowledge_synthesis_agent_execution(self) -> None:
        """Test KnowledgeSynthesisAgent execution."""
        agent = KnowledgeSynthesisAgent()
        insights = [
            {"theme": "governance", "key_point": "AI governance is critical"},
            {"theme": "safety", "key_point": "Safety measures required"},
        ]
        result = await agent.synthesize(
            insights=insights,
            synthesis_mode="thematic",
            target_audience="technical",
        )
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert "synthesis" in result

    def test_orchestrator_init(self) -> None:
        """Test ResearchOrchestrator initialization."""
        orchestrator = ResearchOrchestrator()
        assert orchestrator is not None
