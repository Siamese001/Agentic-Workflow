"""
Phase 2 Configuration & Base Integration Tests - 100% pass required.

Tests the configuration layer and context integration:
- OrchestrationTopology schema validation
- SovereignConfigLoader singleton
- SovereignContext integration
- BaseRGEngine telemetry wrapper
"""

import pytest
import sys
from pathlib import Path

# Add project root to path for imports BEFORE any app imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from apps_rg.domain.config.schemas import OrchestrationTopology, AgentSpec
from apps_rg.domain.config.loader import SovereignConfigLoader
from apps_rg.engines.base.sovereign_context import SovereignContext
from apps_rg.engines.base.base_resume_engine import BaseRGEngine


def test_schema_validation_success():
    """Ensure valid topology passes schema validation."""
    data = {
        "phases": {"PHASE1": ["AGENT_A"]},
        "agents": {
            "AGENT_A": {
                "name": "AGENT_A",
                "module_path": "path.to.module",
                "inputs": [],
                "outputs": [],
            }
        },
    }
    topology = OrchestrationTopology(**data)
    assert topology.phases["PHASE1"] == ["AGENT_A"]


def test_schema_validation_missing_agent():
    """Ensure topology fails if phase references unknown agent."""
    data = {"phases": {"PHASE1": ["GHOST_AGENT"]}, "agents": {}}
    with pytest.raises(ValueError):
        OrchestrationTopology(**data)


def test_agent_spec_defaults():
    """Verify AgentSpec has correct defaults."""
    spec = AgentSpec(name="TEST", module_path="test.path")
    assert spec.timeout_sec == 30
    assert spec.criticality == "required"
    assert spec.inputs == []
    assert spec.outputs == []


def test_context_integration():
    """Verify Context initializes Buffer and Trace."""
    ctx = SovereignContext()
    assert ctx.buffer is not None
    assert ctx.trace is not None

    # Test Legacy Adapter
    ctx.add_signal("TEST_SIGNAL")
    assert "TEST_SIGNAL" in ctx.signals


def test_context_record_result():
    """Verify record_result creates trace entries."""
    ctx = SovereignContext()
    ctx.record_result("TestAgent", True, "Test passed", {"data": 123})

    traces = ctx.trace.get_traces()
    assert len(traces) >= 1


def test_context_mission_id():
    """Verify mission_id is accessible."""
    ctx = SovereignContext(mission_id="MISSION_001")
    assert ctx.mission_id == "MISSION_001"


def test_sovereign_loader_default_scaffold():
    """Verify loader returns default scaffold when file missing."""
    SovereignConfigLoader.reset()
    topology = SovereignConfigLoader._get_default_scaffold()

    assert "HOP1" in topology.phases
    assert "HOP1_CLERK" in topology.agents
    assert topology.agents["HOP1_CLERK"].module_path.startswith("apps_rg")


@pytest.mark.asyncio
async def test_base_engine_telemetry_wrapper():
    """Verify engine.run() automatically creates trace spans."""
    ctx = SovereignContext()

    class TestEngine(BaseRGEngine):
        async def execute(self):
            return "DONE"

    engine = TestEngine(ctx)
    result = await engine.run()

    assert result == "DONE"
    summary = ctx.trace.get_summary()
    assert summary["total_spans"] == 1
    assert summary["completed"] == 1


@pytest.mark.asyncio
async def test_base_engine_failure_tracking():
    """Verify engine.run() tracks failures correctly."""
    ctx = SovereignContext()

    class FailingEngine(BaseRGEngine):
        async def execute(self):
            raise ValueError("Intentional failure")

    engine = FailingEngine(ctx)

    with pytest.raises(ValueError):
        await engine.run()

    summary = ctx.trace.get_summary()
    assert summary["failures"] == 1


def test_topology_version():
    """Verify topology has version field."""
    data = {"phases": {"P1": ["A1"]}, "agents": {"A1": {"name": "A1", "module_path": "test"}}}
    topology = OrchestrationTopology(**data)
    assert topology.version == "2.5.0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
