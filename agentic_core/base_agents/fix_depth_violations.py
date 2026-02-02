from __future__ import annotations

"""
Fix depth violations by moving shallow files into proper stage subdirectories.
Files at Layer/file.py need to move to Layer/Stage/file.py
"""
import shutil

# [SSOT IMPORT] Structure blueprint is the single source of truth
from typing import Any

from agentic_core.L5_safety.validators.structure_blueprint_config import (
    get_validated_project_root,
    safe_path_join,
)
from agentic_core.utils.ssot_discovery_validator import get_python_files

# FILESYSTEM COMPLIANCE: Use safe_path_join for all file operations
PROJECT_ROOT = get_validated_project_root()
CORE = safe_path_join(PROJECT_ROOT, "agentic_core")
STAGE_MAPPINGS: Any = {
    "L1_cognition": "P1_core",
    "L2_execution": "P1_core",
    "L3_orchestration": "P1_core",
    "L4_state": "P1_core",
    "L5_safety": "P1_core",
    "memory": "P1_core",
    "patterns": "P1_core",
    "runtime": "P1_core",
    "utils": "P1_core",
}


def fix_depth_violations() -> Any:
    """Move shallow files into proper stage subdirectories."""
    print("[*] FIXING DEPTH VIOLATIONS...")
    moved: Any = 0
    for layer_name, default_stage in STAGE_MAPPINGS.items():
        layer_path: Any = CORE / layer_name
        if not layer_path.exists():
            continue
        all_py = get_python_files(PROJECT_ROOT)
        layer_files = [
            f for f in all_py if str(f).startswith(str(layer_path)) and f.parent == layer_path
        ]
        for py_file in layer_files:
            if py_file.name == "__init__.py":
                continue
            stage_path: Any = layer_path / default_stage
            stage_path.mkdir(exist_ok=True)
            stage_init: Any = stage_path / "__init__.py"
            if not stage_init.exists():
                stage_init.write_text('"""Stage module."""\n')
            target: Any = stage_path / py_file.name
            if not target.exists():
                shutil.move(str(py_file), str(target))
                print(f"  [✓] Moved: {py_file.relative_to(CORE)} -> {target.relative_to(CORE)}")
                moved += 1
            else:
                print(f"  [SKIP] Already exists: {target.relative_to(CORE)}")
    print(f"\n[OK] Moved {moved} files to proper depth")
    return moved


if __name__ == "__main__":
    fix_depth_violations()
    print("\n[!] NEXT: Run 'python sovereign_lock.py' to verify compliance")
