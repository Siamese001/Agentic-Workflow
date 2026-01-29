"""
Cleanup Script - Phase 8 Ghost Removal

[PHASE 8] Archives "Ghost" files that survived Phase 7.
These are legacy infrastructure files that bypass the new Gateways.
"""

import shutil
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
ARCHIVE_ROOT = (
    PROJECT_ROOT
    / "agentic_core"
    / "archived"
    / f"phase8_ghosts_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
)

GHOST_FILES = [
    # The Legacy Client Factory (Critical Sprawl)
    "agentic_core/L2_execution/mcp/runtime_shared_multi_provider_clients.py",
    # Deprecated router
    "agentic_core/L2_execution/mcp/llm_router_mcp_client.py",
    # Any leftovers from Phase 7 investigation if you want to be aggressive:
    # "agentic_core/L0_maintenance/scripts/dashboard_ssot_definitions.py"
]


def run_cleanup():
    print("--- STARTING PHASE 8 GHOST CLEANUP ---")
    if not ARCHIVE_ROOT.exists():
        ARCHIVE_ROOT.mkdir(parents=True)

    moved_count = 0
    for file_rel_path in GHOST_FILES:
        src_path = PROJECT_ROOT / file_rel_path
        if src_path.exists():
            dest_path = ARCHIVE_ROOT / file_rel_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.move(str(src_path), str(dest_path))
                print(f"[ARCHIVED] {file_rel_path}")
                moved_count += 1
            except Exception as e:
                print(f"[ERROR] {file_rel_path}: {e}")
        else:
            print(f"[GONE] {file_rel_path}")

    print(f"--- GHOSTS BUSTED: {moved_count} ---")


if __name__ == "__main__":
    run_cleanup()
