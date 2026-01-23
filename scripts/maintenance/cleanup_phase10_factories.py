"""
Cleanup Script - Phase 10 Factory Removal

[PHASE 10]
Archives the final legacy infrastructure files:
1. runtime_shared_cache_clients.py (Legacy Redis Factory)
2. runtime_shared_vector_store_clients.py (Legacy Pinecone Factory)
"""

import shutil
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
ARCHIVE_ROOT = (
    PROJECT_ROOT
    / "agentic_core"
    / "archived"
    / f"phase10_factories_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
)

OBSOLETE_FILES = [
    "agentic_core/L2_execution/mcp/runtime_shared_cache_clients.py",
    "agentic_core/L2_execution/mcp/runtime_shared_vector_store_clients.py",
]


def run_cleanup():
    print("--- STARTING PHASE 10 FACTORY CLEANUP ---")
    if not ARCHIVE_ROOT.exists():
        ARCHIVE_ROOT.mkdir(parents=True)

    moved_count = 0
    for file_rel_path in OBSOLETE_FILES:
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

    print(f"--- PHASE 10 COMPLETE: {moved_count} files archived ---")


if __name__ == "__main__":
    run_cleanup()
