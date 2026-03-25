#!/usr/bin/env python3
"""
Test script to reproduce the heal_violation issue with LocationAgent.
"""

import sys
from pathlib import Path

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_location_agent_heal")
# REMOVED: _emit_applies_guardrail("p0", "test_location_agent_heal", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_location_agent_heal", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_location_agent_heal", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_location_agent_heal")
# REMOVED: emit_determinism_digest("p0", "test_location_agent_heal")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_location_agent_heal", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_location_agent_heal", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_location_agent_heal", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_location_agent_heal", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_location_agent_heal", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_location_agent_heal", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_location_agent_heal", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_location_agent_heal", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_location_agent_heal", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_location_agent_heal", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_location_agent_heal", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_location_agent_heal", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_location_agent_heal", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_location_agent_heal", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_location_agent_heal", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_location_agent_heal", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_location_agent_heal", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_location_agent_heal", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_location_agent_heal", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_location_agent_heal", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agentic_core.L5_safety.reasoning.LocationHealerAgent import LocationHealerAgent as LocationAgent
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_location_agent_heal", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_location_agent_heal", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_location_agent_heal", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_location_agent_heal", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_location_agent_heal", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_location_agent_heal", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_location_agent_heal", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_location_agent_heal", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_location_agent_heal", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_location_agent_heal", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_location_agent_heal", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_location_agent_heal", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_location_agent_heal", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_location_agent_heal", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_location_agent_heal", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_location_agent_heal", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_location_agent_heal", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_location_agent_heal", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_location_agent_heal", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_location_agent_heal", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_location_agent_heal", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_location_agent_heal", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_location_agent_heal", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_location_agent_heal", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_location_agent_heal", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_location_agent_heal", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_location_agent_heal", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_location_agent_heal", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_location_agent_heal", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_location_agent_heal", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_location_agent_heal", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_location_agent_heal", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_location_agent_heal", "write_through")
# REMOVED: _emit_writes_through("p1", "test_location_agent_heal", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_location_agent_heal", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_location_agent_heal", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_location_agent_heal", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_location_agent_heal", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_location_agent_heal", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_location_agent_heal", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_location_agent_heal", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_location_agent_heal", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_location_agent_heal", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_location_agent_heal", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_location_agent_heal", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_location_agent_heal", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_location_agent_heal", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_location_agent_heal", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_location_agent_heal")
# REMOVED: _emit_gated_by_confidence("p1", "test_location_agent_heal", "confidence_gate")


def test_location_agent_heal_method():
    """Test if LocationAgent has the required heal method."""

    print("Testing LocationAgent heal method...")

    # Initialize LocationAgent
    agent = LocationAgent(project_root)

    # Check if heal method exists
    if hasattr(agent, "heal"):
        print("✓ LocationAgent has heal method")

        # Try to call it with a mock violation
        mock_violation = {
            "type": "LOCATION",
            "file": str(project_root / "test_file.py"),
            "message": "Test violation",
        }

        try:
            result = agent.heal(mock_violation)
            print("✓ heal method executed successfully")
            print(f"  Result: {result}")
        except Exception as e:  # guardian: allow-silent-swallower
            print(f"✗ heal method failed: {e}")
            return False
    else:
        print("✗ LocationAgent does not have heal method")
        print(f"  Available methods: {[m for m in dir(agent) if not m.startswith('_')]}")
        return False

    return True


def test_heal_violations_method():
    """Test if LocationAgent has heal_violations method."""

    print("\nTesting LocationAgent heal_violations method...")

    agent = LocationAgent(project_root)

    if hasattr(agent, "heal_violations"):
        print("✓ LocationAgent has heal_violations method")

        # Try to call it
        violations = [(Path("test_file.py"), "Test violation")]

        try:
            result = agent.heal_violations(violations)
            print("✓ heal_violations method executed successfully")
            print(f"  Result: {result}")
        except Exception as e:  # guardian: allow-silent-swallower
            print(f"✗ heal_violations method failed: {e}")
            return False
    else:
        print("✗ LocationAgent does not have heal_violations method")
        return False

    return True


if __name__ == "__main__":
    print("=== LocationAgent Healing Method Test ===\n")

    heal_test = test_location_agent_heal_method()
    heal_violations_test = test_heal_violations_method()

    print("\n=== Test Results ===")
    print(f"heal method: {'PASS' if heal_test else 'FAIL'}")
    print(f"heal_violations method: {'PASS' if heal_violations_test else 'FAIL'}")

    if not heal_test or not heal_violations_test:
        print("\n⚠️  LocationAgent needs to implement proper healing methods for execute_ssot.py")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        sys.exit(0)
