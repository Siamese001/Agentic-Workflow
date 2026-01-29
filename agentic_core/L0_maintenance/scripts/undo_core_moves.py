from __future__ import annotations

"""
Undo all the incorrect core/ subdirectory moves
"""
import shutil
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
)


def undo_core_moves() -> Any:
    """Move all files back from */core/ to parent directories"""
    root: Any = Path(".")
    directories: Any = [
        AGENTIC_CORE_DIR,
        APPS_LIC_DIR,
        APPS_RG_DIR,
        APPS_SHARED_DIR,
        "config",
        "observability",
        "schemas",
        SCRIPTS_DIR,
        "tools",
        "validator",
        "prompt_governance",
    ]
    moved_count: Any = 0
    for dir_name in directories:
        core_path: Any = root / dir_name / "core"
        if not core_path.exists():
            continue
        # Phase 6.9 Sub-50: Use ssot_discovery instead of glob
        from agentic_core.utils.ssot_discovery import get_python_files

        for py_file in get_python_files(core_path):
            if py_file.name == "__init__.py":
                continue
            target: Any = core_path.parent / py_file.name
            if target.exists():
                print(f"Skipping {py_file} (target exists)")
                continue
            print(f"Moving {py_file} -> {dir_name}/{py_file.name}")
            shutil.move(str(py_file), str(target))
            moved_count += 1
        try:
            core_path.rmdir()
            print(f"Removed {dir_name}/core/")
        except:
            pass
    print(f"\nTotal files moved back: {moved_count}")


if __name__ == "__main__":
    undo_core_moves()
