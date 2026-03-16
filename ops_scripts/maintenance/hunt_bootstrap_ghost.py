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
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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
