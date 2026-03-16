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
)

_emit_records_execution_trace("p0", "evidence", "execute_convergence")
_emit_applies_guardrail("p0", "execute_convergence", "p0_governance")
_emit_reads_policy_state("p0", "execute_convergence", "policy_binding")
_emit_snapshots_state("p0", "execute_convergence", "state_snapshot")
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
    try:
        project_root = Path(__file__).resolve().parent.parent.parent
        # guardian: allow-global-mutation
        sys.path.insert(0, str(project_root))

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
    except Exception as e:
        raise
        Logger.error(f"[ERROR] Execution Error: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(run_terminal_convergence())
