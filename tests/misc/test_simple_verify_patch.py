#!/usr/bin/env python3
"""
Simple Verification Script for Universal Healing Implementation
Quick verification that the patch is correctly applied.
"""

import re
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    L0_ROUTING_DIR,
)
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_simple_verify_patch")
# REMOVED: _emit_applies_guardrail("p0", "test_simple_verify_patch", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_simple_verify_patch", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_simple_verify_patch", "state_snapshot")
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

# REMOVED: _emit_emits_metric_event("test_simple_verify_patch", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_simple_verify_patch", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_simple_verify_patch", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_simple_verify_patch", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_simple_verify_patch", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_simple_verify_patch", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_simple_verify_patch", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_simple_verify_patch", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_simple_verify_patch", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_simple_verify_patch", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_simple_verify_patch", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_simple_verify_patch", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_simple_verify_patch", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_simple_verify_patch", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_simple_verify_patch", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_simple_verify_patch", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_simple_verify_patch", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_simple_verify_patch", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_simple_verify_patch", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_simple_verify_patch", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_simple_verify_patch", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_simple_verify_patch", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_simple_verify_patch", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_simple_verify_patch", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_simple_verify_patch", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_simple_verify_patch", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_simple_verify_patch", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_simple_verify_patch", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_simple_verify_patch", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_simple_verify_patch", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_simple_verify_patch", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_simple_verify_patch", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_simple_verify_patch", "write_through")
# REMOVED: _emit_writes_through("p1", "test_simple_verify_patch", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_simple_verify_patch", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_simple_verify_patch", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_simple_verify_patch", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_simple_verify_patch", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_simple_verify_patch", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_simple_verify_patch", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_simple_verify_patch", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_simple_verify_patch", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_simple_verify_patch", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_simple_verify_patch", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_simple_verify_patch", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_simple_verify_patch", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_simple_verify_patch", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_simple_verify_patch", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_simple_verify_patch")
# REMOVED: _emit_gated_by_confidence("p1", "test_simple_verify_patch", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_simple_verify_patch")
# REMOVED: emit_determinism_digest("p0", "test_simple_verify_patch")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_simple_verify_patch", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_simple_verify_patch", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_simple_verify_patch", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_simple_verify_patch", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_simple_verify_patch", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_simple_verify_patch", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_simple_verify_patch", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_simple_verify_patch", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_simple_verify_patch", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_simple_verify_patch", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_simple_verify_patch", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_simple_verify_patch", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_simple_verify_patch", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_simple_verify_patch", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_simple_verify_patch", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_simple_verify_patch", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_simple_verify_patch", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_simple_verify_patch", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_simple_verify_patch", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_simple_verify_patch", "exec_snapshot_link")


def verify_patch():
    """Verify that the Universal Healing patch is correctly applied."""
    print("🔍 Universal Healing Patch Verification")
    print("=" * 50)

    project_root = Path.cwd()
    execute_ssot_path = project_root / L0_ROUTING_DIR / "scripts" / "execute_ssot.py"

    if not execute_ssot_path.exists():
        print("❌ FAIL: execute_ssot.py not found")
        return False

    # Read the file
    try:
        content = execute_ssot_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"❌ FAIL: Could not read execute_ssot.py: {e}")
        return False

    # Check for Universal Healing comment
    if "[UNIVERSAL HEALING]" not in content:
        print("❌ FAIL: Universal Healing patch not found")
        return False
    else:
        print("✅ PASS: Universal Healing patch detected")

    # Check for Phase 2.5 Sovereignty Enforcement
    if "Phase 2.5: Sovereignty Enforcement" not in content:
        print("❌ FAIL: Phase 2.5 Sovereignty Enforcement not found")
        return False
    else:
        print("✅ PASS: Phase 2.5 Sovereignty Enforcement detected")

    # Check for Pascal agent healing call
    if "pascal.heal_repository(target_territory=territory, dry_run=False)" not in content:
        print("❌ FAIL: Pascal agent healing call not found")
        return False
    else:
        print("✅ PASS: Pascal agent healing call detected")

    # Check for dry-run safety
    if "if not dry_run:" not in content:
        print("❌ FAIL: Dry-run safety check not found")
        return False
    else:
        print("✅ PASS: Dry-run safety check detected")

    # Check for all required agents in imports
    required_agents = ["PascalSovereigntyAgent", "RootHygieneAgent"]

    for agent in required_agents:
        if agent not in content:
            print(f"❌ FAIL: {agent} not found in imports")
            return False
        else:
            print(f"✅ PASS: {agent} found in imports")

    # Check that the patch is in the right location (main execution loop)
    main_execution_pattern = (
        r"for territory in targets:.*?if not dry_run:.*?pascal = agents\['pascal_sovereignty'\]"
    )
    if not re.search(main_execution_pattern, content, re.DOTALL):
        print("❌ FAIL: Universal Healing logic not in main execution loop")
        return False
    else:
        print("✅ PASS: Universal Healing logic in correct location")

    print("\n" + "=" * 50)
    print("🎉 PATCH VERIFICATION COMPLETE")
    print("=" * 50)
    print("✅ Universal Healing patch is CORRECTLY APPLIED")
    print("\nKey Features Verified:")
    print("- Universal Healing comment block")
    print("- Phase 2.5 Sovereignty Enforcement")
    print("- Pascal agent heal_repository call")
    print("- Dry-run safety mechanism")
    print("- All required agents imported")
    print("- Logic in main execution loop")

    return True


def test_imports():
    """Test that the patched module can be imported."""
    print("\n🧪 Module Import Test")
    print("-" * 30)

    try:
        project_root = Path.cwd()
        sys.path.insert(0, str(project_root))

        from agentic_core.L0_routing.scripts.execute_ssot import AutonomousDecisionEngine

        print("✅ PASS: Module imports successfully")

        # Test decision engine
        decision_engine = AutonomousDecisionEngine(enable_llm=False)
        confidence = decision_engine.calculate_healing_confidence(
            violations_count=10,
            violation_types=["NAMING", "HIERARCHY"],
            territory="prompt_governance",
        )

        print(f"✅ PASS: Decision engine working (confidence: {confidence.value:.2f})")
        return True

    except Exception as e:  # guardian: allow-silent-swallower
        print(f"❌ FAIL: Import test failed: {e}")
        return False


if __name__ == "__main__":
    patch_ok = verify_patch()
    imports_ok = test_imports()

    if patch_ok and imports_ok:
        print("\n🎉 ALL VERIFICATIONS PASSED")
        print("Universal Healing is READY FOR USE!")
        sys.exit(0)
    else:
        print("\n❌ SOME VERIFICATIONS FAILED")
        sys.exit(1)
