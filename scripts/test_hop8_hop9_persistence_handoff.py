"""
MANDATORY Test Suite: HOP 8-9 Persistence & Handoff
100% Pass Requirement for Windsurf Execution.

Focus Areas:
- HOP-8: Report Persistence & Quality Scoring
- HOP-8: Defensive State Aggregation
- HOP-9: Checksum Integrity Verification
- HOP-9: Priority Escalation for C_LEVEL
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
import hashlib
from unittest.mock import MagicMock, patch
from apps_lic.engines.HOP8QAReportAgent import HOP8QAReportAgent
from apps_lic.engines.HOP9IntegrationAgent import HOP9IntegrationAgent
from apps_lic.shared.core.immutable_buffer import ImmutableStagingBuffer
from apps_lic.shared.core.trace_registry import TraceRegistry


class TestFinalityAndIntegration:
    """
    MANDATORY: 100% PASS REQUIREMENT.
    Focus: Persistence Verification, Checksum Integrity, Priority Escalation.
    """

    def test_hop8_report_persistence_and_scoring(self):
        """Verify HOP-8: Report is generated and quality scores are calculated correctly."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        # Seed minimum state for scoring
        buffer.write_once("hop2_research", {"signal_score": 0.8})
        buffer.write_once("hop6_validation_report", {"passed": True, "validation_results": []})
        buffer.write_once("hop5_generation", {"selected_draft": {"score": 9.0, "text": "Draft"}})
        
        agent = HOP8QAReportAgent()
        agent.run_phase(buffer, registry)
        
        report_data = buffer.read("hop8_qa_report")
        # Verify 100% Pass: Score must be calculated and path returned
        assert report_data["total_score"] > 0, "Total score should be positive"
        assert "report_path" in report_data, "Report path should be present"

    def test_hop8_defensive_state_reads(self):
        """Verify HOP-8: Handles missing HOP outputs gracefully with empty dict fallbacks."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        # Only provide minimal state
        buffer.write_once("hop5_generation", {"selected_draft": {"score": 5.0, "text": "Minimal"}})
        
        agent = HOP8QAReportAgent()
        # Should not crash even with missing HOPs
        agent.run_phase(buffer, registry)
        
        report_data = buffer.read("hop8_qa_report")
        # Verify: Report generated despite missing state
        assert report_data is not None, "Report should be generated"
        assert "total_score" in report_data, "Should calculate score"

    def test_hop8_score_breakdown_dimensions(self):
        """Verify HOP-8: Score breakdown includes all 4 dimensions."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("hop2_research", {"signal_score": 0.9})
        buffer.write_once("hop6_validation_report", {
            "passed": True,
            "validation_results": [
                {"passed": True},
                {"passed": True}
            ]
        })
        buffer.write_once("hop5_generation", {"selected_draft": {"score": 8.0, "text": "Test"}})
        
        agent = HOP8QAReportAgent()
        agent.run_phase(buffer, registry)
        
        report_data = buffer.read("hop8_qa_report")
        scores = report_data["score_breakdown"]
        
        # Verify: All 4 dimensions present
        assert "research" in scores, "Should have research score"
        assert "alignment" in scores, "Should have alignment score"
        assert "validation" in scores, "Should have validation score"
        assert "generation" in scores, "Should have generation score"

    def test_hop9_checksum_mismatch_halt(self):
        """Verify HOP-9: ValueError is raised if the draft checksum has changed since HOP-5."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("mission_input", {"recipient_id": "123"})
        buffer.write_once("hop4_routing", {"route": "INMAIL"})
        buffer.write_once("hop8_qa_report", {"report_path": "audit.md"})
        # Generation draft with a mismatched manual checksum
        buffer.write_once("hop5_generation", {
            "selected_draft": {"text": "Original Text", "checksum": "incorrect_hash"}
        })
        
        agent = HOP9IntegrationAgent()
        # Verify 100% Pass: Terminal halt on integrity violation (LICAgentBase wraps as RuntimeError)
        with pytest.raises(RuntimeError, match="HOP9IntegrationAgent execution failed"):
            agent.run_phase(buffer, registry)
        
        # Verify trace shows integrity failure
        traces = registry.get_traces()
        assert any(t.get("type") == "INTEGRITY_FAILURE" for t in traces), "Should log integrity failure"

    def test_hop9_checksum_match_pass(self):
        """Verify HOP-9: Passes when checksum matches."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        text = "Strategic Message"
        checksum = hashlib.sha256(text.encode()).hexdigest()
        
        buffer.write_once("mission_input", {"recipient_id": "123"})
        buffer.write_once("hop4_routing", {"route": "INMAIL"})
        buffer.write_once("hop8_qa_report", {"report_path": "audit.md"})
        buffer.write_once("hop5_generation", {
            "selected_draft": {"text": text, "checksum": checksum},
            "meta": {"archetype": "MANAGER"}
        })
        
        agent = HOP9IntegrationAgent()
        agent.run_phase(buffer, registry)
        
        result = buffer.read("hop9_integration")
        # Verify: Should pass
        assert result["status"] == "READY_FOR_DELIVERY", "Should be ready for delivery"

    def test_hop9_missing_checksum_warning(self):
        """Verify HOP-9: Logs warning if checksum is missing from HOP-5."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("mission_input", {"recipient_id": "123"})
        buffer.write_once("hop4_routing", {"route": "INMAIL"})
        buffer.write_once("hop8_qa_report", {"report_path": "audit.md"})
        buffer.write_once("hop5_generation", {
            "selected_draft": {"text": "No checksum"}  # Missing checksum
        })
        
        agent = HOP9IntegrationAgent()
        agent.run_phase(buffer, registry)
        
        # Verify: Warning trace logged
        traces = registry.get_traces()
        assert any(t.get("type") == "INTEGRITY_WARNING" for t in traces), "Should log integrity warning"

    def test_hop9_priority_escalation_for_cxo(self):
        """Verify HOP-9: Archetype priority is correctly set to HIGH for C_LEVEL targets."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        text = "Strategic Message"
        checksum = hashlib.sha256(text.encode()).hexdigest()
        
        buffer.write_once("mission_input", {"recipient_id": "ceo_99"})
        buffer.write_once("hop4_routing", {"route": "INMAIL"})
        buffer.write_once("hop8_qa_report", {"report_path": "audit.md"})
        buffer.write_once("hop1_analysis", {"Archetype": "C_LEVEL"})
        buffer.write_once("hop5_generation", {
            "selected_draft": {"text": text, "checksum": checksum},
            "meta": {"archetype": "C_LEVEL"}
        })
        
        agent = HOP9IntegrationAgent()
        agent.run_phase(buffer, registry)
        
        payload = buffer.read("hop9_integration")["payload"]
        # Verify 100% Pass: Priority must be HIGH for C_LEVEL
        assert payload["priority"] == "HIGH", "C_LEVEL should have HIGH priority"

    def test_hop9_priority_normal_for_non_cxo(self):
        """Verify HOP-9: Non-C_LEVEL targets get NORMAL priority."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        text = "Message"
        checksum = hashlib.sha256(text.encode()).hexdigest()
        
        buffer.write_once("mission_input", {"recipient_id": "mgr_01"})
        buffer.write_once("hop4_routing", {"route": "CONNECTION_REQ"})
        buffer.write_once("hop8_qa_report", {"report_path": "audit.md"})
        buffer.write_once("hop5_generation", {
            "selected_draft": {"text": text, "checksum": checksum},
            "meta": {"archetype": "MANAGER"}
        })
        
        agent = HOP9IntegrationAgent()
        agent.run_phase(buffer, registry)
        
        payload = buffer.read("hop9_integration")["payload"]
        # Verify: NORMAL priority for non-C_LEVEL
        assert payload["priority"] == "NORMAL", "MANAGER should have NORMAL priority"

    def test_hop9_payload_structure(self):
        """Verify HOP-9: Delivery payload has all required fields."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        text = "Test Message"
        checksum = hashlib.sha256(text.encode()).hexdigest()
        
        buffer.write_once("mission_input", {"recipient_id": "test_123"})
        buffer.write_once("hop4_routing", {"route": "FOLLOW_UP"})
        buffer.write_once("hop8_qa_report", {"report_path": "/path/to/audit.md"})
        buffer.write_once("hop5_generation", {
            "selected_draft": {"text": text, "checksum": checksum},
            "meta": {"archetype": "EXECUTIVE"}
        })
        
        agent = HOP9IntegrationAgent()
        agent.run_phase(buffer, registry)
        
        result = buffer.read("hop9_integration")
        payload = result["payload"]
        
        # Verify: All required fields
        assert "message" in payload, "Should have message"
        assert "delivery_route" in payload, "Should have delivery_route"
        assert "recipient_id" in payload, "Should have recipient_id"
        assert "audit_report_path" in payload, "Should have audit_report_path"
        assert "priority" in payload, "Should have priority"
        assert payload["delivery_route"] == "FOLLOW_UP", "Route should match"
        assert payload["recipient_id"] == "test_123", "Recipient ID should match"

    def test_hop9_missing_artifacts_halt(self):
        """Verify HOP-9: Raises RuntimeError if required HOPs missing."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        # Don't write required inputs
        
        agent = HOP9IntegrationAgent()
        
        # Verify: Should halt (LICAgentBase wraps with agent name)
        with pytest.raises(RuntimeError, match="HOP9IntegrationAgent execution failed"):
            agent.run_phase(buffer, registry)

    def test_hop8_markdown_generation(self):
        """Verify HOP-8: Markdown report contains key sections."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("hop1_analysis", {"recipient_name": "John Doe", "Archetype": "EXECUTIVE"})
        buffer.write_once("hop2_research", {"signal_score": 0.85})
        buffer.write_once("hop4_routing", {"route": "INMAIL"})
        buffer.write_once("hop5_generation", {"selected_draft": {"text": "Test draft", "score": 7.5}})
        buffer.write_once("hop6_validation_report", {"passed": True, "validation_results": []})
        
        agent = HOP8QAReportAgent()
        
        # Access internal method for testing
        states = {
            "hop1": buffer.read("hop1_analysis"),
            "hop2": buffer.read("hop2_research"),
            "hop4": buffer.read("hop4_routing"),
            "hop5": buffer.read("hop5_generation"),
            "hop6": buffer.read("hop6_validation_report")
        }
        scores = agent._calculate_scores(states)
        total = sum(scores.values())
        
        markdown = agent._generate_markdown(states, scores, total)
        
        # Verify: Key sections present
        assert "Mission Audit Report" in markdown, "Should have title"
        assert "John Doe" in markdown, "Should include recipient name"
        assert "Quality Score" in markdown, "Should have quality score section"
        assert "Score Breakdown" in markdown, "Should have breakdown"
        assert "Generated Draft" in markdown, "Should include draft"

    def test_hop9_archetype_fallback_to_hop1(self):
        """Verify HOP-9: Falls back to HOP-1 for archetype if not in HOP-5 meta."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        text = "Message"
        checksum = hashlib.sha256(text.encode()).hexdigest()
        
        buffer.write_once("mission_input", {"recipient_id": "test"})
        buffer.write_once("hop4_routing", {"route": "INMAIL"})
        buffer.write_once("hop8_qa_report", {"report_path": "audit.md"})
        buffer.write_once("hop1_analysis", {"Archetype": "C_LEVEL"})
        buffer.write_once("hop5_generation", {
            "selected_draft": {"text": text, "checksum": checksum},
            "meta": {"archetype": "UNKNOWN"}  # Unknown in meta
        })
        
        agent = HOP9IntegrationAgent()
        agent.run_phase(buffer, registry)
        
        payload = buffer.read("hop9_integration")["payload"]
        # Verify: Should use HOP-1 archetype
        assert payload["priority"] == "HIGH", "Should use C_LEVEL from HOP-1"

    def test_hop9_mission_completed_trace(self):
        """Verify HOP-9: Logs MISSION_COMPLETED trace on success."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        text = "Final Message"
        checksum = hashlib.sha256(text.encode()).hexdigest()
        
        buffer.write_once("mission_input", {"recipient_id": "final"})
        buffer.write_once("hop4_routing", {"route": "CONNECTION_REQ"})
        buffer.write_once("hop8_qa_report", {"report_path": "audit.md"})
        buffer.write_once("hop5_generation", {
            "selected_draft": {"text": text, "checksum": checksum},
            "meta": {"archetype": "MANAGER"}
        })
        
        agent = HOP9IntegrationAgent()
        agent.run_phase(buffer, registry)
        
        # Verify: MISSION_COMPLETED trace
        traces = registry.get_traces()
        assert any(t.get("type") == "MISSION_COMPLETED" for t in traces), "Should log mission completed"


def run_tests():
    """Execute test suite with detailed reporting."""
    print("=" * 80)
    print("HOP 8-9 PERSISTENCE & HANDOFF TEST SUITE")
    print("=" * 80)
    print()

    # Run pytest with verbose output
    exit_code = pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "--color=yes",
            "-W",
            "ignore::DeprecationWarning",
        ]
    )

    print()
    print("=" * 80)
    if exit_code == 0:
        print("✅ ALL TESTS PASSED - 100% Pass Requirement Met")
        print("HOP 8-9 Persistence & Handoff is ready for deployment")
    else:
        print("❌ TEST FAILURES DETECTED")
        print("DO NOT DEPLOY until all tests pass")
    print("=" * 80)

    return exit_code


if __name__ == "__main__":
    sys.exit(run_tests())
