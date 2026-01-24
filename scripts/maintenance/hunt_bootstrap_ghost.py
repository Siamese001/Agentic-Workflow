"""
Ghost Hunter - Bootstrap Edition

Hunts for duplicate BootstrapAgent.py files that might be causing
ArchGuard false positives.
"""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
TARGET_FILE = "BootstrapAgent.py"
VALID_PATH = PROJECT_ROOT / "agentic_core/L0_maintenance/scripts/BootstrapAgent.py"


def hunt_bootstrap():
    print("--- HUNTING BOOTSTRAP GHOSTS ---")

    found_any = False

    for root, dirs, files in os.walk(PROJECT_ROOT / "agentic_core"):
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
                except Exception as e:
                    print(f" -> Failed to archive: {e}")

    if not found_any:
        print("[CLEAN] No ghosts found.")


if __name__ == "__main__":
    hunt_bootstrap()
