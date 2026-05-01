"""
Unit tests for HOP1ProfileAnalysisAgent (V2).
Verifies heuristic logic matches legacy behavior within V2 architecture.
"""

import pytest
from apps_lic.types.ImmutableStagingBuffer import ImmutableStagingBuffer
from apps_lic.types.TraceRegistry import TraceRegistry

from apps_lic.config.loader_config import load_agent_specs
from apps_lic.engines.HOP1ProfileAnalysisAgent import HOP1ProfileAnalysisAgent


@pytest.fixture
def agent():
    """Fixture to initialize agent with loaded config."""
    # Ensure config is loaded
    load_agent_specs(force_reload=False)
    return HOP1ProfileAnalysisAgent()


@pytest.fixture
def resources():
    """Fixture for buffer and registry."""
    return ImmutableStagingBuffer(), TraceRegistry()


class TestHOP1Logic:
    def test_c_level_match(self, agent, resources):
        """Verify C-Level keyword detection."""
        buffer, registry = resources
        buffer.write_once(
            "recipient_profile", {"title": "Chief Executive Officer", "name": "Alice"}
        )

        agent.run_phase(buffer, registry)

        result = buffer.read("hop1_analysis")
        assert result["Archetype"] == "C_LEVEL"
        assert result["confidence"] >= 0.95
        assert "Chief" in result["reasoning"] or "contains indicator" in result["reasoning"]

    def test_vp_match(self, agent, resources):
        """Verify Executive keyword detection."""
        buffer, registry = resources
        buffer.write_once("recipient_profile", {"title": "VP of Engineering", "name": "Bob"})

        agent.run_phase(buffer, registry)

        result = buffer.read("hop1_analysis")
        assert result["Archetype"] == "EXECUTIVE"
        assert result["confidence"] == 0.85

    def test_fallback_logic(self, agent, resources):
        """Verify fallback to default for unknown titles."""
        buffer, registry = resources
        buffer.write_once("recipient_profile", {"title": "Intern", "name": "Charlie"})

        agent.run_phase(buffer, registry)

        result = buffer.read("hop1_analysis")
        # Assuming config default is SENIOR_TA or similar, checking it's the default
        assert result["Archetype"] == agent.config.profile_analysis_agent.default_archetype
        assert result["confidence"] == agent.config.profile_analysis_agent.default_confidence
        assert result["needs_manual_override"] is True

    def test_missing_input_error(self, agent, resources):
        """Verify strict input validation."""
        buffer, registry = resources
        # Buffer is empty

        with pytest.raises(RuntimeError) as exc:
            agent.run_phase(buffer, registry)

        # Verify the error was raised
        assert "HOP1ProfileAnalysisAgent execution failed" in str(exc.value)

        # Verify error was traced
        traces = registry.get_traces()
        error_traces = [t for t in traces if t["type"] == "PHASE_ERROR"]
        assert len(error_traces) > 0
        assert "HOP-1 requires 'recipient_profile'" in error_traces[0]["details"]["error"]

    def test_tracing_integrity(self, agent, resources):
        """Verify traces are recorded."""
        buffer, registry = resources
        buffer.write_once("recipient_profile", {"title": "CEO"})

        agent.run_phase(buffer, registry)

        traces = registry.get_traces()
        types = [t["type"] for t in traces]

        assert "PHASE_START" in types
        assert "DECISION_FINAL" in types
        assert "PHASE_COMPLETE" in types
