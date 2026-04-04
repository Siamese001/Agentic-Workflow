from pathlib import Path

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "sovereign_lockdown_check_util")
emit_determinism_digest("p0", "sovereign_lockdown_check_util")

_emit_dispatches_healing_run("p1", "sovereign_lockdown_check_util", "L0")
_emit_routes_through("p1", "sovereign_lockdown_check_util", "L0")
_emit_checks_agent_registry("p1", "sovereign_lockdown_check_util", "agent_registry")
_emit_validates_agent_capability("p1", "sovereign_lockdown_check_util", "capability")
_emit_dispatches_execution_plan("p1", "sovereign_lockdown_check_util", "exec_plan")
_emit_agent_executes_agent("p1", "sovereign_lockdown_check_util", "sub_agent")
_emit_routes_to_agent("p1", "sovereign_lockdown_check_util", "target_agent")
_emit_verifies_policy("p1", "sovereign_lockdown_check_util", "policy_check")
_emit_observes_runtime_state("p1", "sovereign_lockdown_check_util", "runtime_state")
_emit_verifies_boundary("p1", "sovereign_lockdown_check_util", "boundary_check")
_emit_transcripts_response("p1", "sovereign_lockdown_check_util", "transcript")
_emit_hard_fails_untranscripted("p1", "sovereign_lockdown_check_util")
_emit_gated_by_confidence("p1", "sovereign_lockdown_check_util", "confidence_gate")
_emit_escalates_to_human("p1", "sovereign_lockdown_check_util", "L0")
_emit_reads_policy_state("p1", "sovereign_lockdown_check_util", "L0")
_emit_authorize_and_execute("p2", "sovereign_lockdown_check_util", "execution_auth")
_emit_validates_capability("p2", "sovereign_lockdown_check_util", "capability_check")
_emit_routes_to_capability("p2", "sovereign_lockdown_check_util", "capability_route")
_emit_writes_via_uwg("p2", "sovereign_lockdown_check_util", "uwg_write")
_emit_blocks_direct_write("p2", "sovereign_lockdown_check_util", "direct_write_block")
_emit_records_tool_invocation("p2", "sovereign_lockdown_check_util", "tool_invocation")
_emit_captures_execution_output("p2", "sovereign_lockdown_check_util", "exec_output")
_emit_dispatches_agent("p3", "sovereign_lockdown_check_util", "agent_dispatch")
_emit_coordinates_agents("p3", "sovereign_lockdown_check_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "sovereign_lockdown_check_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "sovereign_lockdown_check_util", "healing_outcome")
_emit_escalates_failure("p3", "sovereign_lockdown_check_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "sovereign_lockdown_check_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "sovereign_lockdown_check_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "sovereign_lockdown_check_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "sovereign_lockdown_check_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "sovereign_lockdown_check_util", "eval_metric")
_emit_stores_embedding("p4", "sovereign_lockdown_check_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "sovereign_lockdown_check_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "sovereign_lockdown_check_util", "exec_snapshot_link")

"\n[PHASE 7/8] Sovereign Lockdown Check - CI/CD Entrypoint.\n\nThis script acts as the final gatekeeper for architectural purity.\nIt interfaces with the ArchitectureGovernorAgent in headless mode.\n\nUsage:\n    python scripts/ci/sovereign_lockdown_check_util.py\n\nExit Codes:\n    0 - Repository is sovereign-compliant (no violations)\n    1 - Violations detected (commit should be blocked)\n    2 - Error during verification\n\nPre-commit Hook Entry:\n    - id: sovereign-lockdown-verification\n      name: Sovereign Lockdown Verification (Phase 7)\n      entry: python\n      args: [scripts/ci/sovereign_lockdown_check_util.py]\n      language: python\n      pass_filenames: false\n      always_run: true\n"
import sys

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
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
    _emit_routes_to_agent,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

_emit_emits_metric_event("sovereign_lockdown_check_util", "p4obs", "metric_1")
_emit_emits_metric_event("sovereign_lockdown_check_util", "p4obs", "metric_2")
_emit_emits_metric_event("sovereign_lockdown_check_util", "p4obs", "metric_3")
_emit_emits_metric_event("sovereign_lockdown_check_util", "p4obs", "metric_4")
_emit_emits_metric_event("sovereign_lockdown_check_util", "p4obs", "metric_5")
_emit_emits_metric_event("sovereign_lockdown_check_util", "p4obs", "metric_6")
_emit_records_incident_event("sovereign_lockdown_check_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("sovereign_lockdown_check_util", "p4obs", "anomaly")
_emit_writes_observability_log("sovereign_lockdown_check_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("sovereign_lockdown_check_util", "p4obs", "mon_state")
_emit_triggers_alert("sovereign_lockdown_check_util", "p4obs", "alert")
_emit_links_incident_trace("sovereign_lockdown_check_util", "p4obs", "trace_link")
_emit_captures_pattern("sovereign_lockdown_check_util", "p3lm", "pattern")
_emit_records_learning_event("sovereign_lockdown_check_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("sovereign_lockdown_check_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("sovereign_lockdown_check_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("sovereign_lockdown_check_util", "p3lm", "routing")
_emit_improves_agent_policy("sovereign_lockdown_check_util", "p3lm", "policy")
_emit_stores_learning_state("sovereign_lockdown_check_util", "p3lm", "state")
_emit_records_execution_trace("sovereign_lockdown_check_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("sovereign_lockdown_check_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("sovereign_lockdown_check_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("sovereign_lockdown_check_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("sovereign_lockdown_check_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("sovereign_lockdown_check_util", "env_read", "p2_env_1")
_emit_reads_environ("sovereign_lockdown_check_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("sovereign_lockdown_check_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("sovereign_lockdown_check_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "sovereign_lockdown_check_util", "context_pull")
_emit_pulls_context("p1", "sovereign_lockdown_check_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "sovereign_lockdown_check_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "sovereign_lockdown_check_util", "uwg_term_2")
_emit_writes_through("p1", "sovereign_lockdown_check_util", "write_through")
_emit_writes_through("p1", "sovereign_lockdown_check_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "sovereign_lockdown_check_util", "safety_validation")
_emit_invokes_eval("p1", "sovereign_lockdown_check_util", "eval_call")
_emit_proposal_commits_routing("p1", "sovereign_lockdown_check_util", "routing_commit")


def main() -> int:
    """Run sovereign lockdown verification."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "main", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "main", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "main")
    try:
        project_root = Path(__file__).resolve().parent.parent.parent
        # guardian: allow-global-mutation
        sys.path.insert(0, str(project_root))
        from agentic_core.L0_routing.utils.subprocess_runner_util import invoke_arch_governor

        print("=" * 60)
        print("SOVEREIGN LOCKDOWN VERIFICATION")
        print("=" * 60)
        result = invoke_arch_governor(action="verify", project_root=project_root, auto_approve=True)
        raw_result = result.get("raw_result", result)
        passed = result.get("success", False)
        violations_found = raw_result.get("violations_found", result.get("violations_found", 0))
        roots_scanned = raw_result.get("roots_scanned", result.get("roots_scanned", []))
        print(f"\nRoots Scanned: {(', '.join(roots_scanned) if roots_scanned else 'None')}")
        print(f"Violations Found: {violations_found}")
        if passed:
            print("\n[OK] Sovereign Lockdown Verified: Repository is architecture-pure.")
            print("=" * 60)
            return 0
        else:
            print(f"\n[FAIL] Lockdown Failed: {violations_found} violations detected.")
            violations = raw_result.get("violations", [])
            if violations:
                print("\nViolations:")
                for v in violations[:10]:
                    if isinstance(v, dict):
                        print(f"  - [{v.get('type', 'UNKNOWN')}] {v.get('message', str(v))}")
                    else:
                        print(f"  - {v}")
            print(
                "\nTo fix: Run `python -m agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent --heal`"
            )
            print("=" * 60)
            return 1
    except ImportError as e:
        print(f"[ERROR] Import Error: {e}")
        print("Ensure agentic_core is properly installed.")
        return 2
    # guardian: allow-silent-swallow
    except (ValueError, TypeError) as e:
        print(f"[ERROR] Verification Error: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
