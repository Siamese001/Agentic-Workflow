from __future__ import annotations

import shutil

"""Brief description of functionality and purpose."""

"Brief description of functionality and purpose."
from pathlib import Path

# [SSOT IMPORT] Structure blueprint is the single source of truth
from typing import Any

root: Any = Path("C:/Git/Agentic-Workflow/agentic_core")
quarantine: Any = Path("C:/Git/Agentic-Workflow/quarantine_syntax_errors")
broken_files: Any = [
    "L1_cognition/P1_core/rg_validation_gates_impl.py",
    "L2_execution/P2_tools/examples.py",
    "L2_execution/P4_agents/pattern_retrieval_agent.py",
    "L2_execution/P4_agents/quality.py",
    "L3_orchestration/S3_vitality/context.py",
]


def quarantine_broken() -> Any:
    """Brief description of functionality and purpose."""
    print("[*] QUARANTINE: Moving broken files to quarantine folder...")
    QUARANTINE.mkdir(exist_ok=True)
    moved: Any = 0
    for file_rel in BROKEN_FILES:
        file_path: Any = ROOT / file_rel.replace("/", "\\")
        if not file_path.exists():
            print(f"  [!] Not found: {file_rel}")
            continue
        try:
            dest: Any = QUARANTINE / file_path.name
            shutil.move(str(file_path), str(dest))
            print(f"  [✓] Quarantined: {file_rel}")
            moved += 1
        except Exception as e:
            print(f"  [X] Failed: {file_rel} - {e}")
    print(f"\n[OK] QUARANTINE COMPLETE. {moved} broken files isolated.")
    print(f"    Files moved to: {QUARANTINE}")
    print("    You can restore them later after manual fixes.")


if __name__ == "__main__":
    quarantine_broken()
