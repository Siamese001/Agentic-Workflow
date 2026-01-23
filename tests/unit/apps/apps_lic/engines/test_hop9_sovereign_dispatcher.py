"""
HOP-9 Sovereign Dispatcher Test Suite.

MANDATORY REQUIREMENT: All tests must achieve a 100% PASS RATE for Windsurf execution.
"""
import pytest
import hashlib
from apps_lic.engines.HOP9IntegrationAgent import HOP9IntegrationAgent
from apps_lic.shared.v2_patterns.immutable_buffer import ImmutableStagingBuffer
from apps_lic.shared.v2_patterns.trace_registry import TraceRegistry


class TestHOP9SovereignDispatcher:
    """
    Sovereign Integration Test Suite for HOP-9.
    MANDATORY REQUIREMENT: All tests must achieve a 100% PASS RATE for Windsurf execution.
    """

    def test_checksum_integrity_protection(self):
        """
        Verify that HOP-9 blocks handoff if the message checksum has changed.
        Ensures 100% security against unauthorized state mutation.
        MANDATORY: 100% PASS REQUIREMENT.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("mission_input", {"recipient_id": "user_123"})
        buffer.write_once("hop4_routing", {"route": "INMAIL"})
        buffer.write_once("hop5_generation", {
            "selected_draft": {"text": "Original Text", "checksum": "incorrect_hash"},
            "meta": {"archetype": "EXECUTIVE"}
        })
        buffer.write_once("hop8_qa_report", {"report_path": "/logs/test.md"})
        
        agent = HOP9IntegrationAgent()
        # V2AgentBase wraps exceptions in RuntimeError
        with pytest.raises(RuntimeError):
            agent.run_phase(buffer, registry)
        
        assert registry.count("INTEGRITY_FAILURE") == 1

    def test_delivery_payload_formatting(self):
        """
        Verify that the final payload includes the message, route, and audit link.
        MANDATORY: 100% PASS REQUIREMENT.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("mission_input", {"recipient_id": "user_456"})
        buffer.write_once("hop4_routing", {"route": "CONNECTION_REQ"})
        buffer.write_once("hop5_generation", {
            "selected_draft": {"text": "Final Draft text..."},
            "meta": {"archetype": "SENIOR_TA"}
        })
        buffer.write_once("hop8_qa_report", {"report_path": "/logs/final.md"})

        agent = HOP9IntegrationAgent()
        agent.run_phase(buffer, registry)
        
        result = buffer.read("hop9_integration")
        payload = result["payload"]
        assert payload["delivery_route"] == "CONNECTION_REQ"
        assert payload["audit_report_path"] == "/logs/final.md"
        assert result["status"] == "READY_FOR_DELIVERY"

    def test_priority_escalation_for_cxo(self):
        """
        Verify that C-Level missions are marked with HIGH priority in the delivery payload.
        Ensures high-value missions are prioritized in the execution queue.
        MANDATORY: 100% PASS REQUIREMENT.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("mission_input", {"recipient_id": "vip_789"})
        buffer.write_once("hop4_routing", {"route": "INMAIL"})
        buffer.write_once("hop5_generation", {
            "selected_draft": {"text": "Strategic Outreach..."},
            "meta": {"archetype": "C_LEVEL"}
        })
        buffer.write_once("hop8_qa_report", {"report_path": "/logs/vip.md"})

        agent = HOP9IntegrationAgent()
        agent.run_phase(buffer, registry)
        
        payload = buffer.read("hop9_integration")["payload"]
        assert payload["priority"] == "HIGH"

    def test_mission_completion_trace(self):
        """
        Verify that MISSION_COMPLETED trace is recorded for a successful run.
        MANDATORY: 100% PASS REQUIREMENT.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("mission_input", {"recipient_id": "test_user"})
        buffer.write_once("hop4_routing", {"route": "FOLLOW_UP"})
        buffer.write_once("hop5_generation", {
            "selected_draft": {"text": "Test message content"},
            "meta": {"archetype": "MANAGER"}
        })
        buffer.write_once("hop8_qa_report", {"report_path": "/logs/test.md"})

        agent = HOP9IntegrationAgent()
        agent.run_phase(buffer, registry)
        
        traces = [t["type"] for t in registry.get_traces()]
        assert "MISSION_COMPLETED" in traces
        
        # Find the MISSION_COMPLETED trace and verify its content
        mission_traces = [t for t in registry.get_traces() if t["type"] == "MISSION_COMPLETED"]
        assert len(mission_traces) == 1
        assert mission_traces[0]["details"]["status"] == "SUCCESS"

    def test_checksum_generated_on_output(self):
        """
        Verify that HOP-9 generates and stores checksum in output.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        test_text = "Test message for checksum"
        expected_checksum = hashlib.sha256(test_text.encode()).hexdigest()
        
        buffer.write_once("mission_input", {"recipient_id": "checksum_test"})
        buffer.write_once("hop4_routing", {"route": "INMAIL"})
        buffer.write_once("hop5_generation", {
            "selected_draft": {"text": test_text},
            "meta": {"archetype": "EXECUTIVE"}
        })
        buffer.write_once("hop8_qa_report", {"report_path": "/logs/checksum.md"})

        agent = HOP9IntegrationAgent()
        agent.run_phase(buffer, registry)
        
        result = buffer.read("hop9_integration")
        assert result["checksum"] == expected_checksum

    def test_missing_artifacts_error(self):
        """
        Verify that HOP-9 raises error when required artifacts are missing.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("mission_input", {"recipient_id": "incomplete"})
        # Missing hop4_routing and hop5_generation
        
        agent = HOP9IntegrationAgent()
        # V2AgentBase wraps exceptions in RuntimeError with agent name
        with pytest.raises(RuntimeError):
            agent.run_phase(buffer, registry)
        
        # Verify DATA_ERROR trace was logged
        traces = [t["type"] for t in registry.get_traces()]
        assert "DATA_ERROR" in traces

    def test_normal_priority_for_non_cxo(self):
        """
        Verify that non-C-Level missions get NORMAL priority.
        """
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("mission_input", {"recipient_id": "regular_user"})
        buffer.write_once("hop4_routing", {"route": "CONNECTION_REQ"})
        buffer.write_once("hop5_generation", {
            "selected_draft": {"text": "Regular outreach message"},
            "meta": {"archetype": "RECRUITER"}
        })
        buffer.write_once("hop8_qa_report", {"report_path": "/logs/regular.md"})

        agent = HOP9IntegrationAgent()
        agent.run_phase(buffer, registry)
        
        payload = buffer.read("hop9_integration")["payload"]
        assert payload["priority"] == "NORMAL"
