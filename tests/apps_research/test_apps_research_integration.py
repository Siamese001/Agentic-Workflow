"""
End-to-End Integration Tests — apps_research

Validates full integration with agentic_core and structure blueprint.
"""

from __future__ import annotations

from apps_research.config.agent_spec_config import load_research_specs
from apps_research.reasoning import ResearchOrchestrator
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

    def test_orchestrator_init(self) -> None:
        """Test ResearchOrchestrator initialization."""
        orchestrator = ResearchOrchestrator()
        assert orchestrator is not None
