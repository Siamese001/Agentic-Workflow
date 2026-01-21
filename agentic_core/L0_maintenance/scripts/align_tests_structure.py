from __future__ import annotations

"""
TEST STRUCTURE ALIGNMENT
Ensures all test directories have __init__.py for Python package recognition.
"""
import os
from typing import Any

from agentic_core.L5_safety.validators.structure_blueprint import TESTS_L2_SUBFOLDER_MAP


def align_tests_structure(root_path: Any) -> Any:
    """Brief description of functionality and purpose."""
    print("--- ALIGNING TESTS WITH SOVEREIGN LAW ---")
    tests_root: Any = os.path.join(root_path, "tests")
    for l1, l2_list in TESTS_L2_SUBFOLDER_MAP.items():
        l1_path: Any = os.path.join(tests_root, l1)
        ensure_dir_structure(l1_path)
        for l2 in l2_list:
            l2_path: Any = os.path.join(l1_path, l2)
            ensure_dir_structure(l2_path)


def ensure_dir_structure(path: Any) -> Any:
    """Brief description of functionality and purpose."""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        print(f"✅ CREATED: {path}")
    init_file: Any = os.path.join(path, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, "w") as f:
            f.write("# Sovereign Test Module\n")
        print(f"✅ ADDED __init__.py: {path}")
    gitkeep: Any = os.path.join(path, ".gitkeep")
    if not os.path.exists(gitkeep):
        with open(gitkeep, "w") as f:
            f.write("")


if __name__ == "__main__":
    PROJECT_ROOT: Any = "C:/Git/Agentic-Workflow"
    align_tests_structure(PROJECT_ROOT)
    print("\n✅ TEST ALIGNMENT COMPLETE. Run your Gatekeeper to confirm.")
