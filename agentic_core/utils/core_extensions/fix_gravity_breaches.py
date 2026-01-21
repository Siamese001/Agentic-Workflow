from __future__ import annotations

"""
Fix gravity breaches caused by force_app_depth.py moving app-specific code to core.
Move app-specific orchestrators and engines back to their respective apps.
"""
import shutil
from pathlib import Path

# [SSOT IMPORT] Structure blueprint is the single source of truth
from typing import Any

root: Any = Path("C:/Git/Agentic-Workflow")
core: Any = ROOT / "agentic_core"
moves_back: Any = [
    (
        CORE / "L3_orchestration/P1_core/l5_autonomous_orchestrator.py",
        ROOT / "apps_rg/L3_orchestration",
    ),
    (CORE / "L3_orchestration/P1_core/l5_orchestrator", ROOT / "apps_rg/L3_orchestration"),
    (CORE / "L2_execution/P3_engines/outreach_engine", ROOT / "apps_lic/engines"),
    (CORE / "L2_execution/P3_engines/resume_engine", ROOT / "apps_rg/engines"),
]


def fix_gravity() -> Any:
    """Brief description of functionality and purpose."""
    print("[*] FIXING GRAVITY BREACHES...")
    fixed: Any = 0
    for src, dest_dir in MOVES_BACK:
        if not src.exists():
            print(f"  [SKIP] {src.name} - doesn't exist")
            continue
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest: Any = dest_dir / src.name
        if dest.exists():
            if dest.is_dir():
                shutil.rmtree(str(dest))
            else:
                dest.unlink()
        shutil.move(str(src), str(dest))
        print(f"  [✓] Moved: {src.relative_to(CORE)} -> {dest.relative_to(ROOT)}")
        fixed += 1
    print(f"\n[OK] Fixed {fixed} gravity breaches")


if __name__ == "__main__":
    fix_gravity()
