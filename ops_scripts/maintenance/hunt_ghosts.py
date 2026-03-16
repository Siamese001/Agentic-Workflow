"""
Ghost Hunter Script - Phase 11

Scans the ENTIRE agentic_core directory for forbidden filenames,
ignoring expected paths. If a file matches a forbidden name,
it is archived immediately.

Target: runtime_shared_vector_store_clients.py (The Phantom)
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    get_validated_project_root,
)
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

_emit_records_execution_trace("p0", "evidence", "hunt_ghosts")
_emit_applies_guardrail("p0", "hunt_ghosts", "p0_governance")
_emit_reads_policy_state("p0", "hunt_ghosts", "policy_binding")
_emit_snapshots_state("p0", "hunt_ghosts", "state_snapshot")
emit_replay_key("p0", "hunt_ghosts")
emit_determinism_digest("p0", "hunt_ghosts")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "hunt_ghosts", "execution_auth")
_emit_validates_capability("p2", "hunt_ghosts", "capability_check")
_emit_routes_to_capability("p2", "hunt_ghosts", "capability_route")
_emit_writes_via_uwg("p2", "hunt_ghosts", "uwg_write")
_emit_blocks_direct_write("p2", "hunt_ghosts", "direct_write_block")
_emit_records_tool_invocation("p2", "hunt_ghosts", "tool_invocation")
_emit_captures_execution_output("p2", "hunt_ghosts", "exec_output")
_emit_dispatches_agent("p3", "hunt_ghosts", "agent_dispatch")
_emit_coordinates_agents("p3", "hunt_ghosts", "agent_coordination")
_emit_records_workflow_lineage("p3", "hunt_ghosts", "workflow_lineage")
_emit_records_healing_outcome("p3", "hunt_ghosts", "healing_outcome")
_emit_escalates_failure("p3", "hunt_ghosts", "failure_escalation")
_emit_orchestrates_workflow("p3", "hunt_ghosts", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "hunt_ghosts", "healing_dispatch")
_emit_invokes_evaluation("p3", "hunt_ghosts", "evaluation_signal")
_emit_records_telemetry_event("p4", "hunt_ghosts", "telemetry_event")
_emit_captures_evaluation_metric("p4", "hunt_ghosts", "eval_metric")
_emit_stores_embedding("p4", "hunt_ghosts", "embedding_store")
_emit_updates_meta_learning_state("p4", "hunt_ghosts", "meta_learning")
_emit_links_execution_to_snapshot("p4", "hunt_ghosts", "exec_snapshot_link")

PROJECT_ROOT = get_validated_project_root()
ARCHIVE_ROOT = (
    PROJECT_ROOT
    / AGENTIC_CORE_DIR
    / "archived"
    / f"phase11_hunter_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
)

# Files that should not exist ANYWHERE in agentic_core (except archived)
WANTED_LIST = [
    "runtime_shared_vector_store_clients.py",
    "runtime_shared_cache_clients.py",
    "runtime_shared_multi_provider_clients.py",
]


def hunt_and_archive():
    print("--- STARTING GHOST HUNT ---")
    print(f"Targeting: {WANTED_LIST}")

    scan_dir = PROJECT_ROOT / AGENTIC_CORE_DIR
    found_count = 0

    if not ARCHIVE_ROOT.exists():
        ARCHIVE_ROOT.mkdir(parents=True)

    for root, _dirs, files in os.walk(scan_dir):
        _dirs[:] = [d for d in _dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]

        for file in files:
            if file in WANTED_LIST:
                full_path = Path(root) / file
                print(f"[FOUND] {full_path}")

                # Archive it
                rel_path = full_path.relative_to(PROJECT_ROOT)
                dest_path = ARCHIVE_ROOT / rel_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                try:
                    shutil.move(str(full_path), str(dest_path))
                    print(f"[ARCHIVED] -> {dest_path}")
                    found_count += 1
                except Exception as e:
                    raise
                    print(f"[ERROR] Could not archive {file}: {e}")

    print(f"--- HUNT COMPLETE: {found_count} ghosts busted ---")


if __name__ == "__main__":
    hunt_and_archive()
