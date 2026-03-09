"""
Ghost Hunter - Bootstrap Edition

Hunts for duplicate BootstrapAgent.py files that might be causing
ArchGuard false positives.
"""

import os
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR, get_validated_project_root

PROJECT_ROOT = get_validated_project_root()
TARGET_FILE = "BootstrapAgent.py"
VALID_PATH = PROJECT_ROOT / AGENTIC_CORE_DIR / "L0_routing/scripts/BootstrapAgent.py"


def hunt_bootstrap():
    print("--- HUNTING BOOTSTRAP GHOSTS ---")

    found_any = False

    for root, _dirs, files in os.walk(PROJECT_ROOT / AGENTIC_CORE_DIR):
        if "archived" in root:
            continue

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
                    print(f" -> Failed to archive: {e}")

    if not found_any:
        print("[CLEAN] No ghosts found.")


if __name__ == "__main__":
    hunt_bootstrap()
