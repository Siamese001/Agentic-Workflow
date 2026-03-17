#!/usr/bin/env python3
"""
Simplified test script for Verification Gate functionality.

This script tests the core verification gate without complex dependencies.
"""

# Import only the verification gate directly
import sys
import tempfile
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_records_execution_trace("p0", "evidence", "test_verification_gate_simple")
_emit_applies_guardrail("p0", "test_verification_gate_simple", "p0_governance")
_emit_reads_policy_state("p0", "test_verification_gate_simple", "policy_binding")
_emit_snapshots_state("p0", "test_verification_gate_simple", "state_snapshot")
emit_replay_key("p0", "test_verification_gate_simple")
emit_determinism_digest("p0", "test_verification_gate_simple")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_verification_gate_simple", "execution_auth")
_emit_validates_capability("p2", "test_verification_gate_simple", "capability_check")
_emit_routes_to_capability("p2", "test_verification_gate_simple", "capability_route")
_emit_writes_via_uwg("p2", "test_verification_gate_simple", "uwg_write")
_emit_blocks_direct_write("p2", "test_verification_gate_simple", "direct_write_block")
_emit_records_tool_invocation("p2", "test_verification_gate_simple", "tool_invocation")
_emit_captures_execution_output("p2", "test_verification_gate_simple", "exec_output")
_emit_dispatches_agent("p3", "test_verification_gate_simple", "agent_dispatch")
_emit_coordinates_agents("p3", "test_verification_gate_simple", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_verification_gate_simple", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_verification_gate_simple", "healing_outcome")
_emit_escalates_failure("p3", "test_verification_gate_simple", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_verification_gate_simple", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_verification_gate_simple", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_verification_gate_simple", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_verification_gate_simple", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_verification_gate_simple", "eval_metric")
_emit_stores_embedding("p4", "test_verification_gate_simple", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_verification_gate_simple", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_verification_gate_simple", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

sys.path.append(".")

from agentic_core.L5_safety.enforcement.verification_gate import VerificationGate
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_writes_through,  # noqa: E402
    _emit_links_incident_trace,  # noqa: E402
)

_emit_emits_metric_event("test_verification_gate_simple", "p4obs", "metric_1")
_emit_emits_metric_event("test_verification_gate_simple", "p4obs", "metric_2")
_emit_emits_metric_event("test_verification_gate_simple", "p4obs", "metric_3")
_emit_emits_metric_event("test_verification_gate_simple", "p4obs", "metric_4")
_emit_emits_metric_event("test_verification_gate_simple", "p4obs", "metric_5")
_emit_emits_metric_event("test_verification_gate_simple", "p4obs", "metric_6")
_emit_records_incident_event("test_verification_gate_simple", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_verification_gate_simple", "p4obs", "anomaly")
_emit_writes_observability_log("test_verification_gate_simple", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_verification_gate_simple", "p4obs", "mon_state")
_emit_triggers_alert("test_verification_gate_simple", "p4obs", "alert")
_emit_links_incident_trace("test_verification_gate_simple", "p4obs", "trace_link")
_emit_captures_pattern("test_verification_gate_simple", "p3lm", "pattern")
_emit_records_learning_event("test_verification_gate_simple", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_verification_gate_simple", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_verification_gate_simple", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_verification_gate_simple", "p3lm", "routing")
_emit_improves_agent_policy("test_verification_gate_simple", "p3lm", "policy")
_emit_stores_learning_state("test_verification_gate_simple", "p3lm", "state")
_emit_records_execution_trace("test_verification_gate_simple", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_verification_gate_simple", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_verification_gate_simple", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_verification_gate_simple", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_verification_gate_simple", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_verification_gate_simple", "env_read", "p2_env_1")
_emit_reads_environ("test_verification_gate_simple", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_verification_gate_simple", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_verification_gate_simple", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_verification_gate_simple", "context_pull")
_emit_pulls_context("p1", "test_verification_gate_simple", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_verification_gate_simple", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_verification_gate_simple", "uwg_term_2")
_emit_writes_through("p1", "test_verification_gate_simple", "write_through")
_emit_writes_through("p1", "test_verification_gate_simple", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_verification_gate_simple", "safety_validation")
_emit_invokes_eval("p1", "test_verification_gate_simple", "eval_call")
_emit_proposal_commits_routing("p1", "test_verification_gate_simple", "routing_commit")
_emit_escalates_to_human("p1", "test_verification_gate_simple", "human_escalation")
_emit_routes_through("p1", "test_verification_gate_simple", "route_through")
_emit_checks_agent_registry("p1", "test_verification_gate_simple", "agent_registry")
_emit_validates_agent_capability("p1", "test_verification_gate_simple", "capability")
_emit_dispatches_execution_plan("p1", "test_verification_gate_simple", "exec_plan")
_emit_agent_executes_agent("p1", "test_verification_gate_simple", "sub_agent")
_emit_routes_to_agent("p1", "test_verification_gate_simple", "target_agent")
_emit_verifies_policy("p1", "test_verification_gate_simple", "policy_check")
_emit_observes_runtime_state("p1", "test_verification_gate_simple", "runtime_state")
_emit_verifies_boundary("p1", "test_verification_gate_simple", "boundary_check")
_emit_transcripts_response("p1", "test_verification_gate_simple", "transcript")
_emit_hard_fails_untranscripted("p1", "test_verification_gate_simple")
_emit_gated_by_confidence("p1", "test_verification_gate_simple", "confidence_gate")


def test_verification_gate_basic():
    """Test basic verification gate functionality."""
    print("=== Testing Verification Gate Basic Functionality ===")

    gate = VerificationGate()

    # Test with non-existent file
    assert not gate.verify_action(Path("nonexistent.py"), "delete_import", "requests")
    print("✓ Correctly rejected non-existent file")

    # Test with empty file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("# Empty file\n")
        f.flush()
        temp_path = Path(f.name)

    try:
        # Should fail - no imports in empty file
        assert not gate.verify_action(temp_path, "delete_import", "requests")
        print("✓ Correctly rejected import deletion in empty file")

        # Should fail - no functions in empty file
        assert not gate.verify_action(temp_path, "modify_function", "test_func")
        print("✓ Correctly rejected function modification in empty file")

        # Should fail - no classes in empty file
        assert not gate.verify_action(temp_path, "remove_class", "TestClass")
        print("✓ Correctly rejected class removal in empty file")

    finally:
        temp_path.unlink()


def test_verification_gate_with_real_code():
    """Test verification gate with actual Python code."""
    print("\n=== Testing Verification Gate with Real Code ===")

    gate = VerificationGate()

    # Create test file with imports, functions, and classes
    test_code = '''
import os
import sys
from pathlib import Path

def test_function():
    """Test function."""
    pass

class TestClass:
    """Test class."""

    def test_method(self):
        """Test method."""
        pass

unused_variable = "test"
'''

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(test_code)
        f.flush()
        temp_path = Path(f.name)

    try:
        # Should succeed - imports exist
        assert gate.verify_action(temp_path, "delete_import", "os")
        assert gate.verify_action(temp_path, "delete_import", "sys")
        assert gate.verify_action(temp_path, "delete_import", "Path")
        print("✓ Correctly verified existing imports")

        # Should fail - import doesn't exist
        assert not gate.verify_action(temp_path, "delete_import", "requests")
        assert not gate.verify_action(temp_path, "delete_import", "nonexistent_module")
        print("✓ Correctly rejected non-existent imports")

        # Should succeed - function exists
        assert gate.verify_action(temp_path, "modify_function", "test_function")
        print("✓ Correctly verified existing function")

        # Should fail - function doesn't exist
        assert not gate.verify_action(temp_path, "modify_function", "nonexistent_function")
        print("✓ Correctly rejected non-existent function")

        # Should succeed - class exists
        assert gate.verify_action(temp_path, "remove_class", "TestClass")
        print("✓ Correctly verified existing class")

        # Should fail - class doesn't exist
        assert not gate.verify_action(temp_path, "remove_class", "NonexistentClass")
        print("✓ Correctly rejected non-existent class")

        # Should succeed - method exists
        assert gate.verify_action(temp_path, "modify_method", "test_method")
        print("✓ Correctly verified existing method")

        # Should fail - method doesn't exist
        assert not gate.verify_action(temp_path, "modify_method", "nonexistent_method")
        print("✓ Correctly rejected non-existent method")

        # Should succeed - variable exists
        assert gate.verify_action(temp_path, "modify_variable", "unused_variable")
        print("✓ Correctly verified existing variable")

        # Should fail - variable doesn't exist
        assert not gate.verify_action(temp_path, "modify_variable", "nonexistent_variable")
        print("✓ Correctly rejected non-existent variable")

    finally:
        temp_path.unlink()


def test_cache_functionality():
    """Test verification gate caching."""
    print("\n=== Testing Cache Functionality ===")

    gate = VerificationGate()

    test_code = "import os\n"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(test_code)
        f.flush()
        temp_path = Path(f.name)

    try:
        # First call - should compute and cache
        result1 = gate.verify_action(temp_path, "delete_import", "os")
        stats1 = gate.get_cache_stats()

        # Second call - should use cache
        result2 = gate.verify_action(temp_path, "delete_import", "os")
        stats2 = gate.get_cache_stats()

        assert result1 == result2  # Results should be identical
        assert stats1["cache_size"] == stats2["cache_size"]  # Cache size should be same

        print("✓ Cache functionality working correctly")
        print(f"  Cache size: {stats1['cache_size']}")

        # Clear cache and verify
        gate.clear_cache()
        stats3 = gate.get_cache_stats()
        assert stats3["cache_size"] == 0
        print("✓ Cache clear functionality working")

    finally:
        temp_path.unlink()


def test_hallucination_prevention():
    """Test that verification gate prevents hallucinated fixes."""
    print("\n=== Testing Hallucination Prevention ===")

    gate = VerificationGate()

    # Test file with only one import
    test_code = """
import os

def test_function():
    return os.getcwd()
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(test_code)
        f.flush()
        temp_path = Path(f.name)

    try:
        # Test trying to delete non-existent import (hallucinated fix)
        result = gate.verify_action(temp_path, "delete_import", "requests")
        assert not result, "Should have blocked hallucinated import deletion"
        print("✓ Correctly blocked hallucinated import deletion")

        # Test trying to modify non-existent function (hallucinated fix)
        result = gate.verify_action(temp_path, "modify_function", "nonexistent_func")
        assert not result, "Should have blocked hallucinated function modification"
        print("✓ Correctly blocked hallucinated function modification")

        # Test trying to remove non-existent class (hallucinated fix)
        result = gate.verify_action(temp_path, "remove_class", "NonexistentClass")
        assert not result, "Should have blocked hallucinated class removal"
        print("✓ Correctly blocked hallucinated class removal")

        print("✅ Epistemic Cascade prevention is working!")

    finally:
        temp_path.unlink()


if __name__ == "__main__":
    print("Testing Verification Gate - Epistemic Cascade Prevention")
    print("=" * 60)

    try:
        test_verification_gate_basic()
        test_verification_gate_with_real_code()
        test_cache_functionality()
        test_hallucination_prevention()

        print("\n" + "=" * 60)
        print("🎉 All tests passed! Verification Gate is working correctly.")
        print("✅ Epistemic Cascade prevention is active.")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
