from __future__ import annotations

"""Brief description of functionality and purpose."""

"Brief description of functionality and purpose."
import re
from pathlib import Path

# [SSOT IMPORT] Structure blueprint is the single source of truth
from typing import Any

root: Any = Path("C:/Git/Agentic-Workflow")


def undo_gravity_comments(file_path: Path) -> Any:
    """Remove gravity fix comments and restore original imports."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content: Any = f.read()
        content: Any = re.sub("# GRAVITY FIX:.*?\\n# ", "", content)
        content: Any = re.sub("# GRAVITY FIX:.*?\\n", "", content)
        lines: Any = content.split("\n")
        new_lines: Any = []
        for line in lines:
            if line.strip().startswith("# from ") or line.strip().startswith("# import "):
                new_lines.append(line.replace("# ", "", 1))
            else:
                new_lines.append(line)
        content: Any = "\n".join(new_lines)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"  [!] Error: {e}")
        return False


def undo_all_comments() -> Any:
    """Brief description of functionality and purpose."""
    print("[*] UNDOING GRAVITY FIX COMMENTS...")
    files_to_fix: Any = [
        "agentic_core/L1_cognition/agent_logic.py",
        "agentic_core/L3_orchestration/mission_runner.py",
        "agentic_core/L2_execution/P4_agents/analysis.py",
        "apps_shared/verify_hardening.py",
        "scripts/validation/dry_run_signal_failure_test.py",
        "scripts/validation/test_l5_infrastructure.py",
        "scripts/workflow/dry_run_l5_verification.py",
    ]
    count: Any = 0
    for file_rel in files_to_fix:
        file_path: Any = ROOT / file_rel
        if file_path.exists():
            if undo_gravity_comments(file_path):
                print(f"  ✓ Restored: {file_rel}")
                count += 1
    print(f"\n[OK] Restored {count} files")


if __name__ == "__main__":
    undo_all_comments()
