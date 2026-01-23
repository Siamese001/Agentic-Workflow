"""
HOP-7 Governor Logic Test Suite.

Tests for Phase 17: V2.5 Governor with FACTUAL/CREATIVE Classification.
Requirement: 100% Pass Rate for Back-Hop Routing.
"""
import pytest
from apps_lic.engines.HOP7GateDecisionAgent import HOP7GateDecisionAgent
from apps_lic.shared.v2_patterns.immutable_buffer import ImmutableStagingBuffer
from apps_lic.shared.v2_patterns.trace_registry import TraceRegistry


class TestHOP7GovernorLogic:
    """
    Integration Tests for the V2.5 Governor.
    Requirement: 100% Pass Language.
    """

    def test_factual_failure_routing_s2(self):
        """Verify LIC-E015 (Strategic Alignment) triggers RETRY_HOP2."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()
        
        buffer.write_once("hop6_validation_report", {
            "passed": False,
            "validation_results": [
                {"rule_id": "LIC-E015", "passed": False, "severity": "CRITICAL"}
            ]
        })

        agent = HOP7GateDecisionAgent()
        agent.run_phase(buffer, registry)
        
        decision = buffer.read("hop7_gate_decision")
        assert decision["action"] == "RETRY_HOP2", "LIC-E015 should trigger RETRY_HOP2"
        assert decision["decision"] == "FAIL_FACTUAL"
        
        # Verify trace logging
        traces = [t["type"] for t in registry.get_traces()]
        assert "FACTUAL_LOOP_TRIGGERED" in traces

    def test_creative_failure_routing_s5(self):
        """Verify LIC-E001 (Placeholders) triggers RETRY_HOP5."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()
        
        buffer.write_once("hop6_validation_report", {
            "passed": False,
            "validation_results": [
                {"rule_id": "LIC-E001", "passed": False, "severity": "CRITICAL"}
            ]
        })

        agent = HOP7GateDecisionAgent()
        agent.run_phase(buffer, registry)
        
        decision = buffer.read("hop7_gate_decision")
        assert decision["action"] == "RETRY_HOP5", "LIC-E001 should trigger RETRY_HOP5"
        assert decision["decision"] == "FAIL_CREATIVE"
        
        # Verify trace logging
        traces = [t["type"] for t in registry.get_traces()]
        assert "CREATIVE_LOOP_TRIGGERED" in traces

    def test_clean_pass_proceed(self):
        """Verify passing validation triggers PROCEED."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()
        
        buffer.write_once("hop6_validation_report", {
            "passed": True,
            "validation_results": []
        })

        agent = HOP7GateDecisionAgent()
        agent.run_phase(buffer, registry)
        
        decision = buffer.read("hop7_gate_decision")
        assert decision["action"] == "PROCEED", "Clean validation should trigger PROCEED"
        assert decision["decision"] == "PASS"
        assert "quality gates satisfied" in decision["reason"].lower()

    def test_sovereign_error_handling(self):
        """Verify Governor raises error if validation report is missing."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()
        
        agent = HOP7GateDecisionAgent()
        
        with pytest.raises(RuntimeError):
            agent.run_phase(buffer, registry)
        
        # Verify error trace was logged (V2AgentBase logs PHASE_ERROR)
        traces = [t["type"] for t in registry.get_traces()]
        assert "PHASE_ERROR" in traces or "DATA_ERROR" in traces

    def test_factual_precedence_over_creative(self):
        """Verify FACTUAL failures take precedence over CREATIVE when both present."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()
        
        buffer.write_once("hop6_validation_report", {
            "passed": False,
            "validation_results": [
                {"rule_id": "LIC-E001", "passed": False, "severity": "CRITICAL"},  # Creative
                {"rule_id": "LIC-E015", "passed": False, "severity": "CRITICAL"}   # Factual
            ]
        })

        agent = HOP7GateDecisionAgent()
        agent.run_phase(buffer, registry)
        
        decision = buffer.read("hop7_gate_decision")
        # FACTUAL should take precedence
        assert decision["action"] == "RETRY_HOP2"
        assert decision["decision"] == "FAIL_FACTUAL"

    def test_forbidden_verbs_creative_routing(self):
        """Verify LIC-E008 (Forbidden Verbs) triggers RETRY_HOP5."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()
        
        buffer.write_once("hop6_validation_report", {
            "passed": False,
            "validation_results": [
                {"rule_id": "LIC-E008", "passed": False, "severity": "MEDIUM"}
            ]
        })

        agent = HOP7GateDecisionAgent()
        agent.run_phase(buffer, registry)
        
        decision = buffer.read("hop7_gate_decision")
        assert decision["action"] == "RETRY_HOP5"
        assert decision["decision"] == "FAIL_CREATIVE"

    def test_decision_reason_includes_rule_id(self):
        """Verify decision reason includes the failing rule ID."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()
        
        buffer.write_once("hop6_validation_report", {
            "passed": False,
            "validation_results": [
                {"rule_id": "LIC-E015", "passed": False, "severity": "CRITICAL"}
            ]
        })

        agent = HOP7GateDecisionAgent()
        agent.run_phase(buffer, registry)
        
        decision = buffer.read("hop7_gate_decision")
        assert "LIC-E015" in decision["reason"]

    def test_trace_logging_flow(self):
        """Verify complete trace logging flow."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()
        
        buffer.write_once("hop6_validation_report", {
            "passed": False,
            "validation_results": [
                {"rule_id": "LIC-E001", "passed": False, "severity": "CRITICAL"}
            ]
        })

        agent = HOP7GateDecisionAgent()
        agent.run_phase(buffer, registry)
        
        traces = [t["type"] for t in registry.get_traces()]
        
        assert "PHASE_START" in traces
        assert "PHASE_STEP" in traces
        assert "CREATIVE_LOOP_TRIGGERED" in traces
        assert "DECISION_FINAL" in traces

    def test_multiple_factual_failures(self):
        """Verify first factual failure is used for routing."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()
        
        buffer.write_once("hop6_validation_report", {
            "passed": False,
            "validation_results": [
                {"rule_id": "LIC-E015", "passed": False, "severity": "CRITICAL"},
                {"rule_id": "STRATEGIC_ALIGNMENT", "passed": False, "severity": "CRITICAL"}
            ]
        })

        agent = HOP7GateDecisionAgent()
        agent.run_phase(buffer, registry)
        
        decision = buffer.read("hop7_gate_decision")
        assert decision["action"] == "RETRY_HOP2"
        assert "LIC-E015" in decision["reason"]

    def test_decision_output_structure(self):
        """Verify decision output has correct structure."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()
        
        buffer.write_once("hop6_validation_report", {
            "passed": True,
            "validation_results": []
        })

        agent = HOP7GateDecisionAgent()
        agent.run_phase(buffer, registry)
        
        decision = buffer.read("hop7_gate_decision")
        
        # Verify required fields
        assert "decision" in decision
        assert "action" in decision
        assert "reason" in decision
        
        # Verify values
        assert decision["decision"] == "PASS"
        assert decision["action"] == "PROCEED"
        assert isinstance(decision["reason"], str)

    def test_config_driven_classification(self):
        """Verify classification is driven by config factual_failure_rules."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()
        
        # STRATEGIC_ALIGNMENT is in factual_failure_rules config
        buffer.write_once("hop6_validation_report", {
            "passed": False,
            "validation_results": [
                {"rule_id": "STRATEGIC_ALIGNMENT", "passed": False, "severity": "CRITICAL"}
            ]
        })

        agent = HOP7GateDecisionAgent()
        agent.run_phase(buffer, registry)
        
        decision = buffer.read("hop7_gate_decision")
        assert decision["action"] == "RETRY_HOP2"
        assert decision["decision"] == "FAIL_FACTUAL"
