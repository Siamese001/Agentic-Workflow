"""
Unit tests for V2AgentBase.
Verifies the Bridge Pattern enforces tracing, config loading, and error handling.
"""

from unittest.mock import MagicMock, patch

import pytest

from apps_lic.domain.config.schemas import AgentSpecs
from apps_lic.shared.foundation.agent_base import V2AgentBase
from apps_lic.shared.foundation.immutable_buffer import ImmutableStagingBuffer
from apps_lic.shared.foundation.trace_registry import TraceRegistry


# Concrete implementation for testing
class ConcreteTestAgent(V2AgentBase):
    def _process(self, buffer: ImmutableStagingBuffer, registry: TraceRegistry) -> None:
        # Simulate work: Read input, write output
        input_val = buffer.read("input_key")
        buffer.write_once("output_key", f"processed_{input_val}")
        registry.add_trace("DEBUG", {"msg": "processing_done"})


class FailingTestAgent(V2AgentBase):
    def _process(self, buffer: ImmutableStagingBuffer, registry: TraceRegistry) -> None:
        raise ValueError("Simulated failure")


class TestV2AgentBase:
    @patch("apps_lic.shared.foundation.agent_base.load_agent_specs")
    def test_initialization_loads_config(self, mock_load):
        """Test that __init__ automatically loads configuration."""
        mock_specs = MagicMock(spec=AgentSpecs)
        mock_load.return_value = mock_specs

        agent = ConcreteTestAgent()

        assert agent.config == mock_specs
        assert agent.toggles is not None
        mock_load.assert_called_once()

    @patch("apps_lic.shared.foundation.agent_base.load_agent_specs")
    def test_run_phase_success_flow(self, mock_load):
        """Test the standard execution flow: Start Trace -> Process -> End Trace."""
        # Setup
        agent = ConcreteTestAgent()
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()

        # Pre-seed buffer
        buffer.write_once("input_key", "test")

        # Execute
        agent.run_phase(buffer, registry)

        # Verify Buffer Output
        assert buffer.read("output_key") == "processed_test"

        # Verify Traces
        traces = registry.get_traces()
        assert len(traces) >= 3
        assert traces[0]["type"] == "PHASE_START"
        assert traces[0]["details"]["agent"] == "ConcreteTestAgent"

        # Verify internal trace from _process
        debug_trace = next(t for t in traces if t["type"] == "DEBUG")
        assert debug_trace["details"]["msg"] == "processing_done"

        assert traces[-1]["type"] == "PHASE_COMPLETE"

    @patch("apps_lic.shared.foundation.agent_base.load_agent_specs")
    def test_run_phase_error_handling(self, mock_load):
        """Test that exceptions are caught, traced, and re-raised."""
        agent = FailingTestAgent()
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()

        # Execute expecting error
        with pytest.raises(RuntimeError) as exc:
            agent.run_phase(buffer, registry)

        assert "FailingTestAgent execution failed" in str(exc.value)

        # Verify Error Trace
        traces = registry.get_traces()
        assert traces[-1]["type"] == "PHASE_ERROR"
        assert "Simulated failure" in traces[-1]["details"]["error"]
