"""
Unit tests for HOP4RoutingAgent (V2).
Verifies rule-based routing logic and V2 architecture compliance.
"""

from unittest.mock import MagicMock, patch

import pytest

from apps_lic.domain.config.schemas import (
    RouteConditions,
    RouteConstraints,
    RouteDef,
    RoutingConfig,
)
from apps_lic.engines.HOP4RoutingAgent import HOP4RoutingAgent
from apps_lic.shared.foundation.immutable_buffer import ImmutableStagingBuffer
from apps_lic.shared.foundation.trace_registry import TraceRegistry

# --- Fixtures ---


@pytest.fixture
def resources():
    """Standard V2 resources."""
    return ImmutableStagingBuffer(), TraceRegistry()


@pytest.fixture
def mock_routing_config():
    """
    Creates a standard routing configuration mirroring production rules.
    """
    return RoutingConfig(
        routing_rules={
            "CONNECTION_REQUEST": RouteDef(
                conditions=RouteConditions(
                    connection_status="NOT_CONNECTED", prior_message_count=0
                ),
                constraints=RouteConstraints(word_range=[0, 300], char_limit=300),
            ),
            "DIRECT_MESSAGE": RouteDef(
                conditions=RouteConditions(connection_status="CONNECTED"),
                constraints=RouteConstraints(word_range=[50, 200], char_limit=2000),
            ),
            # INMAIL rules often have 'prior_message_count_gt: 0' logic
            "INMAIL": RouteDef(
                conditions=RouteConditions(
                    connection_status="NOT_CONNECTED", prior_message_count_gt=0
                ),
                constraints=RouteConstraints(word_range=[0, 2000], char_limit=2000),
            ),
        }
    )


@pytest.fixture
def agent_with_config(mock_routing_config):
    """Initializes agent with mocked configuration."""
    mock_specs = MagicMock()
    mock_specs.routing_agent = mock_routing_config

    with patch("apps_lic.shared.foundation.agent_base.load_agent_specs", return_value=mock_specs):
        return HOP4RoutingAgent()


# --- Tests ---


class TestHOP4RoutingLogic:
    def test_route_connection_request(self, agent_with_config, resources):
        """
        Scenario: Not Connected, 0 prior messages.
        Expected: Route = CONNECTION_REQUEST.
        """
        buffer, registry = resources

        # Input State
        buffer.write_once(
            "mission_input", {"connection_status": "NOT_CONNECTED", "prior_message_count": 0}
        )
        buffer.write_once("hop1_analysis", {"Archetype": "C_LEVEL"})  # Context only

        # Execute
        agent_with_config.run_phase(buffer, registry)

        # Verify Output
        result = buffer.read("hop4_routing")
        assert result["route"] == "CONNECTION_REQUEST"
        assert result["constraints"]["char_limit"] == 300

        # Verify Trace
        traces = registry.get_traces()
        decision = next(t for t in traces if t["type"] == "DECISION_FINAL")
        assert decision["details"]["route"] == "CONNECTION_REQUEST"

    def test_route_direct_message(self, agent_with_config, resources):
        """
        Scenario: Connected (message count irrelevant in this config).
        Expected: Route = DIRECT_MESSAGE.
        """
        buffer, registry = resources

        buffer.write_once(
            "mission_input", {"connection_status": "CONNECTED", "prior_message_count": 5}
        )

        agent_with_config.run_phase(buffer, registry)

        result = buffer.read("hop4_routing")
        assert result["route"] == "DIRECT_MESSAGE"
        assert result["constraints"]["char_limit"] == 2000

    def test_route_inmail_logic(self, agent_with_config, resources):
        """
        Scenario: Not Connected, but HAS prior messages (e.g. previous outreach).
        Expected: Route = INMAIL (based on gt: 0 rule).
        """
        buffer, registry = resources

        buffer.write_once(
            "mission_input", {"connection_status": "NOT_CONNECTED", "prior_message_count": 2}
        )

        agent_with_config.run_phase(buffer, registry)

        result = buffer.read("hop4_routing")
        assert result["route"] == "INMAIL"

    def test_fallback_logic(self, agent_with_config, resources):
        """
        Scenario: Context doesn't match ANY rule explicitly.
        Expected: Fallback to Default (INMAIL).
        """
        buffer, registry = resources

        # Weird state: Not connected, count is negative? Or specific status not in rules
        buffer.write_once(
            "mission_input", {"connection_status": "UNKNOWN_STATUS", "prior_message_count": 0}
        )

        agent_with_config.run_phase(buffer, registry)

        result = buffer.read("hop4_routing")
        # Agent implementation defaults to INMAIL
        assert result["route"] == "INMAIL"
        assert "Default Fallback" in result["reasoning"]

    def test_missing_input_failure(self, agent_with_config, resources):
        """
        Scenario: Buffer missing 'mission_input'.
        Expected: RuntimeError wrapping ValueError.
        """
        buffer, registry = resources
        # No write

        with pytest.raises(RuntimeError) as exc:
            agent_with_config.run_phase(buffer, registry)

        assert "execution failed" in str(exc.value)

        traces = registry.get_traces()
        assert any(t["type"] == "DATA_ERROR" for t in traces)
