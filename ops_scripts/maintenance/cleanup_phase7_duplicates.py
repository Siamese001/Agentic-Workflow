"""
Cleanup Script - Phase 7 Duplicate Removal
Archives 11 critical duplicate files identified in DUPLICATE_FILES_REPORT.md
"""

import shutil
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
ARCHIVE_ROOT = (
    PROJECT_ROOT
    / "agentic_core"
    / "archived"
    / f"phase7_dupes_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
)

DUPLICATE_FILES = [
    "agentic_core/L5_safety/guardrails/CognitiveBatchProcessor.py",
    "agentic_core/L5_safety/guardrails/TieredBatchProcessor.py",
    "agentic_core/L1_cognition/thought_engine/structured_engine.py",
    "agentic_core/L0_maintenance/scripts/maintenance",
    "agentic_core/L0_maintenance/scripts/security/gatekeeper_lock.py",
]


def run_cleanup():
    print("--- STARTING PHASE 7 CLEANUP ---")
    if not ARCHIVE_ROOT.exists():
        ARCHIVE_ROOT.mkdir(parents=True)
    moved_count = 0
    for file_rel_path in DUPLICATE_FILES:
        src_path = PROJECT_ROOT / file_rel_path
        if src_path.exists():
            dest_path = ARCHIVE_ROOT / file_rel_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.move(str(src_path), str(dest_path))
                print(f"[MOVED]  {file_rel_path}")
                moved_count += 1
            except Exception as e:
                print(f"[ERROR] {file_rel_path}: {e}")
        else:
            print(f"[SKIP]   Not found: {file_rel_path}")
    print(f"--- CLEANUP COMPLETE (Archived: {moved_count}) ---")


if __name__ == "__main__":
    run_cleanup()
