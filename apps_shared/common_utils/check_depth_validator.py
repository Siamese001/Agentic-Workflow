"""
Check depth violations using SSOT.
[SSOT] All depth requirements derived from SOVEREIGN_REGISTRY in structure_blueprint.py
"""

from typing import Any
from pathlib import Path


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
