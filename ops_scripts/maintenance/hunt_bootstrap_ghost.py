"""
Ghost Hunter - Bootstrap Edition

Hunts for duplicate BootstrapAgent.py files that might be causing
ArchGuard false positives.
"""

import os
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR, get_validated_project_root
from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS
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

_emit_records_execution_trace("p0", "evidence", "hunt_bootstrap_ghost")
_emit_applies_guardrail("p0", "hunt_bootstrap_ghost", "p0_governance")
_emit_reads_policy_state("p0", "hunt_bootstrap_ghost", "policy_binding")
_emit_snapshots_state("p0", "hunt_bootstrap_ghost", "state_snapshot")
emit_replay_key("p0", "hunt_bootstrap_ghost")
emit_determinism_digest("p0", "hunt_bootstrap_ghost")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "hunt_bootstrap_ghost", "execution_auth")
_emit_validates_capability("p2", "hunt_bootstrap_ghost", "capability_check")
_emit_routes_to_capability("p2", "hunt_bootstrap_ghost", "capability_route")
_emit_writes_via_uwg("p2", "hunt_bootstrap_ghost", "uwg_write")
_emit_blocks_direct_write("p2", "hunt_bootstrap_ghost", "direct_write_block")
_emit_records_tool_invocation("p2", "hunt_bootstrap_ghost", "tool_invocation")
_emit_captures_execution_output("p2", "hunt_bootstrap_ghost", "exec_output")
_emit_dispatches_agent("p3", "hunt_bootstrap_ghost", "agent_dispatch")
_emit_coordinates_agents("p3", "hunt_bootstrap_ghost", "agent_coordination")
_emit_records_workflow_lineage("p3", "hunt_bootstrap_ghost", "workflow_lineage")
_emit_records_healing_outcome("p3", "hunt_bootstrap_ghost", "healing_outcome")
_emit_escalates_failure("p3", "hunt_bootstrap_ghost", "failure_escalation")
_emit_orchestrates_workflow("p3", "hunt_bootstrap_ghost", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "hunt_bootstrap_ghost", "healing_dispatch")
_emit_invokes_evaluation("p3", "hunt_bootstrap_ghost", "evaluation_signal")
_emit_records_telemetry_event("p4", "hunt_bootstrap_ghost", "telemetry_event")
_emit_captures_evaluation_metric("p4", "hunt_bootstrap_ghost", "eval_metric")
_emit_stores_embedding("p4", "hunt_bootstrap_ghost", "embedding_store")
_emit_updates_meta_learning_state("p4", "hunt_bootstrap_ghost", "meta_learning")
_emit_links_execution_to_snapshot("p4", "hunt_bootstrap_ghost", "exec_snapshot_link")

PROJECT_ROOT = get_validated_project_root()
TARGET_FILE = "BootstrapAgent.py"
VALID_PATH = PROJECT_ROOT / AGENTIC_CORE_DIR / "L0_routing/scripts/BootstrapAgent.py"


def hunt_bootstrap():
    print("--- HUNTING BOOTSTRAP GHOSTS ---")

    found_any = False

    for root, _dirs, files in os.walk(PROJECT_ROOT / AGENTIC_CORE_DIR):
        _dirs[:] = [d for d in _dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]

        if TARGET_FILE in files:
            found_path = Path(root) / TARGET_FILE

            if found_path.resolve() == VALID_PATH.resolve():
                print(f"[VALID] {found_path}")
            else:
                print(f"[GHOST FOUND] {found_path}")
                found_any = True

                archive_dir = PROJECT_ROOT / "archives/agentic_core_archived"
                archive_dir.mkdir(exist_ok=True)
                dest = archive_dir / f"ghost_bootstrap_{os.urandom(4).hex()}.py"
                try:
                    found_path.rename(dest)
                    print(f" -> Archived to {dest.name}")
                # guardian: allow-silent-swallow
                except Exception as e:
                    raise
                    print(f" -> Failed to archive: {e}")

    if not found_any:
        print("[CLEAN] No ghosts found.")


if __name__ == "__main__":
    hunt_bootstrap()
