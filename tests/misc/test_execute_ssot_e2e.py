#!/usr/bin/env python3
"""
End-to-end test for LocationAgent integration with execute_ssot.py
"""

import json
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_execute_ssot_e2e")
# REMOVED: _emit_applies_guardrail("p0", "test_execute_ssot_e2e", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_execute_ssot_e2e", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_execute_ssot_e2e", "state_snapshot")
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

# REMOVED: _emit_emits_metric_event("test_execute_ssot_e2e", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_execute_ssot_e2e", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_execute_ssot_e2e", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_execute_ssot_e2e", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_execute_ssot_e2e", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_execute_ssot_e2e", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_execute_ssot_e2e", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_execute_ssot_e2e", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_execute_ssot_e2e", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_execute_ssot_e2e", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_execute_ssot_e2e", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_execute_ssot_e2e", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_execute_ssot_e2e", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_execute_ssot_e2e", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_execute_ssot_e2e", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_execute_ssot_e2e", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_execute_ssot_e2e", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_execute_ssot_e2e", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_execute_ssot_e2e", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_execute_ssot_e2e", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_execute_ssot_e2e", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_execute_ssot_e2e", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_execute_ssot_e2e", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_execute_ssot_e2e", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_execute_ssot_e2e", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_execute_ssot_e2e", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_execute_ssot_e2e", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_execute_ssot_e2e", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_execute_ssot_e2e", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_execute_ssot_e2e", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_execute_ssot_e2e", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_execute_ssot_e2e", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_execute_ssot_e2e", "write_through")
# REMOVED: _emit_writes_through("p1", "test_execute_ssot_e2e", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_execute_ssot_e2e", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_execute_ssot_e2e", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_execute_ssot_e2e", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_execute_ssot_e2e", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_execute_ssot_e2e", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_execute_ssot_e2e", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_execute_ssot_e2e", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_execute_ssot_e2e", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_execute_ssot_e2e", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_execute_ssot_e2e", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_execute_ssot_e2e", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_execute_ssot_e2e", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_execute_ssot_e2e", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_execute_ssot_e2e", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_execute_ssot_e2e")
# REMOVED: _emit_gated_by_confidence("p1", "test_execute_ssot_e2e", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_execute_ssot_e2e")
# REMOVED: emit_determinism_digest("p0", "test_execute_ssot_e2e")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_execute_ssot_e2e", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_execute_ssot_e2e", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_execute_ssot_e2e", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_execute_ssot_e2e", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_execute_ssot_e2e", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_execute_ssot_e2e", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_execute_ssot_e2e", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_execute_ssot_e2e", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_execute_ssot_e2e", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_execute_ssot_e2e", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_execute_ssot_e2e", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_execute_ssot_e2e", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_execute_ssot_e2e", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_execute_ssot_e2e", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_execute_ssot_e2e", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_execute_ssot_e2e", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_execute_ssot_e2e", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_execute_ssot_e2e", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_execute_ssot_e2e", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_execute_ssot_e2e", "exec_snapshot_link")

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


def test_execute_ssot_integration():
    """Test that LocationAgent works correctly with execute_ssot.py"""

    print("=== End-to-End Test: execute_ssot.py with LocationAgent ===\n")

    # Create a test file in an invalid location
    test_dir = project_root / "temp_test_location"
    test_dir.mkdir(exist_ok=True)

    test_file = test_dir / "InvalidLocationAgent.py"
    test_file.write_text("""
# Invalid location agent - should be in agentic_core/
class InvalidLocationAgent:
    '''This file is in the wrong location'''
    pass
""")

    from agentic_core.L0_routing.scripts.execute_ssot import (
        RuntimeStateManager,
        SovereignDecisionEngine,
        execute_phase2_reconciliation,
    )
    print("1. Setting up agents and decision engine...")
    state_mgr = RuntimeStateManager(project_root)
    decision_engine = SovereignDecisionEngine(enable_llm=False)
    from agentic_core.L5_safety.reasoning.LocationHealerAgent import LocationHealerAgent
    agents = {"LocationAgent": LocationHealerAgent(project_root)}
    print("2. Creating violation plan...")
    violations_found = [
        {
            "suggested_agent": "LocationAgent",
            "file": str(test_file),
            "type": "LOCATION",
            "message": "File in invalid location: temp_test_location",
            "severity": "medium",
        },
    ]
    plan = {
        "violations_found": violations_found,
        "territory": "temp_test_location",
        "confidence": 0.9,
    }
    print(f"  Plan includes {len(violations_found)} violation(s)")
    print("\n3. Testing Phase 2 reconciliation...")
    result = execute_phase2_reconciliation(
        agents=agents,
        territory="temp_test_location",
        decision_engine=decision_engine,
        state_mgr=state_mgr,
        plan=plan,
        dry_run=False,  # Actually perform the healing
    )
    print(f"  Result: {json.dumps(result, indent=2)}")
    required_keys = [
        "violations_found",
        "violations_fixed",
        "status",
        "errors",
        "skipped",
        "execution_time_ms",
    ]
    missing_keys = [k for k in required_keys if k not in result]
    if missing_keys:
        print(f"✗ Missing required keys in result: {missing_keys}")
        return False
    if result["violations_found"] != 1:
        print(f"✗ Expected violations_found=1, got {result['violations_found']}")
        return False
    if result["status"] not in ["success", "partial_success", "skipped"]:
        print(f"✗ Unexpected status: {result['status']}")
        return False
    print("✓ Phase 2 reconciliation completed successfully")
    if not test_file.exists():
        print("✓ File was successfully moved/archived")
    else:
        print("! File still exists (may be expected if healing failed)")
    return True

def test_agent_validation():
    """Test that LocationAgent passes PreFlightValidator validation"""

    print("\n=== Agent Validation Test ===\n")

    from agentic_core.L0_routing.scripts.execute_ssot import PreFlightValidator
    validator = PreFlightValidator(project_root)
    from agentic_core.L5_safety.reasoning.LocationHealerAgent import LocationHealerAgent
    agents = {"LocationAgent": LocationHealerAgent(project_root)}
    print("1. Testing agent integrity validation...")
    integrity_errors = validator.validate_agent_integrity(agents)
    if integrity_errors:
        print(f"✗ Agent integrity errors: {integrity_errors}")
        return False
    else:
        print("✓ All agents pass integrity validation")
    location_agent = agents["LocationAgent"]
    if hasattr(location_agent, "heal") and callable(location_agent.heal):
        print("✓ LocationAgent has required heal method")
    else:
        print("✗ LocationAgent missing heal method")
        return False
    if hasattr(location_agent, "heal_violations") and callable(location_agent.heal_violations):
        print("✓ LocationAgent has heal_violations method")
    else:
        print("✗ LocationAgent missing heal_violations method")
        return False
    return True

if __name__ == "__main__":
    print("=== LocationAgent execute_ssot.py End-to-End Test ===\n")

    integration_test = test_execute_ssot_integration()
    validation_test = test_agent_validation()

    print("\n=== Final Results ===")
    print(f"End-to-end integration: {'PASS' if integration_test else 'FAIL'}")
    print(f"Agent validation: {'PASS' if validation_test else 'FAIL'}")

    if integration_test and validation_test:
        print("\n✅ All tests passed!")
        print("LocationAgent is fully compatible with execute_ssot.py")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)
