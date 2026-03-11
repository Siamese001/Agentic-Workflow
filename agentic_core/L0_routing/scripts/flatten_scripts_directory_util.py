from __future__ import annotations

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""
Flatten scripts directory to SSOT-compliant depth.
[SSOT] All depth requirements derived from SOVEREIGN_REGISTRY in structure_blueprint.py
"""
import os
import shutil
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
)
from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.L0_routing.utils.path_util import (
    safe_prefixed_filename,
    validate_no_duplicate_prefix,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS
from agentic_core.L5_safety.config.structure_blueprint_config import DEPTH_RULES

root: Any = Path("C:/Git/Agentic-Workflow")
core: Any = ROOT / AGENTIC_CORE_DIR
scripts_dir: Any = CORE / "L0_routing/scripts"
required_depth: Any = DEPTH_RULES.get("agentic_core", 4)


def flatten_scripts() -> Any:
    """Brief description of functionality and purpose."""
    print(f"[*] FLATTENING L0_routing/scripts TO DEPTH-{REQUIRED_DEPTH}...")
    moved: Any = 0
    if not SCRIPTS_DIR.exists():
        print("[!] Scripts directory not found")
        return
    # Phase 6.9: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery_validator import get_python_files

    for py_file in get_python_files(SCRIPTS_DIR):
        rel_path: Any = py_file.relative_to(CORE)
        parts: Any = rel_path.parts
        if len(parts) > REQUIRED_DEPTH - 1:
            path_prefix: Any = "_".join(parts[2:-1])
            # [SAFEGUARD] Use SSOT function to prevent duplicate prefix sprawl
            new_name: Any = safe_prefixed_filename(path_prefix, py_file.name)

            # Validate no duplicate prefix was created
            has_dup, dup_msg = validate_no_duplicate_prefix(new_name)
            if has_dup:
                print(f"  [!] BLOCKED: {dup_msg}")
                continue

            target: Any = SCRIPTS_DIR / new_name
            counter: Any = 1
            while target.exists():
                target: Any = SCRIPTS_DIR / f"{path_prefix}_{counter}_{py_file.stem}{py_file.suffix}"
                counter += 1
            try:
                assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
                shutil.move(str(py_file), str(target))
                print(f"  [✓] {rel_path} -> {target.relative_to(CORE)}")
                moved += 1
            # guardian: allow-silent-swallow
            except Exception as e:
                print(f"  [X] Failed: {py_file.name} - {e}")
    print("\n[*] Cleaning empty directories...")
    for root, dirs, _files in os.walk(SCRIPTS_DIR, topdown=False):
        dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
        for dir_name in dirs:
            dir_path: Any = Path(root) / dir_name
            try:
                if not any(dir_path.iterdir()) and dir_path != SCRIPTS_DIR:
                    dir_path.rmdir()
                    print(f"  [✓] Removed: {dir_path.relative_to(CORE)}")
            # guardian: allow-silent-swallow
            except:
                pass
    print(f"\n[OK] FLATTENING COMPLETE. {moved} files moved to depth-{REQUIRED_DEPTH}.")


if __name__ == "__main__":
    flatten_scripts()
