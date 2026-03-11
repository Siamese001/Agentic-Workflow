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
Fix tunnel violations by flattening to SSOT-compliant depth.
[SSOT] All depth requirements derived from SOVEREIGN_REGISTRY in structure_blueprint.py
"""
import os
import shutil
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.L0_routing.config.path_constants import DEPTH_RULES, SOVEREIGN_EXCLUDED_FOLDERS
from agentic_core.L0_routing.utils.ssot_discovery_util import get_python_files

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
)

ROOT: Any = Path(__file__).parent.parent.parent.parent
CORE: Any = ROOT / AGENTIC_CORE_DIR
REQUIRED_DEPTH: Any = DEPTH_RULES.get("agentic_core", 4)


def fix_tunnel_violations() -> Any:
    """Moves files from deep tunnels up to proper SSOT-compliant depth structure."""
    print(f"[*] FIXING ALL TUNNEL VIOLATIONS (target depth: {REQUIRED_DEPTH})...")
    fixed: Any = 0
    all_py = get_python_files(ROOT)
    for py_file in [f for f in all_py if str(f).startswith(str(CORE))]:
        if py_file.name == "__init__.py":
            continue
        parts: Any = py_file.relative_to(CORE).parts
        if len(parts) > REQUIRED_DEPTH - 1:
            layer: Any = parts[0]
            stage: Any = parts[1]
            filename: Any = py_file.name
            target_dir: Any = CORE / layer / stage
            target_file: Any = target_dir / filename
            if target_file.exists():
                prefix: Any = parts[2]
                target_file: Any = target_dir / f"{prefix}_{filename}"
            try:
                target_dir.mkdir(parents=True, exist_ok=True)
                assert_no_persistent_write("L0", "shutil.mutate")  # G-12-1: mutation prohibition guard
                shutil.move(str(py_file), str(target_file))
                print(f"  [✓] Flattened: {py_file.relative_to(CORE)} -> {target_file.relative_to(CORE)}")
                fixed += 1
            # guardian: allow-silent-swallow
            except Exception as e:
                print(f"  [!] Failed to move {py_file.name}: {e}")
    print(f"\n[OK] TUNNEL FIX COMPLETE. {fixed} files moved to proper depth.")
    print("\n[*] CLEANING UP EMPTY DIRECTORIES...")
    cleaned: Any = 0
    for root, dirs, _files in os.walk(CORE, topdown=False):
        dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
        for name in dirs:
            dir_path: Any = Path(root) / name
            try:
                if not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    print(f"  [✓] Removed empty: {dir_path.relative_to(CORE)}")
                    cleaned += 1
            # guardian: allow-silent-swallow
            except:
                pass
    print(f"\n[OK] CLEANUP COMPLETE. {cleaned} empty directories removed.")


if __name__ == "__main__":
    fix_tunnel_violations()
