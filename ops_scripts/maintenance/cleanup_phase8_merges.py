"""
Cleanup Script - Phase 8 Manual Merges & Ghost Busting

[PHASE 8]
1. Archives "Ghost" infrastructure files (Legacy Clients).
2. Resolves "Medium" priority duplicates by archiving the obsolete versions.
"""

import shutil
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
ARCHIVE_ROOT = (
    PROJECT_ROOT / "agentic_core" / "archived" / f"phase8_merges_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
)

# Files to ARCHIVE (The Losers of the Merge)
OBSOLETE_FILES = [
    # 1. Ghost Infrastructure (CRITICAL)
    "agentic_core/L2_execution/enforcement/runtime_shared_multi_provider_clients.py",
    "agentic_core/L2_execution/enforcement/llm_router_mcp_client.py",
    # 2. Dashboard SSOT (Keep L0, Archive L5 duplicate)
    "agentic_core/L5_safety/validators/dashboard_ssot_definitions.py",
    # 3. Intervention Server (Keep L5, Archive L3 duplicate)
    "agentic_core/L3_orchestration/reasoning/intervention_server.py",
    # 4. Constitution (Keep Config, Archive L1 duplicate)
    "agentic_core/L1_cognition/thought_engine/sovereign_domain_constitution.py",
]


def run_cleanup():
    print("--- STARTING PHASE 8 MERGE CLEANUP ---")
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

    print(f"--- PHASE 8 COMPLETE: {moved_count} files archived ---")


if __name__ == "__main__":
    run_cleanup()
