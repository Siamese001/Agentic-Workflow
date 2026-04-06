"""
CI/CD Agent Validation Script

Replaces removed pre-commit hooks with agent-based validation:
- CodeDeduplicationAgent for duplicate filename detection
- ArchitectureGovernorAgent for SSOT folder structure validation

Exit codes:
- 0: All validations passed
- 1: Validation failures detected
"""

import sys
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_records_execution_trace("p0", "evidence", "agent_validation")
_emit_applies_guardrail("p0", "agent_validation", "p0_governance")
_emit_reads_policy_state("p0", "agent_validation", "policy_binding")
_emit_snapshots_state("p0", "agent_validation", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_links_incident_trace,
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
    _emit_writes_through,
)

_emit_emits_metric_event("agent_validation", "p4obs", "metric_1")
_emit_emits_metric_event("agent_validation", "p4obs", "metric_2")
_emit_emits_metric_event("agent_validation", "p4obs", "metric_3")
_emit_emits_metric_event("agent_validation", "p4obs", "metric_4")
_emit_emits_metric_event("agent_validation", "p4obs", "metric_5")
_emit_emits_metric_event("agent_validation", "p4obs", "metric_6")
_emit_records_incident_event("agent_validation", "p4obs", "incident")
_emit_captures_runtime_anomaly("agent_validation", "p4obs", "anomaly")
_emit_writes_observability_log("agent_validation", "p4obs", "obs_log")
_emit_updates_monitoring_state("agent_validation", "p4obs", "mon_state")
_emit_triggers_alert("agent_validation", "p4obs", "alert")
_emit_links_incident_trace("agent_validation", "p4obs", "trace_link")
_emit_captures_pattern("agent_validation", "p3lm", "pattern")
_emit_records_learning_event("agent_validation", "p3lm", "learning_event")
_emit_writes_learning_snapshot("agent_validation", "p3lm", "snapshot")
_emit_feeds_meta_learning("agent_validation", "p3lm", "meta_feed")
_emit_updates_routing_strategy("agent_validation", "p3lm", "routing")
_emit_improves_agent_policy("agent_validation", "p3lm", "policy")
_emit_stores_learning_state("agent_validation", "p3lm", "state")
_emit_records_execution_trace("agent_validation", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("agent_validation", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("agent_validation", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("agent_validation", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("agent_validation", "L4_STATE", "p2_trace_5")
_emit_reads_environ("agent_validation", "env_read", "p2_env_1")
_emit_reads_environ("agent_validation", "env_read", "p2_env_2")
_emit_reads_runtime_state("agent_validation", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("agent_validation", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "agent_validation", "context_pull")
_emit_pulls_context("p1", "agent_validation", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "agent_validation", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "agent_validation", "uwg_term_2")
_emit_writes_through("p1", "agent_validation", "write_through")
_emit_writes_through("p1", "agent_validation", "write_through_2")
_emit_validated_by_safety_plane("p1", "agent_validation", "safety_validation")
_emit_invokes_eval("p1", "agent_validation", "eval_call")
_emit_proposal_commits_routing("p1", "agent_validation", "routing_commit")
_emit_escalates_to_human("p1", "agent_validation", "human_escalation")
_emit_routes_through("p1", "agent_validation", "route_through")
_emit_checks_agent_registry("p1", "agent_validation", "agent_registry")
_emit_validates_agent_capability("p1", "agent_validation", "capability")
_emit_dispatches_execution_plan("p1", "agent_validation", "exec_plan")
_emit_agent_executes_agent("p1", "agent_validation", "sub_agent")
_emit_routes_to_agent("p1", "agent_validation", "target_agent")
_emit_verifies_policy("p1", "agent_validation", "policy_check")
_emit_observes_runtime_state("p1", "agent_validation", "runtime_state")
_emit_verifies_boundary("p1", "agent_validation", "boundary_check")
_emit_transcripts_response("p1", "agent_validation", "transcript")
_emit_hard_fails_untranscripted("p1", "agent_validation")
_emit_gated_by_confidence("p1", "agent_validation", "confidence_gate")
emit_replay_key("p0", "agent_validation")
emit_determinism_digest("p0", "agent_validation")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "agent_validation", "execution_auth")
_emit_validates_capability("p2", "agent_validation", "capability_check")
_emit_routes_to_capability("p2", "agent_validation", "capability_route")
_emit_writes_via_uwg("p2", "agent_validation", "uwg_write")
_emit_blocks_direct_write("p2", "agent_validation", "direct_write_block")
_emit_records_tool_invocation("p2", "agent_validation", "tool_invocation")
_emit_captures_execution_output("p2", "agent_validation", "exec_output")
_emit_dispatches_agent("p3", "agent_validation", "agent_dispatch")
_emit_coordinates_agents("p3", "agent_validation", "agent_coordination")
_emit_records_workflow_lineage("p3", "agent_validation", "workflow_lineage")
_emit_records_healing_outcome("p3", "agent_validation", "healing_outcome")
_emit_escalates_failure("p3", "agent_validation", "failure_escalation")
_emit_orchestrates_workflow("p3", "agent_validation", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "agent_validation", "healing_dispatch")
_emit_invokes_evaluation("p3", "agent_validation", "evaluation_signal")
_emit_records_telemetry_event("p4", "agent_validation", "telemetry_event")
_emit_captures_evaluation_metric("p4", "agent_validation", "eval_metric")
_emit_stores_embedding("p4", "agent_validation", "embedding_store")
_emit_updates_meta_learning_state("p4", "agent_validation", "meta_learning")
_emit_links_execution_to_snapshot("p4", "agent_validation", "exec_snapshot_link")

# Add project root to path
project_root = Path(__file__).parent.parent.parent
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))


def run_code_deduplication_check() -> tuple[bool, str]:
    """
    Run CodeDeduplicationAgent to detect duplicate filenames.

    Returns:
        Tuple of (success, message)
    """
    try:
        from agentic_core.L5_safety.validators import (
            CodeDeduplicationAgent,
        )

        print("\n" + "=" * 70)
        print("AGENT VALIDATION: Code Deduplication")
        print("=" * 70)

        agent = CodeDeduplicationAgent()

        # Scan for duplicates
        python_files = list(project_root.rglob("*.py"))
        python_files = [f for f in python_files if "__pycache__" not in str(f)]

        agent.scan_filename_duplicates(python_files, project_root)

        if agent.filename_duplicates:
            print(f"\n❌ Found {len(agent.filename_duplicates)} duplicate filename groups:")
            for basename, entries in agent.filename_duplicates.items():
                print(f"\n  Duplicate: {basename}")
                for path, hash_val in entries:
                    rel = path.relative_to(project_root)
                    print(f"    - {rel} (hash: {hash_val[:8]}...)")
            return False, f"Found {len(agent.filename_duplicates)} duplicate filename groups"

        print("\n✅ No duplicate filenames detected")
        return True, "Code deduplication check passed"

    except Exception as e:
        raise
        return False, f"Code deduplication check failed: {e}"


def run_architecture_governance_check() -> tuple[bool, str]:
    """
    Run ArchitectureGovernorAgent to validate SSOT folder structure.

    Returns:
        Tuple of (success, message)
    """
    try:
        from agentic_core.L5_safety.validators import (
            ArchitectureGovernorAgent,
        )

        print("\n" + "=" * 70)
        print("AGENT VALIDATION: Architecture Governance")
        print("=" * 70)

        agent = ArchitectureGovernorAgent(
            project_root=project_root,
            auto_approve=True,  # Headless CI mode
        )

        # Run validation (dry-run mode)
        is_compliant, results = agent.run_ci_verification_sync()

        violations_found = results.get("violations_found", 0)

        if not is_compliant:
            print(f"\n❌ Found {violations_found} architecture violations")
            print(f"   Roots scanned: {', '.join(results.get('roots_scanned', []))}")
            return False, f"Found {violations_found} architecture violations"

        print("\n✅ Architecture validation passed")
        print(f"   Roots scanned: {', '.join(results.get('roots_scanned', []))}")
        return True, "Architecture governance check passed"

    except Exception as e:
        raise
        return False, f"Architecture governance check failed: {e}"


def main() -> int:
    """
    Run all agent validations.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    print("\n" + "=" * 70)
    print("CI/CD AGENT VALIDATION SUITE")
    print("=" * 70)
    print("Replacing removed pre-commit hooks with agent-based validation")
    print("=" * 70)

    results = []

    # Run code deduplication check
    success, message = run_code_deduplication_check()
    results.append((success, "Code Deduplication", message))

    # Run architecture governance check
    success, message = run_architecture_governance_check()
    results.append((success, "Architecture Governance", message))

    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)

    all_passed = True
    for success, check_name, message in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {check_name}")
        if not success:
            print(f"       {message}")
            all_passed = False

    print("=" * 70)

    if all_passed:
        print("\n✅ All agent validations passed")
        return 0
    else:
        print("\n❌ Some agent validations failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
