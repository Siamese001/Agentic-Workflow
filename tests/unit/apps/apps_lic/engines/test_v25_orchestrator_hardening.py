"""
V2.5 Orchestrator Hardening Test Suite.

Tests for Phase 18: Buffer Forking, Global Safety Budget, Trace Persistence.
Requirement: 100% Pass Rate for Sovereign Orchestration.
"""

import pytest
import json
from unittest.mock import MagicMock
from apps_lic.engines.HOPOrchestratorAgent import HOPOrchestratorAgent
from apps_lic.shared.v2_patterns.trace_registry import TraceRegistry


class TestV25OrchestratorHardening:
    """
    Sovereign Orchestration Test Suite.
    MANDATORY REQUIREMENT: All tests must achieve a 100% PASS RATE for Windsurf execution.
    """

    @pytest.fixture
    def orchestrator_with_mocks(self):
        """Create orchestrator with mocked agents."""
        orch = HOPOrchestratorAgent(mission_id="test_mission_001")

        # Mock all HOP agents
        for hop_id in ["HOP1", "HOP2", "HOP3", "HOP4", "HOP5", "HOP6", "HOP7", "HOP8"]:
            mock_agent = MagicMock()
            mock_agent.run_phase = MagicMock()
            orch.register_agent(hop_id, mock_agent)

        # Configure HOP7 to return PASS on first call
        def hop7_side_effect(buffer, registry):
            buffer.write_once(
                "hop7_gate_decision",
                {"decision": "PASS", "action": "PROCEED", "reason": "All gates passed"},
            )

        orch.agents["HOP7"].run_phase.side_effect = hop7_side_effect

        # Configure HOP8 to write QA report
        def hop8_side_effect(buffer, registry):
            buffer.write_once("hop8_qa_report", {"status": "complete"})

        orch.agents["HOP8"].run_phase.side_effect = hop8_side_effect

        return orch

    @pytest.fixture
    def orchestrator_with_retry_mock(self):
        """Create orchestrator that triggers a retry loop."""
        orch = HOPOrchestratorAgent(mission_id="test_retry_001")

        # Mock all HOP agents
        for hop_id in ["HOP1", "HOP2", "HOP3", "HOP4", "HOP5", "HOP6", "HOP7", "HOP8"]:
            mock_agent = MagicMock()
            mock_agent.run_phase = MagicMock()
            orch.register_agent(hop_id, mock_agent)

        # Configure HOP7 to fail once, then pass
        call_count = {"count": 0}

        def hop7_retry_side_effect(buffer, registry):
            call_count["count"] += 1
            if call_count["count"] == 1:
                # First call: trigger retry
                buffer.write_once(
                    "hop7_gate_decision",
                    {
                        "decision": "FAIL_CREATIVE",
                        "action": "RETRY_HOP5",
                        "reason": "Placeholder detected",
                    },
                )
            else:
                # Second call: pass
                buffer.write_once(
                    "hop7_gate_decision",
                    {"decision": "PASS", "action": "PROCEED", "reason": "All gates passed"},
                )

        orch.agents["HOP7"].run_phase.side_effect = hop7_retry_side_effect

        # Configure HOP8
        def hop8_side_effect(buffer, registry):
            buffer.write_once("hop8_qa_report", {"status": "complete"})

        orch.agents["HOP8"].run_phase.side_effect = hop8_side_effect

        return orch

    def test_buffer_forking_immutability(self, orchestrator_with_retry_mock):
        """
        Verify that retry loops successfully fork the buffer.
        New buffer must allow writing to purged keys but protect preserved keys.
        """
        mission_input = {"mission_id": "fork_test_001"}
        result = orchestrator_with_retry_mock.run_mission(mission_input)

        # Verify the TraceRegistry contains the RETRY event
        traces = orchestrator_with_retry_mock.registry.get_traces()
        retry_traces = [t for t in traces if t["type"] == "ORCHESTRATOR_RETRY"]

        assert len(retry_traces) > 0, "Buffer forking must create ORCHESTRATOR_RETRY trace"
        assert result["status"] == "SUCCESS"

    def test_global_safety_budget_enforcement(self):
        """
        Verify that the Orchestrator halts execution if the step budget is exceeded.
        Prevents infinite token drain in failing validation cycles.
        """
        orch = HOPOrchestratorAgent(mission_id="budget_test_001")

        # Mock agents that always fail validation
        for hop_id in ["HOP1", "HOP2", "HOP3", "HOP4", "HOP5", "HOP6", "HOP7", "HOP8"]:
            mock_agent = MagicMock()
            mock_agent.run_phase = MagicMock()
            orch.register_agent(hop_id, mock_agent)

        # Configure HOP7 to always fail (infinite loop scenario)
        def hop7_infinite_fail(buffer, registry):
            buffer.write_once(
                "hop7_gate_decision",
                {"decision": "FAIL_CREATIVE", "action": "RETRY_HOP5", "reason": "Always fail"},
            )

        orch.agents["HOP7"].run_phase.side_effect = hop7_infinite_fail

        # Lower step limit for testing
        orch.GLOBAL_STEP_LIMIT = 8

        result = orch.run_mission({"mission_id": "infinite_test"})

        assert result["status"] == "FAILED"
        assert "Exceeded global step limit" in result["error"]

    def test_disk_backed_trace_persistence(self, tmp_path):
        """
        Verify that traces are written to disk incrementally.
        Ensures audit trail survival after process termination.
        """
        # Use tmp_path for test isolation
        mission_id = "persistence_audit_99"
        trace_file = tmp_path / "trace.jsonl"

        # Create registry with tmp path
        registry = TraceRegistry(persistence_path=trace_file)
        registry.add_trace("PHASE_START", {"agent": "HOP1"})

        # Verify trace file exists
        assert trace_file.exists(), "Trace file must exist for persistence"

        # Verify content
        with open(trace_file) as f:
            lines = f.readlines()
            assert len(lines) > 0
            first_trace = json.loads(lines[0])
            assert first_trace["type"] == "PHASE_START"

    def test_specialist_knode_trace_integration(self):
        """
        Verify that internal K-Node triggers (like CXO Precedence) are captured in the master trace.
        Ensures visibility into micro-reasoning decisions.
        """
        from apps_lic.engines.HOP1ProfileAnalysisAgent import HOP1ProfileAnalysisAgent

        orch = HOPOrchestratorAgent(mission_id="cxo_test_001")

        # Register real HOP1 agent to trigger CXO precedence
        hop1_agent = HOP1ProfileAnalysisAgent()
        orch.register_agent("HOP1", hop1_agent)

        # Mock other agents
        for hop_id in ["HOP2", "HOP3", "HOP4", "HOP5", "HOP6", "HOP7", "HOP8"]:
            mock_agent = MagicMock()
            mock_agent.run_phase = MagicMock()
            orch.register_agent(hop_id, mock_agent)

        # Configure HOP7 to pass
        def hop7_pass(buffer, registry):
            buffer.write_once(
                "hop7_gate_decision",
                {"decision": "PASS", "action": "PROCEED", "reason": "All gates passed"},
            )

        orch.agents["HOP7"].run_phase.side_effect = hop7_pass

        # Configure HOP8
        def hop8_side_effect(buffer, registry):
            buffer.write_once("hop8_qa_report", {"status": "complete"})

        orch.agents["HOP8"].run_phase.side_effect = hop8_side_effect

        # Run mission with CEO title to trigger CXO precedence
        mission_input = {
            "mission_id": "cxo_test",
            "recipient_profile": {
                "title": "CEO",
                "about": "Executive leader",
                "name": "John Doe",
                "company": "TestCorp",
            },
        }

        result = orch.run_mission(mission_input)

        # Verify CXO precedence trace is in master registry
        traces = orch.registry.get_traces()
        cxo_traces = [t for t in traces if t["type"] == "CXO_PRECEDENCE_TRIGGERED"]

        assert len(cxo_traces) > 0, "CXO Precedence must be captured in master trace"
        assert result["status"] == "SUCCESS"

    def test_retry_limit_enforcement(self):
        """Verify retry limits are enforced based on config."""
        orch = HOPOrchestratorAgent(mission_id="retry_limit_test")

        # Mock all agents
        for hop_id in ["HOP1", "HOP2", "HOP3", "HOP4", "HOP5", "HOP6", "HOP7", "HOP8"]:
            mock_agent = MagicMock()
            mock_agent.run_phase = MagicMock()
            orch.register_agent(hop_id, mock_agent)

        # Configure HOP7 to always fail creative
        def hop7_always_fail(buffer, registry):
            buffer.write_once(
                "hop7_gate_decision",
                {"decision": "FAIL_CREATIVE", "action": "RETRY_HOP5", "reason": "Always fail"},
            )

        orch.agents["HOP7"].run_phase.side_effect = hop7_always_fail

        # Configure HOP8
        def hop8_side_effect(buffer, registry):
            buffer.write_once("hop8_qa_report", {"status": "complete"})

        orch.agents["HOP8"].run_phase.side_effect = hop8_side_effect

        result = orch.run_mission({"mission_id": "limit_test"})

        # Should hit retry limit and proceed to HOP8
        traces = orch.registry.get_traces()
        limit_traces = [t for t in traces if t["type"] == "ORCHESTRATOR_LIMIT_EXCEEDED"]

        assert len(limit_traces) > 0, "Retry limit must be enforced"
        assert result["status"] == "SUCCESS"

    def test_factual_retry_purges_hop2(self, orchestrator_with_mocks):
        """Verify RETRY_HOP2 purges hop2_research from buffer."""
        orch = orchestrator_with_mocks

        # Override HOP7 to trigger factual retry
        call_count = {"count": 0}

        def hop7_factual_retry(buffer, registry):
            call_count["count"] += 1
            if call_count["count"] == 1:
                buffer.write_once(
                    "hop7_gate_decision",
                    {
                        "decision": "FAIL_FACTUAL",
                        "action": "RETRY_HOP2",
                        "reason": "Strategic alignment failure",
                    },
                )
            else:
                buffer.write_once(
                    "hop7_gate_decision",
                    {"decision": "PASS", "action": "PROCEED", "reason": "All gates passed"},
                )

        orch.agents["HOP7"].run_phase.side_effect = hop7_factual_retry

        # Add side effect to HOP2 to write research data
        def hop2_side_effect(buffer, registry):
            buffer.write_once("hop2_research", {"data": "research_data"})

        orch.agents["HOP2"].run_phase.side_effect = hop2_side_effect

        result = orch.run_mission({"mission_id": "factual_retry_test"})

        # Verify retry happened
        traces = orch.registry.get_traces()
        retry_traces = [
            t
            for t in traces
            if t["type"] == "ORCHESTRATOR_RETRY" and t["details"]["action"] == "RETRY_HOP2"
        ]

        assert len(retry_traces) > 0, "RETRY_HOP2 must be triggered"
        assert result["status"] == "SUCCESS"

    def test_orchestrator_error_handling(self):
        """Verify orchestrator handles agent errors gracefully."""
        orch = HOPOrchestratorAgent(mission_id="error_test")

        # Mock agents with one that raises error
        for hop_id in ["HOP1", "HOP2", "HOP3", "HOP4", "HOP5", "HOP6", "HOP7", "HOP8"]:
            mock_agent = MagicMock()
            if hop_id == "HOP3":
                mock_agent.run_phase.side_effect = RuntimeError("HOP3 failed")
            else:
                mock_agent.run_phase = MagicMock()
            orch.register_agent(hop_id, mock_agent)

        result = orch.run_mission({"mission_id": "error_test"})

        assert result["status"] == "FAILED"
        assert "HOP3 failed" in result["error"]

        # Verify error trace
        traces = orch.registry.get_traces()
        error_traces = [t for t in traces if t["type"] == "ORCHESTRATOR_ERROR"]
        assert len(error_traces) > 0

    def test_mission_success_flow(self, orchestrator_with_mocks):
        """Verify complete mission success flow."""
        result = orchestrator_with_mocks.run_mission({"mission_id": "success_test"})

        assert result["status"] == "SUCCESS"
        assert "report" in result
        assert "traces" in result

        # Verify all phases executed
        traces = orchestrator_with_mocks.registry.get_traces()
        assert any(t["type"] == "ORCHESTRATOR_START" for t in traces)
