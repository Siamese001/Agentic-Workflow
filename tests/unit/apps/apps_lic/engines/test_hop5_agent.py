"""
Unit tests for HOP5GenerationAgent (V2).
Verifies multi-candidate generation, scoring, and V2 architecture compliance.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from apps_lic.utils.archetype_indicator_util import GenerationConfig
from apps_lic.types.ImmutableStagingBuffer import ImmutableStagingBuffer
from apps_lic.types.TraceRegistry import TraceRegistry

from apps_lic.engines.HOP5GenerationAgent import HOP5GenerationAgent

# --- Fixtures ---


@pytest.fixture
def resources():
    return ImmutableStagingBuffer(), TraceRegistry()


@pytest.fixture
def mock_llm():
    llm = MagicMock()
    llm.generate = AsyncMock(return_value="Draft Message Content")
    return llm


@pytest.fixture
def populated_buffer(resources):
    """Pre-load buffer with upstream data."""
    buf, _ = resources
    buf.write_once(
        "hop1_analysis",
        {"Archetype": "C_LEVEL", "recipient_title": "CEO", "recipient_company": "Acme"},
    )
    buf.write_once("hop2_research", {"signal_score": 0.9, "recipient_insights": []})
    buf.write_once("hop3_sender_grounding", {"sender_grounding": {"products": ["A", "B"]}})
    buf.write_once("hop4_routing", {"route": "INMAIL", "constraints": {"char_limit": 500}})
    return buf, resources[1]


@pytest.fixture
def mock_gen_config(monkeypatch):
    """Mock configuration for generation."""
    mock_specs = MagicMock()
    mock_specs.generation_agent = GenerationConfig(
        base_temperatures={"C_LEVEL": 0.7}, c_level_n_candidates=2
    )
    monkeypatch.setattr(
        "agentic_core.mixins.configuration_mixin.get_sovereign_config",
        lambda: mock_specs,
    )
    yield mock_specs


# --- Tests ---


class TestHOP5Generation:
    def test_c_level_multi_candidate(self, mock_gen_config, mock_llm, populated_buffer):
        """Verify C-Level triggers multi-candidate generation."""
        buffer, registry = populated_buffer

        agent = HOP5GenerationAgent(llm_client=mock_llm)
        agent.run_phase(buffer, registry)

        result = buffer.read("hop5_generation")

        # Verify 2 candidates generated (from config)
        assert len(result["all_candidates"]) == 2
        assert result["meta"]["n_candidates"] == 2

        # Verify LLM called twice
        assert mock_llm.generate.call_count == 2

        # Verify Selection
        assert result["selected_draft"]["text"] == "Draft Message Content"

    def test_missing_upstream_input(self, mock_gen_config, mock_llm, resources):
        """Verify crash on missing inputs."""
        buffer, registry = resources
        # Empty buffer

        agent = HOP5GenerationAgent(llm_client=mock_llm)

        with pytest.raises(RuntimeError):
            agent.run_phase(buffer, registry)

        traces = registry.get_traces()
        assert any(t["type"] == "CRITICAL_FAILURE" for t in traces)

    def test_constraint_scoring(self, mock_gen_config, mock_llm, populated_buffer):
        """Verify internal scoring respects constraints."""
        buffer, registry = populated_buffer

        # Mock LLM to return one long and one short draft
        # Side effect: First call Long, Second call Short
        mock_llm.generate = AsyncMock(side_effect=["A" * 600, "A" * 100])

        agent = HOP5GenerationAgent(llm_client=mock_llm)
        agent.run_phase(buffer, registry)

        result = buffer.read("hop5_generation")
        candidates = result["all_candidates"]

        # First candidate (600 chars) > 500 limit -> Score should be low
        assert candidates[0]["score"] < 0

        # Second candidate (100 chars) < 500 limit -> Score should be positive
        assert candidates[1]["score"] > 0

        # Ensure second was selected
        assert result["selected_draft"]["id"] == 1
