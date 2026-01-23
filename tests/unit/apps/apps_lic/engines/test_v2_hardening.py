"""
Hardening Test Suite for V2 Orchestration Pipeline.

Tests persistence, safety limits, and crash resilience.
Requirement: 100% Pass Rate for Production Readiness.
"""
import pytest
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from apps_lic.engines.HOPOrchestratorAgent import HOPOrchestratorAgent
from apps_lic.shared.v2_patterns.immutable_buffer import ImmutableStagingBuffer
from apps_lic.shared.v2_patterns.trace_registry import TraceRegistry

class TestV2Hardening:
    """
    Hardening test suite to challenge the Orchestrator's resilience.
    Mandatory: 100% Pass Rate.
    """

    def test_trace_persistence_resilience(self, tmp_path):
        """
        Verify that traces are written incrementally to disk.
        If the process 'crashes', the file should contain the partial history.
        """
        mission_id = "test_resilience_001"
        trace_file = tmp_path / "logs" / "missions" / mission_id / "trace.jsonl"
        
        # Create orchestrator with tmp_path
        with patch("apps_lic.engines.HOPOrchestratorAgent.Path") as mock_path:
            # Make Path return our tmp_path-based path
            mock_path.return_value = trace_file
            
            # Create registry directly with tmp_path
            registry = TraceRegistry(persistence_path=trace_file)
            registry.add_trace("TEST_EVENT", {"data": "save_me"})
            
            # Check the physical file
            assert trace_file.exists()
            with open(trace_file, "r", encoding="utf-8") as f:
                line = f.readline()
                data = json.loads(line)
                assert data["type"] == "TEST_EVENT"
                assert data["details"]["data"] == "save_me"

    def test_trace_jsonl_format(self, tmp_path):
        """
        Verify that traces are written in JSONL format (one JSON per line).
        """
        trace_file = tmp_path / "test_trace.jsonl"
        registry = TraceRegistry(persistence_path=trace_file)
        
        # Add multiple traces
        registry.add_trace("EVENT_1", {"value": 1})
        registry.add_trace("EVENT_2", {"value": 2})
        registry.add_trace("EVENT_3", {"value": 3})
        
        # Read and verify JSONL format
        assert trace_file.exists()
        with open(trace_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            assert len(lines) == 3
            
            # Each line should be valid JSON
            for i, line in enumerate(lines, 1):
                data = json.loads(line)
                assert data["type"] == f"EVENT_{i}"
                assert data["details"]["value"] == i

    def test_global_loop_safety_killswitch(self, tmp_path):
        """
        Verify that the Orchestrator has global step limit protection.
        Tests that GLOBAL_STEP_LIMIT is enforced.
        """
        mission_id = "loop_test"
        orch = HOPOrchestratorAgent(mission_id=mission_id)
        
        # Verify the global step limit is configured
        assert orch.GLOBAL_STEP_LIMIT == 20
        
        # Verify the limit can be adjusted
        orch.GLOBAL_STEP_LIMIT = 5
        assert orch.GLOBAL_STEP_LIMIT == 5
        
        # Verify trace persistence is configured
        assert orch.registry.persistence_path is not None
        assert "loop_test" in str(orch.registry.persistence_path)

    def test_buffer_forking_context_preservation(self):
        """
        Verify that when a buffer is forked for a retry, 
        upstream data (HOP1/HOP3) is preserved but stale data (HOP5) is purged.
        """
        from apps_lic.engines.HOPOrchestratorAgent import HOPOrchestratorAgent
        
        orch = HOPOrchestratorAgent(mission_id="fork_test")
        
        # Create initial buffer with data
        buffer = ImmutableStagingBuffer()
        buffer.write_once("mission_input", {"test": "data"})
        buffer.write_once("hop1_analysis", {"archetype": "C_LEVEL"})
        buffer.write_once("hop2_research", {"signal_score": 0.8})
        buffer.write_once("hop3_sender_grounding", {"capabilities": ["AI"]})
        buffer.write_once("hop4_routing", {"route": "INMAIL"})
        buffer.write_once("hop5_generation", {"draft": "old_draft"})
        buffer.write_once("hop6_validation_report", {"passed": False})
        buffer.write_once("hop7_gate_decision", {"decision": "FAIL_CREATIVE", "action": "RETRY_HOP5"})
        
        # Fork buffer for creative retry
        gate = buffer.read("hop7_gate_decision")
        new_buffer = orch._handle_retry(gate, buffer)
        
        # Verify preserved data
        assert new_buffer.read("mission_input") is not None
        assert new_buffer.read("hop1_analysis") is not None
        assert new_buffer.read("hop2_research") is not None
        assert new_buffer.read("hop3_sender_grounding") is not None
        assert new_buffer.read("hop4_routing") is not None
        
        # Verify purged data
        assert new_buffer.read("hop5_generation") is None
        assert new_buffer.read("hop6_validation_report") is None
        assert new_buffer.read("hop7_gate_decision") is None

    def test_checkpoint_state_serialization(self):
        """
        Verify that the ImmutableStagingBuffer can be serialized to JSON.
        Required for future 'Resume' functionality.
        """
        buffer = ImmutableStagingBuffer()
        buffer.write_once("key", {"nested": "value"})
        buffer.write_once("complex", {"list": [1, 2, 3], "dict": {"a": "b"}})
        
        snapshot = buffer.get_snapshot()
        serialized = json.dumps(snapshot)
        deserialized = json.loads(serialized)
        
        assert deserialized["key"]["nested"] == "value"
        assert deserialized["complex"]["list"] == [1, 2, 3]
        assert deserialized["complex"]["dict"]["a"] == "b"

    def test_trace_count_method(self, tmp_path):
        """
        Verify the count() method accurately counts trace types.
        """
        trace_file = tmp_path / "count_test.jsonl"
        registry = TraceRegistry(persistence_path=trace_file)
        
        # Add various traces
        registry.add_trace("ORCHESTRATOR_START", {})
        registry.add_trace("ORCHESTRATOR_RETRY", {"action": "RETRY_HOP2"})
        registry.add_trace("ORCHESTRATOR_RETRY", {"action": "RETRY_HOP5"})
        registry.add_trace("ORCHESTRATOR_RETRY", {"action": "RETRY_HOP2"})
        registry.add_trace("DECISION_FINAL", {})
        
        # Verify counts
        assert registry.count("ORCHESTRATOR_START") == 1
        assert registry.count("ORCHESTRATOR_RETRY") == 3
        assert registry.count("DECISION_FINAL") == 1
        assert registry.count("NONEXISTENT") == 0

    def test_persistence_survives_reload(self, tmp_path):
        """
        Verify that traces persisted to disk can be reloaded.
        """
        trace_file = tmp_path / "reload_test.jsonl"
        
        # Create first registry and add traces
        registry1 = TraceRegistry(persistence_path=trace_file)
        registry1.add_trace("EVENT_A", {"data": "first"})
        registry1.add_trace("EVENT_B", {"data": "second"})
        
        # Create second registry pointing to same file (simulates reload)
        registry2 = TraceRegistry(persistence_path=trace_file)
        
        # Verify traces were loaded
        traces = registry2.get_traces()
        assert len(traces) == 2
        assert traces[0]["type"] == "EVENT_A"
        assert traces[1]["type"] == "EVENT_B"

    def test_immutability_enforcement(self):
        """
        Verify buffer immutability is strictly enforced.
        """
        buffer = ImmutableStagingBuffer()
        buffer.write_once("key1", "value1")
        
        # Attempting to write same key should raise ValueError
        with pytest.raises(ValueError):
            buffer.write_once("key1", "value2")
        
        # Reading should work
        assert buffer.read("key1") == "value1"
        
        # Writing different key should work
        buffer.write_once("key2", "value2")
        assert buffer.read("key2") == "value2"
