"""
Check depth violations using SSOT.
[SSOT] All depth requirements derived from SOVEREIGN_REGISTRY in structure_blueprint.py
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

SOVEREIGN_REGISTRY: dict[str, Any] = {
    "agentic_core": {"depth": 8},
}


def get_python_files(root_dir: Path) -> list[Path]:
    """Get all Python files in directory."""
    return list(root_dir.rglob("*.py"))


def check_depth(root_dir: Path) -> list[tuple[str, int]]:
    """Check depth of all Python files."""
    violations = []
    required_depth: Any = SOVEREIGN_REGISTRY["agentic_core"]["depth"]
    for py_file in get_python_files(root_dir):
        rel_path: Any = py_file.relative_to(root_dir)
        depth: Any = len(rel_path.parts) - 1
        if depth > required_depth:
            violations.append((str(rel_path), depth))
    return violations
