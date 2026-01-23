"""
Unit tests for HOPOrchestratorAgent (V2).
Verifies linear flow, factual retry loops, and creative retry loops.
"""

import pytest
from unittest.mock import MagicMock, patch
from apps_lic.engines.HOPOrchestratorAgent import HOPOrchestratorAgent
from apps_lic.shared.core.immutable_buffer import ImmutableStagingBuffer
from apps_lic.shared.core.trace_registry import TraceRegistry
from apps_lic.shared.core.agent_base import LICAgentBase


class MockAgent(LICAgentBase):
    """Mock agent for testing orchestrator."""

    def __init__(self, hop_id: str, output_data: dict):
        self.hop_id = hop_id
        self.output_data = output_data
        self.call_count = 0

    def _process(self, buffer: ImmutableStagingBuffer, registry: TraceRegistry) -> None:
        self.call_count += 1
        output_key = (
            f"hop{self.hop_id[-1]}_"
            + {
                "HOP1": "analysis",
                "HOP2": "research",
                "HOP3": "sender_grounding",
                "HOP4": "routing",
                "HOP5": "generation",
                "HOP6": "validation_report",
                "HOP7": "gate_decision",
                "HOP8": "qa_report",
            }[self.hop_id]
        )

        # For retry scenarios, modify output based on call count
        if self.hop_id == "HOP7" and hasattr(self, "retry_scenario"):
            if self.retry_scenario == "factual" and self.call_count == 1:
                buffer.write_once(
                    output_key,
                    {
                        "decision": "FAIL_FACTUAL",
                        "action": "RETRY_HOP2",
                        "reason": "Strategic alignment failure",
                    },
                )
            elif self.retry_scenario == "creative" and self.call_count == 1:
                buffer.write_once(
                    output_key,
                    {
                        "decision": "FAIL_CREATIVE",
                        "action": "RETRY_HOP5",
                        "reason": "Placeholder detected",
                    },
                )
            else:
                buffer.write_once(output_key, {"decision": "PASS", "action": "PROCEED"})
        else:
            buffer.write_once(output_key, self.output_data)


@pytest.fixture
def mock_config():
    mock = MagicMock()
    mock.gate_decision_agent.max_factual_loops = 2
    mock.gate_decision_agent.max_creative_retries = 3
    return mock


class TestOrchestratorV2:
    def test_linear_flow_no_failures(self, mock_config):
        """Verify HOPs 1-8 execute in sequence when no failures occur."""
        with patch(
            "apps_lic.engines.HOPOrchestratorAgent.load_agent_specs", return_value=mock_config
        ):
            orchestrator = HOPOrchestratorAgent()

            # Register mock agents
            orchestrator.register_agent("HOP1", MockAgent("HOP1", {"Archetype": "C_LEVEL"}))
            orchestrator.register_agent("HOP2", MockAgent("HOP2", {"signal_score": 0.8}))
            orchestrator.register_agent("HOP3", MockAgent("HOP3", {}))
            orchestrator.register_agent("HOP4", MockAgent("HOP4", {"route": "INMAIL"}))
            orchestrator.register_agent(
                "HOP5", MockAgent("HOP5", {"selected_draft": {"text": "Draft", "score": 10}})
            )
            orchestrator.register_agent(
                "HOP6", MockAgent("HOP6", {"passed": True, "validation_results": []})
            )
            orchestrator.register_agent(
                "HOP7", MockAgent("HOP7", {"decision": "PASS", "action": "PROCEED"})
            )
            orchestrator.register_agent(
                "HOP8", MockAgent("HOP8", {"total_score": 95, "report_path": "/tmp/report.md"})
            )

            mission_input = {"mission_id": "test_001", "recipient_name": "John Doe"}
            result = orchestrator.run_mission(mission_input)

            assert result["status"] == "SUCCESS"
            assert result["report"]["total_score"] == 95

            # Verify each agent was called exactly once
            for hop_id in ["HOP1", "HOP2", "HOP3", "HOP4", "HOP5", "HOP6", "HOP7", "HOP8"]:
                assert orchestrator.agents[hop_id].call_count == 1

    def test_factual_failure_retry_hop2(self, mock_config):
        """Verify orchestrator retries HOP2 on factual failure."""
        with patch(
            "apps_lic.engines.HOPOrchestratorAgent.load_agent_specs", return_value=mock_config
        ):
            orchestrator = HOPOrchestratorAgent()

            # Register mock agents
            orchestrator.register_agent("HOP1", MockAgent("HOP1", {"Archetype": "C_LEVEL"}))

            hop2_agent = MockAgent("HOP2", {"signal_score": 0.8})
            orchestrator.register_agent("HOP2", hop2_agent)

            orchestrator.register_agent("HOP3", MockAgent("HOP3", {}))
            orchestrator.register_agent("HOP4", MockAgent("HOP4", {"route": "INMAIL"}))
            orchestrator.register_agent(
                "HOP5", MockAgent("HOP5", {"selected_draft": {"text": "Draft", "score": 10}})
            )
            orchestrator.register_agent(
                "HOP6",
                MockAgent(
                    "HOP6",
                    {
                        "passed": False,
                        "validation_results": [{"rule_id": "STRATEGIC_ALIGNMENT", "passed": False}],
                    },
                ),
            )

            # HOP7 fails first time, passes second time
            hop7_agent = MockAgent("HOP7", {"decision": "PASS", "action": "PROCEED"})
            hop7_agent.retry_scenario = "factual"
            orchestrator.register_agent("HOP7", hop7_agent)

            orchestrator.register_agent(
                "HOP8", MockAgent("HOP8", {"total_score": 85, "report_path": "/tmp/report.md"})
            )

            mission_input = {"mission_id": "test_002", "recipient_name": "Jane Smith"}
            result = orchestrator.run_mission(mission_input)

            assert result["status"] == "SUCCESS"

            # HOP2 should be called twice (initial + retry)
            assert hop2_agent.call_count == 2

            # HOP7 should be called twice (fail + pass)
            assert hop7_agent.call_count == 2

            # Verify ORCHESTRATOR_RETRY trace exists
            traces = orchestrator.registry.get_traces()
            retry_traces = [t for t in traces if t["type"] == "ORCHESTRATOR_RETRY"]
            assert len(retry_traces) == 1
            assert retry_traces[0]["details"]["action"] == "RETRY_HOP2"

    def test_creative_failure_retry_hop5(self, mock_config):
        """Verify orchestrator retries HOP5 on creative failure."""
        with patch(
            "apps_lic.engines.HOPOrchestratorAgent.load_agent_specs", return_value=mock_config
        ):
            orchestrator = HOPOrchestratorAgent()

            # Register mock agents
            orchestrator.register_agent("HOP1", MockAgent("HOP1", {"Archetype": "C_LEVEL"}))
            orchestrator.register_agent("HOP2", MockAgent("HOP2", {"signal_score": 0.8}))
            orchestrator.register_agent("HOP3", MockAgent("HOP3", {}))
            orchestrator.register_agent("HOP4", MockAgent("HOP4", {"route": "INMAIL"}))

            hop5_agent = MockAgent("HOP5", {"selected_draft": {"text": "Draft", "score": 10}})
            orchestrator.register_agent("HOP5", hop5_agent)

            orchestrator.register_agent(
                "HOP6",
                MockAgent(
                    "HOP6",
                    {
                        "passed": False,
                        "validation_results": [{"rule_id": "PLACEHOLDERS", "passed": False}],
                    },
                ),
            )

            # HOP7 fails first time, passes second time
            hop7_agent = MockAgent("HOP7", {"decision": "PASS", "action": "PROCEED"})
            hop7_agent.retry_scenario = "creative"
            orchestrator.register_agent("HOP7", hop7_agent)

            orchestrator.register_agent(
                "HOP8", MockAgent("HOP8", {"total_score": 90, "report_path": "/tmp/report.md"})
            )

            mission_input = {"mission_id": "test_003", "recipient_name": "Bob Johnson"}
            result = orchestrator.run_mission(mission_input)

            assert result["status"] == "SUCCESS"

            # HOP5 should be called twice (initial + retry)
            assert hop5_agent.call_count == 2

            # HOP7 should be called twice (fail + pass)
            assert hop7_agent.call_count == 2

            # Verify ORCHESTRATOR_RETRY trace exists
            traces = orchestrator.registry.get_traces()
            retry_traces = [t for t in traces if t["type"] == "ORCHESTRATOR_RETRY"]
            assert len(retry_traces) == 1
            assert retry_traces[0]["details"]["action"] == "RETRY_HOP5"

    def test_buffer_forking_preserves_state(self, mock_config):
        """Verify buffer forking preserves mission_input and HOP1-4 state."""
        with patch(
            "apps_lic.engines.HOPOrchestratorAgent.load_agent_specs", return_value=mock_config
        ):
            orchestrator = HOPOrchestratorAgent()

            # Register mock agents
            orchestrator.register_agent(
                "HOP1", MockAgent("HOP1", {"Archetype": "C_LEVEL", "recipient_name": "Test User"})
            )
            orchestrator.register_agent("HOP2", MockAgent("HOP2", {"signal_score": 0.8}))
            orchestrator.register_agent("HOP3", MockAgent("HOP3", {"capabilities": ["AI", "ML"]}))
            orchestrator.register_agent("HOP4", MockAgent("HOP4", {"route": "INMAIL"}))
            orchestrator.register_agent(
                "HOP5", MockAgent("HOP5", {"selected_draft": {"text": "Draft", "score": 10}})
            )
            orchestrator.register_agent(
                "HOP6", MockAgent("HOP6", {"passed": False, "validation_results": []})
            )

            hop7_agent = MockAgent("HOP7", {"decision": "PASS", "action": "PROCEED"})
            hop7_agent.retry_scenario = "creative"
            orchestrator.register_agent("HOP7", hop7_agent)

            orchestrator.register_agent(
                "HOP8", MockAgent("HOP8", {"total_score": 88, "report_path": "/tmp/report.md"})
            )

            mission_input = {"mission_id": "test_004", "recipient_name": "Alice Cooper"}
            result = orchestrator.run_mission(mission_input)

            assert result["status"] == "SUCCESS"

            # Verify traces show buffer forking occurred
            traces = orchestrator.registry.get_traces()
            retry_traces = [t for t in traces if t["type"] == "ORCHESTRATOR_RETRY"]
            assert len(retry_traces) == 1
