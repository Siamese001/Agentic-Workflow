"""ADG-driven tests for agentic_core/L6_observability/reasoning/observability_probe_executor.py — fan_in=2.

Contract tests: ObservabilityProbeExecutorAgent init, probe dispatch, execute.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L6_observability.reasoning.observability_probe_executor import (
    ObservabilityProbeExecutorAgent,
)


class TestObservabilityProbeExecutorAgentInit:
    def test_creates_with_defaults(self):
        agent = ObservabilityProbeExecutorAgent()
        assert agent is not None

    def test_probe_type_default_generic(self):
        agent = ObservabilityProbeExecutorAgent()
        assert agent.probe_type == "generic"

    def test_probe_type_custom(self):
        agent = ObservabilityProbeExecutorAgent(probe_type="cost_tracker")
        assert agent.probe_type == "cost_tracker"

    def test_results_start_empty(self):
        agent = ObservabilityProbeExecutorAgent()
        assert agent._results == {}

    def test_project_root_is_path(self):
        from pathlib import Path
        agent = ObservabilityProbeExecutorAgent()
        assert isinstance(agent.project_root, Path)


class TestObservabilityProbeExecutorAgentExecute:
    def test_execute_generic_returns_dict(self):
        agent = ObservabilityProbeExecutorAgent(probe_type="generic")
        result = agent.execute()
        assert isinstance(result, dict)

    def test_execute_cost_tracker(self):
        agent = ObservabilityProbeExecutorAgent(probe_type="cost_tracker")
        result = agent.execute({"cost_metrics": {"tokens": 100}})
        assert result.get("probe") == "cost_tracker"

    def test_execute_coordinator(self):
        agent = ObservabilityProbeExecutorAgent(probe_type="coordinator")
        result = agent.execute()
        assert result.get("probe") == "coordinator"

    def test_execute_strategic(self):
        agent = ObservabilityProbeExecutorAgent(probe_type="strategic")
        result = agent.execute()
        assert result.get("probe") == "strategic"

    def test_execute_deadlock(self):
        agent = ObservabilityProbeExecutorAgent(probe_type="deadlock")
        result = agent.execute()
        assert result.get("probe") == "deadlock"

    def test_execute_debate(self):
        agent = ObservabilityProbeExecutorAgent(probe_type="debate")
        result = agent.execute()
        assert result.get("probe") == "debate"

    def test_execute_runtime_telemetry(self):
        agent = ObservabilityProbeExecutorAgent(probe_type="runtime_telemetry")
        result = agent.execute()
        assert result.get("probe") == "runtime_telemetry"

    def test_execute_with_context(self):
        agent = ObservabilityProbeExecutorAgent(probe_type="cost_tracker")
        result = agent.execute({"cost_metrics": {"tokens": 500}})
        assert result["metrics"].get("tokens") == 500

    def test_execute_unknown_probe_returns_empty(self):
        agent = ObservabilityProbeExecutorAgent(probe_type="unknown_xyz")
        result = agent.execute()
        assert isinstance(result, dict)
