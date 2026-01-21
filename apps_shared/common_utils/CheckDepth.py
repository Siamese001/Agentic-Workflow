from __future__ import annotations

"""
Check depth violations using SSOT.
[SSOT] All depth requirements derived from SOVEREIGN_REGISTRY in structure_blueprint.py
"""
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.validators.structure_blueprint import SOVEREIGN_REGISTRY
from agentic_core.utils.ssot_discovery import get_python_files


def check_depth(root_dir: Path) -> None:
    """Check depth of all Python files."""
    violations = []
    required_depth: Any = SOVEREIGN_REGISTRY["agentic_core"]["depth"]
    for py_file in get_python_files(root_dir):
        rel_path: Any = py_file.relative_to(root_dir)
        depth: Any = len(rel_path.parts) - 1  # Subtract 1 because file itself is not a level
        if depth > required_depth:
            violations.append((str(rel_path), depth))
    print(f"Total violations: {len(violations)}")
    print(f"[SSOT] agentic_core required depth: {required_depth}")
    if violations:
        print("\nFirst 20 violations:")
        for path, depth in violations[:20]:
            print(f"  Depth {depth}: {path}")


root: Any = Path("c:/Git/Agentic-Workflow")
check_depth(root)
if violations:
    print("\nFirst 20 violations:")
    for path, depth in violations[:20]:
        print(f"  Depth {depth}: {path}")
