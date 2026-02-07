"""
Cleanup Script - Phase 4 & 5 Sprawl Reduction

[PHASE 6] Moves obsolete files identified in Infrastructure Report to 'archived/'.
This is critical to preventing accidental usage of deprecated legacy code.
"""

import shutil
from datetime import datetime
from pathlib import Path

# Define project root (assuming script is in scripts/maintenance/)
PROJECT_ROOT = Path(__file__).parent.parent.parent
ARCHIVE_ROOT = (
    PROJECT_ROOT
    / "agentic_core"
    / "archived"
    / f"phase4_5_cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
)

# List of files identified in INFRASTRUCTURE_SPRAWL_REPORT_PHASE4.md
OBSOLETE_FILES = [
    # --- Phase 4: LLM/Embedding ---
    "agentic_core/L1_cognition/thought_engine/llm_engine.py",
    "agentic_core/L2_execution/enforcement/inference_engine.py",
    "agentic_core/L2_execution/unified/ModelRouterAgent.py",
    "agentic_core/L2_execution/reasoning/format_llm_prompt.py",
    "agentic_core/semantic_memory/embeddings/gemini_embedder.py",
    "agentic_core/semantic_memory/embeddings/core_embedder.py",
    # --- Phase 5: Healing ---
    "agentic_core/L5_safety/validators/healing_strategies.py",
    "agentic_core/L5_safety/validators/healing_healing_strategies.py",  # The duplicate
    "agentic_core/L4_state/enforcement/healing_transaction_manager.py",
    # --- Phase 5: Validators ---
    "agentic_core/L5_safety/unified/CodeValidatorAgent.py",
    "agentic_core/L5_safety/unified/CodeValidatorAgent.py",  # Duplicate
    "agentic_core/L5_safety/unified/StructuralValidatorAgent.py",
    "agentic_core/L5_safety/unified/StructureValidatorAgent.py",  # Duplicate
    # --- Config Duplicates ---
    "agentic_core/config/environments/sovereign_config.py",
    "agentic_core/config/blueprint_sovereign/sovereign_config.py",
]


def run_cleanup():
    print("--- STARTING PHASE 4/5 CLEANUP ---")
    print(f"Target Archive: {ARCHIVE_ROOT}")

    if not ARCHIVE_ROOT.exists():
        ARCHIVE_ROOT.mkdir(parents=True)
        print("Created archive directory.")

    moved_count = 0
    missing_count = 0

    for file_rel_path in OBSOLETE_FILES:
        src_path = PROJECT_ROOT / file_rel_path

        if src_path.exists():
            # Prepare destination
            dest_path = ARCHIVE_ROOT / file_rel_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            try:
                shutil.move(str(src_path), str(dest_path))
                print(f"[MOVED]  {file_rel_path}")
                moved_count += 1
            except Exception as e:
                print(f"[ERROR]  Could not move {file_rel_path}: {e}")
        else:
            print(f"[SKIP]   File not found: {file_rel_path}")
            missing_count += 1

    print("--- CLEANUP COMPLETE ---")
    print(f"Files Moved: {moved_count}")
    print(f"Files Missing/Already Moved: {missing_count}")


if __name__ == "__main__":
    run_cleanup()
