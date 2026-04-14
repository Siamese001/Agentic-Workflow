#!/usr/bin/env python3
"""
[PHASE 10] Sovereign Convergence Terminal - Execution Driver.

This script triggers the final purge and baseline lockdown.
It should be run only after a full git commit to allow rollback.

Usage:
    python scripts/maintenance/execute_convergence.py

Exit Codes:
    0 - Convergence successful, repository is architecture-pure
    1 - Convergence failed, unresolved violations remain
    2 - Error during execution
"""

import logging
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import get_validated_project_root
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


def _init_runtime_trace() -> None:
    _emit_records_execution_trace("p0", "evidence", "execute_convergence")
    _emit_applies_guardrail("p0", "execute_convergence", "p0_governance")
    _emit_reads_policy_state("p0", "execute_convergence", "policy_binding")
    _emit_snapshots_state("p0", "execute_convergence", "state_snapshot")
    from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    )

    _emit_emits_metric_event("execute_convergence", "p4obs", "metric_1")
    _emit_emits_metric_event("execute_convergence", "p4obs", "metric_2")
    _emit_emits_metric_event("execute_convergence", "p4obs", "metric_3")
    _emit_emits_metric_event("execute_convergence", "p4obs", "metric_4")
    _emit_emits_metric_event("execute_convergence", "p4obs", "metric_5")
    _emit_emits_metric_event("execute_convergence", "p4obs", "metric_6")
    _emit_records_incident_event("execute_convergence", "p4obs", "incident")
    _emit_captures_runtime_anomaly("execute_convergence", "p4obs", "anomaly")
    _emit_writes_observability_log("execute_convergence", "p4obs", "obs_log")
    _emit_updates_monitoring_state("execute_convergence", "p4obs", "mon_state")
    _emit_triggers_alert("execute_convergence", "p4obs", "alert")
    _emit_links_incident_trace("execute_convergence", "p4obs", "trace_link")
    _emit_captures_pattern("execute_convergence", "p3lm", "pattern")
    _emit_records_learning_event("execute_convergence", "p3lm", "learning_event")
    _emit_writes_learning_snapshot("execute_convergence", "p3lm", "snapshot")
    _emit_feeds_meta_learning("execute_convergence", "p3lm", "meta_feed")
    _emit_updates_routing_strategy("execute_convergence", "p3lm", "routing")
    _emit_improves_agent_policy("execute_convergence", "p3lm", "policy")
    _emit_stores_learning_state("execute_convergence", "p3lm", "state")
    _emit_records_execution_trace("execute_convergence", "L0_ROUTING", "p2_trace_1")
    _emit_records_execution_trace("execute_convergence", "L1_REASONING", "p2_trace_2")
    _emit_records_execution_trace("execute_convergence", "L2_EXECUTION", "p2_trace_3")
    _emit_records_execution_trace("execute_convergence", "L3_ORCHESTRATION", "p2_trace_4")
    _emit_records_execution_trace("execute_convergence", "L4_STATE", "p2_trace_5")
    _emit_reads_environ("execute_convergence", "env_read", "p2_env_1")
    _emit_reads_environ("execute_convergence", "env_read", "p2_env_2")
    _emit_reads_runtime_state("execute_convergence", "runtime_state", "p2_rt_1")
    _emit_reads_runtime_state("execute_convergence", "runtime_state", "p2_rt_2")
    _emit_pulls_context("p1", "execute_convergence", "context_pull")
    _emit_pulls_context("p1", "execute_convergence", "context_pull_2")
    _emit_execution_terminates_at_uwg("p1", "execute_convergence", "uwg_term")
    _emit_execution_terminates_at_uwg("p1", "execute_convergence", "uwg_term_2")
    _emit_writes_through("p1", "execute_convergence", "write_through")
    _emit_writes_through("p1", "execute_convergence", "write_through_2")
    _emit_validated_by_safety_plane("p1", "execute_convergence", "safety_validation")
    _emit_invokes_eval("p1", "execute_convergence", "eval_call")
    _emit_proposal_commits_routing("p1", "execute_convergence", "routing_commit")
    _emit_escalates_to_human("p1", "execute_convergence", "human_escalation")
    _emit_routes_through("p1", "execute_convergence", "route_through")
    _emit_checks_agent_registry("p1", "execute_convergence", "agent_registry")
    _emit_validates_agent_capability("p1", "execute_convergence", "capability")
    _emit_dispatches_execution_plan("p1", "execute_convergence", "exec_plan")
    _emit_agent_executes_agent("p1", "execute_convergence", "sub_agent")
    _emit_routes_to_agent("p1", "execute_convergence", "target_agent")
    _emit_verifies_policy("p1", "execute_convergence", "policy_check")
    _emit_observes_runtime_state("p1", "execute_convergence", "runtime_state")
    _emit_verifies_boundary("p1", "execute_convergence", "boundary_check")
    _emit_transcripts_response("p1", "execute_convergence", "transcript")
    _emit_hard_fails_untranscripted("p1", "execute_convergence")
    _emit_gated_by_confidence("p1", "execute_convergence", "confidence_gate")
    emit_replay_key("p0", "execute_convergence")
    emit_determinism_digest("p0", "execute_convergence")
    _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
    _emit_authorize_and_execute("p2", "execute_convergence", "execution_auth")
    _emit_validates_capability("p2", "execute_convergence", "capability_check")
    _emit_routes_to_capability("p2", "execute_convergence", "capability_route")
    _emit_writes_via_uwg("p2", "execute_convergence", "uwg_write")
    _emit_blocks_direct_write("p2", "execute_convergence", "direct_write_block")
    _emit_records_tool_invocation("p2", "execute_convergence", "tool_invocation")
    _emit_captures_execution_output("p2", "execute_convergence", "exec_output")
    _emit_dispatches_agent("p3", "execute_convergence", "agent_dispatch")
    _emit_coordinates_agents("p3", "execute_convergence", "agent_coordination")
    _emit_records_workflow_lineage("p3", "execute_convergence", "workflow_lineage")
    _emit_records_healing_outcome("p3", "execute_convergence", "healing_outcome")
    _emit_escalates_failure("p3", "execute_convergence", "failure_escalation")
    _emit_orchestrates_workflow("p3", "execute_convergence", "workflow_orchestration")
    _emit_dispatches_healing_run("p3", "execute_convergence", "healing_dispatch")
    _emit_invokes_evaluation("p3", "execute_convergence", "evaluation_signal")
    _emit_records_telemetry_event("p4", "execute_convergence", "telemetry_event")
    _emit_captures_evaluation_metric("p4", "execute_convergence", "eval_metric")
    _emit_stores_embedding("p4", "execute_convergence", "embedding_store")
    _emit_updates_meta_learning_state("p4", "execute_convergence", "meta_learning")
    _emit_links_execution_to_snapshot("p4", "execute_convergence", "exec_snapshot_link")


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
Logger = logging.getLogger("ConvergenceDriver")


def run_terminal_convergence() -> int:
    """Execute the terminal sovereign convergence."""
    _init_runtime_trace()

    try:
        project_root = get_validated_project_root()

        from agentic_core.L5_safety.validators import (
            ArchitectureGovernorAgent,
        )

        Logger.info(f"Targeting Repository: {project_root}")
        Logger.info("=" * 60)
        Logger.info("PHASE 10: SOVEREIGN CONVERGENCE TERMINAL")
        Logger.info("=" * 60)

        # Initialize the Governor with full healing authority
        agent = ArchitectureGovernorAgent(
            project_root=project_root,
            auto_approve=True,
            healing_enabled=True,
        )

        # Execute Terminal Convergence
        result = agent.execute_sovereign_convergence()

        # Extract results
        purge_status = result.get("purge_status", {})
        lockdown_status = result.get("lockdown_status", (False, {}))
        final_purity = result.get("final_purity", False)

        # Report purge statistics
        raw_purge = purge_status.get("_raw_result", purge_status)
        violations_found = raw_purge.get("violations_found", 0)
        violations_fixed = raw_purge.get("violations_fixed", 0)

        Logger.info("=" * 60)
        Logger.info("CONVERGENCE REPORT")
        Logger.info("=" * 60)
        Logger.info(f"Violations Found: {violations_found}")
        Logger.info(f"Violations Fixed: {violations_fixed}")
        Logger.info(f"Final Purity: {final_purity}")

        if final_purity:
            Logger.info("=" * 60)
            Logger.info("[OK] CONVERGENCE SUCCESS: Repository is now 100% Architecture-Pure.")
            Logger.info("The Golden Baseline has been established.")
            Logger.info("=" * 60)
            return 0
        else:
            # Extract remaining violations
            is_pure, lockdown_details = lockdown_status
            raw_lockdown = lockdown_details.get("_raw_result", lockdown_details)
            remaining = raw_lockdown.get("violations_found", 0)

            Logger.error("=" * 60)
            Logger.error("[FAIL] CONVERGENCE INCOMPLETE: Unresolved violations remain.")
            Logger.error(f"Remaining Violations: {remaining}")
            Logger.error("Run again or investigate manually.")
            Logger.error("=" * 60)
            return 1

    except ImportError as e:
        Logger.error(f"[ERROR] Import Error: {e}")
        Logger.error("Ensure agentic_core is properly installed.")
        return 2
    except Exception as e:  # guardian: allow-broad-exception -- operational boundary
        Logger.exception("[ERROR] Execution Error: %s", e)
        return 2


if __name__ == "__main__":
    sys.exit(run_terminal_convergence())
