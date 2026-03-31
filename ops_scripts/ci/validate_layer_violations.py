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


# Layer hierarchy (L0 lowest, L6 highest, plus cross-cutting and top-level layers)
LAYER_ORDER = {
    # Core agentic_core layers
    "L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5, "L6": 6,
    # Cross-cutting layers within agentic_core
    "L_SHARED": 7, "L_RUNTIME": 8, "L_PG": 9,
    # Top-level package layers
    "L_SL": 10, "L_TOOLS": 11, "L_OPS": 12, "L_APP": 13, "L_TEST": 14,
}

# Layer mapping from path prefixes (synchronized with schema_util.py)
LAYER_PREFIX_MAP = {
    # Core layers
    "agentic_core/L0_routing": "L0",
    "agentic_core/L1_cognition": "L1",
    "agentic_core/L2_execution": "L2",
    "agentic_core/L3_orchestration": "L3",
    "agentic_core/L4_state": "L4",
    "agentic_core/L5_safety": "L5",
    "agentic_core/L6_observability": "L6",
    # Cross-cutting
    "agentic_core/_compat": "L_SHARED",
    "agentic_core/embeddings": "L_SHARED",
    "agentic_core/enforcement": "L_SHARED",
    "agentic_core/base_agents": "L_SHARED",
    "agentic_core/interfaces": "L_SHARED",
    "agentic_core/config": "L_SHARED",
    "agentic_core/mixins": "L_SHARED",
    "agentic_core/utils": "L_SHARED",
    "agentic_core/seams": "L_SHARED",
    "agentic_core/cache": "L_SHARED",
    "agentic_core/agents": "L_SHARED",
    "agentic_core/evaluation": "L_SHARED",
    "agentic_core/patterns": "L_SHARED",
    "agentic_core/runtime": "L_RUNTIME",
    "agentic_core/prompt_governance": "L_PG",
    "agentic_core/knowledge": "L_PG",
    "agentic_core/adg": "L_TOOLS",
    # Top-level packages
    "system_learning": "L_SL",
    "tools": "L_TOOLS",
    "ops_scripts": "L_OPS",
    "tests": "L_TEST",
    "apps_rg": "L_APP",
    "apps_lic": "L_APP",
    "apps_shared": "L_APP",
    "apps_eval": "L_APP",
    "apps_exec": "L_APP",
    "apps_research": "L_APP",
    "apps_rfp": "L_APP",
    "apps_underwriting_ai": "L_APP",
}

# Allowed layer edges (higher layer → lower layer imports are OK)
# Based on ALLOWED_LAYER_EDGES from schema_util.py
ALLOWED_EDGES = {
    # Core gravity: LN can import L0..LN-1
    ("L1", "L0"), ("L2", "L1"), ("L2", "L0"),
    ("L3", "L2"), ("L3", "L1"), ("L3", "L0"),
    ("L4", "L3"), ("L4", "L2"), ("L4", "L1"), ("L4", "L0"),
    ("L5", "L4"), ("L5", "L3"), ("L5", "L2"), ("L5", "L1"), ("L5", "L0"),
    ("L6", "L5"), ("L6", "L4"), ("L6", "L3"), ("L6", "L2"), ("L6", "L1"), ("L6", "L0"),
    # Core → Shared (all core layers can use shared utilities)
    ("L0", "L_SHARED"), ("L1", "L_SHARED"), ("L2", "L_SHARED"), ("L3", "L_SHARED"),
    ("L4", "L_SHARED"), ("L5", "L_SHARED"), ("L6", "L_SHARED"),
    # Core → Runtime
    ("L3", "L_RUNTIME"), ("L4", "L_RUNTIME"), ("L5", "L_RUNTIME"), ("L6", "L_RUNTIME"),
    ("L1", "L_RUNTIME"), ("L2", "L5"),
    # Core → PG
    ("L1", "L_PG"), ("L2", "L_PG"), ("L3", "L_PG"), ("L4", "L_PG"), ("L5", "L_PG"), ("L6", "L_PG"),
    # Core → Tools
    ("L4", "L_TOOLS"),
    # Apps → Core (apps can import any core layer)
    ("L_APP", "L6"), ("L_APP", "L5"), ("L_APP", "L4"), ("L_APP", "L3"),
    ("L_APP", "L2"), ("L_APP", "L1"), ("L_APP", "L0"),
    ("L_APP", "L_SHARED"), ("L_APP", "L_SL"),
    # SL → Core
    ("L_SL", "L2"), ("L_SL", "L1"), ("L_SL", "L0"), ("L_SL", "L_SHARED"), ("L_SL", "L5"),
    # Tools → Core
    ("L_TOOLS", "L5"), ("L_TOOLS", "L4"), ("L_TOOLS", "L3"), ("L_TOOLS", "L2"),
    ("L_TOOLS", "L1"), ("L_TOOLS", "L0"), ("L_TOOLS", "L_SHARED"), ("L_TOOLS", "L_SL"),
    # OPS → Core/Apps/SL/Runtime
    ("L_OPS", "L5"), ("L_OPS", "L4"), ("L_OPS", "L3"), ("L_OPS", "L2"),
    ("L_OPS", "L1"), ("L_OPS", "L0"), ("L_OPS", "L_SHARED"), ("L_OPS", "L_TOOLS"),
    ("L_OPS", "L_SL"), ("L_OPS", "L_APP"), ("L_OPS", "L_RUNTIME"),
    # Test → Everything (tests can import anything)
    ("L_TEST", "L0"), ("L_TEST", "L1"), ("L_TEST", "L2"), ("L_TEST", "L3"),
    ("L_TEST", "L4"), ("L_TEST", "L5"), ("L_TEST", "L6"), ("L_TEST", "L_APP"),
    ("L_TEST", "L_SL"), ("L_TEST", "L_TOOLS"), ("L_TEST", "L_OPS"),
    ("L_TEST", "L_RUNTIME"), ("L_TEST", "L_PG"), ("L_TEST", "L_SHARED"),
    # Runtime → Core (bootstrap assembly)
    ("L_RUNTIME", "L0"), ("L_RUNTIME", "L1"), ("L_RUNTIME", "L2"),
    ("L_RUNTIME", "L3"), ("L_RUNTIME", "L4"), ("L_RUNTIME", "L5"),
    ("L_RUNTIME", "L_SHARED"),
    # PG → Core/Runtime
    ("L_PG", "L0"), ("L_PG", "L1"), ("L_PG", "L2"), ("L_PG", "L_RUNTIME"), ("L_PG", "L4"),
    # Shared → Core (cross-cutting utilities)
    ("L_SHARED", "L0"), ("L_SHARED", "L_RUNTIME"), ("L_SHARED", "L5"),
    ("L_SHARED", "L2"), ("L_SHARED", "L1"), ("L_SHARED", "L_APP"),
    # Self-references (layers can import within themselves)
    ("L_SHARED", "L_SHARED"),
}


def get_layer_from_path(file_path: Path) -> str | None:
    """Determine layer from file path using LAYER_PREFIX_MAP."""
    path_str = str(file_path).replace("\\", "/")
    # Sort by longest prefix first to get most specific match
    for prefix, layer in sorted(LAYER_PREFIX_MAP.items(), key=lambda x: -len(x[0])):
        if path_str.startswith(prefix) or f"/{prefix}" in path_str:
            return layer
    return None


def get_layer_from_import(import_path: str) -> str | None:
    """Determine layer from import path using LAYER_PREFIX_MAP."""
    path_lower = import_path.replace(".", "/")
    for prefix, layer in sorted(LAYER_PREFIX_MAP.items(), key=lambda x: -len(x[0])):
        if path_lower.startswith(prefix) or f"/{prefix}" in path_lower:
            return layer
    return None


def analyze_file(file_path: Path, repo_root: Path) -> list[dict]:
    """Analyze a single Python file for layer violations."""
    violations: list[dict] = []
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
                if import_layer and import_layer != file_layer:
                    # Check if this edge is allowed
                    if (file_layer, import_layer) not in ALLOWED_EDGES:
                        violations.append({
                            "file": str(file_path),
                            "line": getattr(node, "lineno", 0),
                            "type": "layer_violation",
                            "message": f"Layer violation: {file_layer} imports from {import_layer}",
                            "import": alias.name,
                            "edge": f"{file_layer}->{import_layer}",
                        })

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                import_layer = get_layer_from_import(node.module)
                if import_layer and import_layer != file_layer:
                    # Check if this edge is allowed
                    if (file_layer, import_layer) not in ALLOWED_EDGES:
                        violations.append({
                            "file": str(file_path),
                            "line": getattr(node, "lineno", 0),
                            "type": "layer_violation",
                            "message": f"Layer violation: {file_layer} imports from {import_layer}",
                            "import": node.module,
                            "edge": f"{file_layer}->{import_layer}",
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
