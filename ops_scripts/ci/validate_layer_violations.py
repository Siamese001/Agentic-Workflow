#!/usr/bin/env python3
"""Validate layer violations in Python imports.

This script analyzes Python files for layer boundary violations:
- Higher layer importing from lower layer (valid)
- Lower layer importing from higher layer (violation)

Outputs JSON format for CI integration.
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path


# Layer hierarchy (L0 lowest, L6 highest)
LAYER_ORDER = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5, "L6": 6}


def get_layer_from_path(file_path: Path) -> str | None:
    """Determine layer from file path."""
    path_str = str(file_path).lower()
    for layer in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]:
        if f"{layer.lower()}_" in path_str or f"/{layer.lower()}/" in path_str:
            return layer
    return None


def get_layer_from_import(import_path: str) -> str | None:
    """Determine layer from import path."""
    path_lower = import_path.lower()
    for layer in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]:
        if f"{layer.lower()}_" in path_lower or f".{layer.lower()}." in path_lower:
            return layer
    return None


def analyze_file(file_path: Path, repo_root: Path) -> list[dict]:
    """Analyze a single Python file for layer violations."""
    violations = []
    file_layer = get_layer_from_path(file_path)

    if not file_layer:
        return violations

    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)
    except SyntaxError:
        return violations

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                import_layer = get_layer_from_import(alias.name)
                if import_layer and LAYER_ORDER.get(import_layer, 0) > LAYER_ORDER.get(file_layer, 0):
                    violations.append({
                        "file": str(file_path),
                        "line": getattr(node, "lineno", 0),
                        "type": "layer_violation",
                        "message": f"Layer violation: {file_layer} imports from {import_layer}",
                        "import": alias.name,
                    })

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                import_layer = get_layer_from_import(node.module)
                if import_layer and LAYER_ORDER.get(import_layer, 0) > LAYER_ORDER.get(file_layer, 0):
                    violations.append({
                        "file": str(file_path),
                        "line": getattr(node, "lineno", 0),
                        "type": "layer_violation",
                        "message": f"Layer violation: {file_layer} imports from {import_layer}",
                        "import": node.module,
                    })

    return violations


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: validate_layer_violations.py <directory>", file=sys.stderr)
        return 1

    target_dir = Path(sys.argv[1])
    if not target_dir.exists():
        print(f"Directory not found: {target_dir}", file=sys.stderr)
        return 1

    repo_root = Path.cwd()
    all_violations = []

    for py_file in target_dir.rglob("*.py"):
        violations = analyze_file(py_file, repo_root)
        all_violations.extend(violations)

    # Output JSON
    output = {
        "violations": all_violations,
        "total": len(all_violations),
        "target": str(target_dir),
    }

    print(json.dumps(output, indent=2))
    return 0 if all_violations else 0


if __name__ == "__main__":
    sys.exit(main())
