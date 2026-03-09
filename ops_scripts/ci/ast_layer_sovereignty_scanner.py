"""
AST Layer Sovereignty Scanner — CI enforcement for cross-layer import restrictions.

Enforces that no layer imports upward (higher layers importing from lower-numbered
layers is fine; lower layers importing from higher is a violation):

  L1 must NOT import L2, L3, L4, L5, L6
  L2 must NOT import L5, L6
  L3 must NOT import L5, L6
  apps_* must NOT import directly from agentic_core.L* layers

Exit codes:
  0 — no violations
  1 — one or more violations found

Phase 1.2: Mathematically-Sealed Sovereignty Hardening
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    TESTS_DIR,
    get_validated_project_root,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)

# ---------------------------------------------------------------------------
# Layer inversion rules: {source_layer: (forbidden_target_layers, ...)}
# ---------------------------------------------------------------------------

_LAYER_RULES: dict[str, tuple[str, ...]] = {
    "agentic_core.L0_routing": (
        "agentic_core.L1_cognition",
        "agentic_core.L2_execution",
        "agentic_core.L3_orchestration",
        "agentic_core.L4_state",
        "agentic_core.L5_safety",
        "agentic_core.L6_observability",
    ),
    "agentic_core.L1_cognition": (
        "agentic_core.L2_execution",
        "agentic_core.L3_orchestration",
        "agentic_core.L4_state",
        "agentic_core.L5_safety",
        "agentic_core.L6_observability",
    ),
    "agentic_core.L2_execution": ("agentic_core.L5_safety", "agentic_core.L6_observability"),
    "agentic_core.L3_orchestration": ("agentic_core.L5_safety", "agentic_core.L6_observability"),
}

# apps_* must not directly import any agentic_core.L* layer
_APPS_PREFIXES = (APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR)
_L_LAYER_PREFIX = AGENTIC_CORE_DIR + ".L"

_EXCLUDE_DIRS = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS


def _layer_prefix_of(file_path: Path) -> str | None:
    """Return the dotted module prefix for *file_path*, or None if not in a layer."""
    parts = file_path.as_posix().split("/")
    for i, part in enumerate(parts):
        if part.startswith("agentic_core") and i + 1 < len(parts):
            next_part = parts[i + 1]
            if next_part.startswith("L") and next_part[1:2].isdigit():
                return f"agentic_core.{next_part}"
    # Check apps_*
    for app_prefix in _APPS_PREFIXES:
        if any(p == app_prefix for p in parts):
            return app_prefix
    return None


def _extract_imported_modules(tree: ast.AST) -> list[tuple[int, str]]:
    """Return list of (lineno, module_name) from all import statements."""
    result: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                result.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                result.append((node.lineno, node.module))
    return result


def scan_file(file_path: Path) -> list[str]:
    """Return list of violation strings for *file_path*."""
    violations: list[str] = []

    try:
        source = file_path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(file_path))
    except SyntaxError as exc:
        return [f"PARSE_ERROR {file_path}:{exc.lineno}: {exc.msg}"]

    source_layer = _layer_prefix_of(file_path)
    if source_layer is None:
        return []

    imports = _extract_imported_modules(tree)

    # Check layer inversion for agentic_core layers
    if source_layer in _LAYER_RULES:
        forbidden = _LAYER_RULES[source_layer]
        for lineno, mod in imports:
            for forbidden_prefix in forbidden:
                if mod == forbidden_prefix or mod.startswith(forbidden_prefix + "."):
                    violations.append(
                        f"VIOLATION {file_path}:{lineno}: layer inversion — {source_layer} imports {mod}"
                    )

    # Check apps_* direct L* imports
    if any(source_layer == ap for ap in _APPS_PREFIXES):
        for lineno, mod in imports:
            if mod.startswith(_L_LAYER_PREFIX):
                violations.append(
                    f"VIOLATION {file_path}:{lineno}: "
                    f"apps_* direct L* import — {source_layer} imports {mod} "
                    f"(use agentic_core.interfaces shims)"
                )

    return violations


def main(argv: list[str] | None = None) -> int:
    repo_root = get_validated_project_root()
    all_violations: list[str] = []
    files_scanned = 0

    scan_roots = (
        list(repo_root.glob(AGENTIC_CORE_DIR + "/L*"))
        + list(repo_root.glob(APPS_LIC_DIR))
        + list(repo_root.glob(APPS_RG_DIR))
        + list(repo_root.glob(APPS_SHARED_DIR))
    )

    for root in scan_roots:
        if not root.is_dir():
            continue
        for py_file in sorted(root.rglob("*.py")):
            if any(part in _EXCLUDE_DIRS for part in py_file.parts):
                continue
            files_scanned += 1
            all_violations.extend(scan_file(py_file))

    if all_violations:
        print("FAIL: Layer sovereignty violations detected:")
        for v in all_violations:
            print(f"  {v}")
        return 1

    print(f"OK: ast_layer_sovereignty_scanner passed ({files_scanned} files scanned, 0 violations)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
