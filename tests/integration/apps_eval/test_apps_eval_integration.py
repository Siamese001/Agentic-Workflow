"""
End-to-End Integration Tests — apps_eval

Validates full integration with agentic_core and structure blueprint.
"""

from __future__ import annotations

import pytest

from apps_eval.config.agent_spec_config import load_eval_specs
from apps_eval.reasoning import (
    EvalOrchestrator,
    QualityGateAgent,
    ScenarioGenerationAgent,
    TestDiscoveryAgent,
)
from apps_eval.services import (
    MetricCollectorService,
    ScenarioLoaderService,
    TestDiscoveryService,
)


class TestAppsEvalIntegration:
    """Integration tests for apps_eval."""

    def test_config_loading(self) -> None:
        """Test that config loads with lifecycle trace integration."""
        specs = load_eval_specs()
        assert specs is not None
        assert specs.version == "1.0.0"
        assert len(specs.scorecard_dimensions) > 0
        assert len(specs.benchmark_suites) > 0

    def test_config_has_trace_integration(self) -> None:
        """Verify config has lifecycle trace contract integration."""
        # This test verifies the config module imports and uses lifecycle traces
        # If the module loads without error, trace integration is working
        from apps_eval.config import agent_spec_config

        assert hasattr(agent_spec_config, "_emit_applies_guardrail")
        assert hasattr(agent_spec_config, "EvalAgentSpecs")

    def test_test_discovery_service_init(self) -> None:
        """Test TestDiscoveryService initialization."""
        service = TestDiscoveryService()
        assert service is not None
        assert hasattr(service, "discover_from_adg")
        assert hasattr(service, "discover_from_codebase")

    def test_test_discovery_agent_init(self) -> None:
        """Test TestDiscoveryAgent initialization."""
        agent = TestDiscoveryAgent()
        assert agent is not None

    @pytest.mark.asyncio
    async def test_test_discovery_agent_execution(self) -> None:
        """Test TestDiscoveryAgent execution."""
        agent = TestDiscoveryAgent()
        result = await agent.discover_tests(
            target_modules=["tests/unit/agentic_core"],
            discovery_mode="codebase",
        )
        assert isinstance(result, dict)
        assert "success" in result
        assert "tests_discovered" in result

    def test_scenario_loader_service_init(self) -> None:
        """Test ScenarioLoaderService initialization."""
        service = ScenarioLoaderService()
        assert service is not None
        assert hasattr(service, "load_from_file")
        assert hasattr(service, "validate_scenario")

    def test_scenario_generation_agent_init(self) -> None:
        """Test ScenarioGenerationAgent initialization."""
        agent = ScenarioGenerationAgent()
        assert agent is not None

    @pytest.mark.asyncio
    async def test_scenario_generation_agent_execution(self) -> None:
        """Test ScenarioGenerationAgent execution."""
        agent = ScenarioGenerationAgent()
        result = await agent.generate_scenarios(
            requirements=["Test determinism", "Test governance"],
            scenario_count=3,
        )
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert result.get("scenarios_generated") == 3

    def test_metric_collector_service_init(self) -> None:
        """Test MetricCollectorService initialization."""
        service = MetricCollectorService()
        assert service is not None

    def test_quality_gate_agent_init(self) -> None:
        """Test QualityGateAgent initialization."""
        agent = QualityGateAgent()
        assert agent is not None

    @pytest.mark.asyncio
    async def test_quality_gate_agent_execution(self) -> None:
        """Test QualityGateAgent execution."""
        agent = QualityGateAgent()
        result = await agent.evaluate_quality_gate(
            evaluation_results={"overall_score": 0.85},
            quality_threshold=0.70,
        )
        assert isinstance(result, dict)
        assert result.get("success") is True
        assert result.get("passed") is True

    def test_orchestrator_init(self) -> None:
        """Test EvalOrchestrator initialization."""
        orchestrator = EvalOrchestrator()
        assert orchestrator is not None

    def test_adg_imports_available(self) -> None:
        """Verify ADG lifecycle trace imports are available."""
        from agentic_core.runtime.lifecycle_trace_contract import (
            LayerSegment,
            _emit_records_execution_trace,
            _emit_records_telemetry_event,
            emit_determinism_digest,
            emit_replay_key,
        )

        assert LayerSegment is not None
        assert _emit_records_execution_trace is not None
        assert _emit_records_telemetry_event is not None
        assert emit_determinism_digest is not None
        assert emit_replay_key is not None
