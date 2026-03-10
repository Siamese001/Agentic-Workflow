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
                    print(f"[ERROR] Could not archive {file}: {e}")

    print(f"--- HUNT COMPLETE: {found_count} ghosts busted ---")


if __name__ == "__main__":
    hunt_and_archive()
