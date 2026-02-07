"""
Refactor Script - Phase 7 Rename & Shim
Renames 4 ambiguous files and creates backward-compatible shims
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent

RENAME_MAP = {
    "agentic_core/L1_cognition/thought_engine/consensus.py": "supreme_court.py",
    "agentic_core/L1_cognition/thought_engine/execution.py": "execution_types.py",
    "agentic_core/L2_execution/reasoning/execution.py": "subprocess_executor.py",
    "agentic_core/L4_state/memory/context.py": "omni_context.py",
}


def create_shim(shim_path: Path, new_module_name: str):
    shim_content = f"""# [PHASE 7 MIGRATION SHIM]
import warnings
from .{new_module_name} import *
warnings.warn("Deprecated. Import from '{new_module_name}' instead.", DeprecationWarning, stacklevel=2)
"""
    with open(shim_path, "w", encoding="utf-8") as f:
        f.write(shim_content.strip())


def run_refactor():
    print("--- STARTING PHASE 7 REFACTOR ---")
    success_count = 0
    for old_rel_path, new_filename in RENAME_MAP.items():
        old_path = PROJECT_ROOT / old_rel_path
        if not old_path.exists():
            print(f"[SKIP] Source not found: {old_rel_path}")
            continue
        new_path = old_path.parent / new_filename
        new_module_name = new_filename.replace(".py", "")
        try:
            with open(old_path, encoding="utf-8") as f:
                content = f.read()
            with open(new_path, "w", encoding="utf-8") as f:
                f.write(content)
            create_shim(old_path, new_module_name)
            print(f"[SHIMMED] {old_path.name} -> {new_module_name}")
            success_count += 1
        except Exception as e:
            print(f"[ERROR] {old_rel_path}: {e}")
    print(f"--- REFACTOR COMPLETE (Processed: {success_count}) ---")


if __name__ == "__main__":
    run_refactor()
