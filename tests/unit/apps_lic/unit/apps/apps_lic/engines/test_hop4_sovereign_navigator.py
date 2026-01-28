"""
HOP-4 Sovereign Navigator Test Suite.

MANDATORY REQUIREMENT: All tests must achieve a 100% PASS RATE for Windsurf execution.
"""

import pytest
from apps_lic.engines.HOP4RoutingAgent import HOP4RoutingAgent
from apps_lic.shared.core.immutable_buffer import ImmutableStagingBuffer
from apps_lic.shared.core.trace_registry import TraceRegistry


class TestHOP4SovereignNavigator:
    """
    Sovereign Foundation Test Suite for HOP-4.
    MANDATORY REQUIREMENT: All tests must achieve a 100% PASS RATE for Windsurf execution.
    """

    def test_gate_6_premium_mismatch_blocking(self):
        """
        Verify Gate 6: System must raise ValueError if INMAIL is requested without premium credits.
        Prevents downstream generation for an unexecutable route.
        MANDATORY: 100% PASS REQUIREMENT.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("hop1_analysis", {"Archetype": "C_LEVEL"})
        buffer.write_once(
            "mission_input",
            {
                "route_override": "INMAIL",
                "premium_available": False,  # The Conflict
            },
        )

        agent = HOP4RoutingAgent()
        # LICAgentBase wraps exceptions in RuntimeError
        with pytest.raises(RuntimeError):
            agent.run_phase(buffer, registry)

        assert registry.count("GATE_6_FAILED") == 1

    def test_deterministic_route_selection_inmail(self):
        """
        Verify Gate 5: Default selection for NOT_CONNECTED + Premium must be INMAIL.
        MANDATORY: 100% PASS REQUIREMENT.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("hop1_analysis", {"Archetype": "EXECUTIVE"})
        buffer.write_once(
            "mission_input", {"connection_status": "NOT_CONNECTED", "premium_available": True}
        )

        agent = HOP4RoutingAgent()
        agent.run_phase(buffer, registry)

        result = buffer.read("hop4_routing")
        assert result["route"] == "INMAIL"

    def test_constraint_injection_integrity(self):
        """
        Verify that routing constraints (char_limit) are correctly injected for HOP-5.
        MANDATORY: 100% PASS REQUIREMENT.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("hop1_analysis", {"Archetype": "RECRUITER"})
        buffer.write_once(
            "mission_input",
            {
                "connection_status": "CONNECTED"  # Should trigger FOLLOW_UP
            },
        )

        agent = HOP4RoutingAgent()
        agent.run_phase(buffer, registry)

        result = buffer.read("hop4_routing")
        # FOLLOW_UP maps to DIRECT_MESSAGE which has char_limit 2000
        assert result["constraints"]["char_limit"] == 2000

    def test_sovereign_trace_registry_audit(self):
        """
        Verify that route selection decisions are recorded in the audit trail.
        MANDATORY: 100% PASS REQUIREMENT.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("hop1_analysis", {"Archetype": "SENIOR_TA"})
        buffer.write_once("mission_input", {"connection_status": "NOT_CONNECTED"})

        agent = HOP4RoutingAgent()
        agent.run_phase(buffer, registry)

        traces = [t["type"] for t in registry.get_traces()]
        assert "DECISION_FINAL" in traces

    def test_route_override_applied(self):
        """
        Verify that route_override takes precedence over connection status.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("hop1_analysis", {"Archetype": "EXECUTIVE"})
        buffer.write_once(
            "mission_input",
            {
                "connection_status": "CONNECTED",
                "route_override": "INMAIL",
                "premium_available": True,
            },
        )

        agent = HOP4RoutingAgent()
        agent.run_phase(buffer, registry)

        result = buffer.read("hop4_routing")
        assert result["route"] == "INMAIL"

        traces = [t["type"] for t in registry.get_traces()]
        assert "ROUTE_OVERRIDE_APPLIED" in traces

    def test_connected_status_selects_follow_up(self):
        """
        Verify that CONNECTED status selects FOLLOW_UP route.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("hop1_analysis", {"Archetype": "MANAGER"})
        buffer.write_once("mission_input", {"connection_status": "CONNECTED"})

        agent = HOP4RoutingAgent()
        agent.run_phase(buffer, registry)

        result = buffer.read("hop4_routing")
        assert result["route"] == "FOLLOW_UP"

    def test_not_connected_no_premium_selects_connection_req(self):
        """
        Verify that NOT_CONNECTED without premium selects CONNECTION_REQ.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("hop1_analysis", {"Archetype": "RECRUITER"})
        buffer.write_once(
            "mission_input", {"connection_status": "NOT_CONNECTED", "premium_available": False}
        )

        agent = HOP4RoutingAgent()
        agent.run_phase(buffer, registry)

        result = buffer.read("hop4_routing")
        assert result["route"] == "CONNECTION_REQ"

    def test_metadata_includes_archetype(self):
        """
        Verify that metadata includes archetype alignment.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("hop1_analysis", {"Archetype": "C_LEVEL"})
        buffer.write_once("mission_input", {"connection_status": "CONNECTED"})

        agent = HOP4RoutingAgent()
        agent.run_phase(buffer, registry)

        result = buffer.read("hop4_routing")
        assert "metadata" in result
        assert result["metadata"]["archetype_aligned"] == "C_LEVEL"
        assert result["metadata"]["premium_validated"] is True
