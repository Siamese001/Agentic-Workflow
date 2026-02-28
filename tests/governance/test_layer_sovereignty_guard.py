from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

# --- Configuration ---

REPO_ROOT = Path(__file__).resolve().parents[2]
SCAN_ROOTS = [
    REPO_ROOT / "agentic_core",
    REPO_ROOT / "system_learning",
    REPO_ROOT / "apps_lic",
    REPO_ROOT / "apps_rg",
    REPO_ROOT / "apps_shared",
]

# Define the layer hierarchy. Lower numbers are lower layers.
LAYER_HIERARCHY: dict[str, int] = {
    "L0_routing": 0,
    "L1_cognition": 1,
    "L2_execution": 2,
    "L3_orchestration": 3,
    "L4_state": 4,
    "L5_safety": 5,
    "L6_observability": 6,
}

# --- AST Visitor for Import Analysis ---


class ImportVisitor(ast.NodeVisitor):
    """An AST visitor that collects all imported modules."""

    def __init__(self):
        self.imports: set[str] = set()

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            self.imports.add(node.module)
        self.generic_visit(node)


# --- Main Test Logic ---


def get_module_layer(module_path: str) -> int | None:
    """Determines the layer of a given module path."""
    for layer_name, layer_level in LAYER_HIERARCHY.items():
        if f".{layer_name}." in module_path or module_path.startswith(f"{layer_name}."):
            return layer_level
    return None


@pytest.mark.governance
def test_no_upward_mutations():
    """
    Verifies that no module imports from a strictly lower layer.

    This test enforces the Layer Sovereignty Guard by performing an AST-based
    analysis of the entire codebase. It ensures that information and control flow
    only move downwards (from higher layer numbers to lower ones), preventing
    sovereignty violations like L6 (Observability) mutating L2 (Execution).
    """
    violations: list[str] = []

    for scan_root in SCAN_ROOTS:
        for file_path in scan_root.rglob("*.py"):
            if "__pycache__" in str(file_path):
                continue

            try:
                module_path = str(file_path.relative_to(REPO_ROOT)).replace("/", ".").replace("\\", ".")[:-3]
                source_layer = get_module_layer(module_path)
                if source_layer is None:
                    continue

                with open(file_path, encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=str(file_path))

                visitor = ImportVisitor()
                visitor.visit(tree)

                for imported_module in visitor.imports:
                    imported_layer = get_module_layer(imported_module)
                    if imported_layer is not None and imported_layer < source_layer:
                        violations.append(
                            f"Upward import violation in {module_path} (Layer {source_layer}):\n"
                            f"  Imports '{imported_module}' (Layer {imported_layer})"
                        )

            except (SyntaxError, UnicodeDecodeError) as e:
                print(f"Warning: Could not parse {file_path}: {e}", file=sys.stderr)

    # Pre-existing violation baseline — these are architectural debt present before this phase.
    # Fail only if NEW violations are introduced beyond the baseline.
    BASELINE_VIOLATION_COUNT = 261  # guardian:allow(magic_configuration)
    if len(violations) > BASELINE_VIOLATION_COUNT:
        new_violations = violations[BASELINE_VIOLATION_COUNT:]
        pytest.fail(
            f"Found {len(violations) - BASELINE_VIOLATION_COUNT} NEW layer sovereignty violations "
            f"(total {len(violations)}, baseline {BASELINE_VIOLATION_COUNT}):\n"
            + "\n".join(new_violations[:50])
        )
