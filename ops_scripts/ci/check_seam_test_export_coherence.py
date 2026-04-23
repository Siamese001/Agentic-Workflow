#!/usr/bin/env python3
"""Gate G2 — seam-test export coherence (plan W2.5).

Detects seam tests that assert package exports which do not exist in the
target package's `__init__.py`. When `pytest.importorskip(...)` masks
missing modules, these tests silently pass, hiding broken APIs.

Example caught today:
    tests/unit/agentic_core/L0_routing/seams/test_c0_context_retriever_adg.py
    asserts `C0ContextRetrieverAdg` / `validate_c0_context_retriever_adg`
    on agentic_core — neither exists.

Tier: B (blocking).

Heuristic:
    For each file under tests/**/seams/*.py, walk the AST for
    `getattr(<pkg>, "<name>", ...)` / `getattr(<pkg>, "<name>")` nodes.
    Resolve <pkg> to the package __init__.py in the repo; fail if <name>
    is not a top-level AST definition OR not in `__all__` OR not imported
    re-export target in that __init__.py.

Gate runs purely against source — does not touch ADG — so it is fast.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci._adg_wiring_gate_base import (  # noqa: E402
    Violation,
    WiringGate,
    cli_exit,
)

SEAM_GLOB = "tests/**/seams/**/*.py"


class SeamTestExportCoherenceGate(WiringGate):
    gate_id = "G2_seam_test_export_coherence"
    tier = "B"

    def run(self, conn) -> list[Violation]:  # conn unused; kept for ABC compat
        _ = conn
        violations: list[Violation] = []
        for py_file in REPO_ROOT.glob(SEAM_GLOB):
            try:
                source = py_file.read_text(encoding="utf-8")
            except OSError:
                continue
            try:
                tree = ast.parse(source)
            except SyntaxError:
                continue
            for pkg_name, sym_name, lineno in _getattr_targets(tree):
                if _resolve_export(pkg_name, sym_name):
                    continue
                rel = py_file.relative_to(REPO_ROOT).as_posix()
                violations.append(
                    Violation(
                        gate_id=self.gate_id,
                        tier=self.tier,
                        subject=f"{rel}:{lineno}",
                        rule="missing_export_in_target_package",
                        detail=(
                            f"seam test asserts getattr({pkg_name}, {sym_name!r}) "
                            f"but {pkg_name}/__init__.py does not export it "
                            f"(no top-level def/class/assign and not in __all__)"
                        ),
                        extra={
                            "pkg": pkg_name,
                            "symbol": sym_name,
                            "test_file": rel,
                            "test_line": lineno,
                        },
                    )
                )
        return violations


# ---------------------------------------------------------------------------
# AST helpers
# ---------------------------------------------------------------------------


def _getattr_targets(tree: ast.AST) -> list[tuple[str, str, int]]:
    """Return list of (pkg_name, symbol_name, lineno) for every
    `getattr(<Name|pytest.fixture-yield>, "<literal>", ...)` call."""
    # Collect name bindings from pytest fixtures of form:
    #   @pytest.fixture(...)
    #   def pkg_fixture():
    #       return pytest.importorskip("agentic_core")
    # so that `getattr(<fixture_param>, "X")` can resolve back to the pkg.
    fixture_to_pkg = _collect_fixture_pkg_bindings(tree)
    results: list[tuple[str, str, int]] = []

    class Visitor(ast.NodeVisitor):
        def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
            if (
                isinstance(node.func, ast.Name)
                and node.func.id == "getattr"
                and len(node.args) >= 2
                and isinstance(node.args[1], ast.Constant)
                and isinstance(node.args[1].value, str)
            ):
                sym_name = node.args[1].value
                first = node.args[0]
                pkg_name = _resolve_first_arg(first, fixture_to_pkg)
                if pkg_name:
                    results.append((pkg_name, sym_name, node.lineno))
            self.generic_visit(node)

    Visitor().visit(tree)
    return results


def _collect_fixture_pkg_bindings(tree: ast.AST) -> dict[str, str]:
    """Return {fixture_name -> pkg_str} for fixtures returning importorskip("pkg")."""
    bindings: dict[str, str] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        # Inspect return statement(s).
        for child in ast.walk(node):
            if not isinstance(child, ast.Return) or child.value is None:
                continue
            call = child.value
            if (
                isinstance(call, ast.Call)
                and isinstance(call.func, ast.Attribute)
                and call.func.attr == "importorskip"
                and call.args
                and isinstance(call.args[0], ast.Constant)
                and isinstance(call.args[0].value, str)
            ):
                bindings[node.name] = call.args[0].value
    return bindings


def _resolve_first_arg(node: ast.AST, fixture_map: dict[str, str]) -> str | None:
    """Given the first arg to `getattr(...)`, return the dotted pkg string or None."""
    if isinstance(node, ast.Name) and node.id in fixture_map:
        return fixture_map[node.id]
    if isinstance(node, ast.Name):
        # Last-resort: treat param name matching fixture name as-is.
        return fixture_map.get(node.id)
    return None


def _resolve_export(pkg: str, symbol: str) -> bool:
    init_path = REPO_ROOT / pkg.replace(".", "/") / "__init__.py"
    if not init_path.exists():
        return False
    try:
        tree = ast.parse(init_path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return False
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name == symbol:
                return True
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == symbol:
                    return True
                if isinstance(target, ast.Name) and target.id == "__all__":
                    if _literal_list_contains(node.value, symbol):
                        return True
        elif isinstance(node, ast.AugAssign):
            if (
                isinstance(node.target, ast.Name)
                and node.target.id == "__all__"
                and _literal_list_contains(node.value, symbol)
            ):
                return True
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                name = alias.asname or alias.name
                if name == symbol:
                    return True
    return False


def _literal_list_contains(node: ast.AST, needle: str) -> bool:
    if isinstance(node, (ast.List, ast.Tuple)):
        for elt in node.elts:
            if isinstance(elt, ast.Constant) and elt.value == needle:
                return True
    return False


def main() -> int:
    return cli_exit(SeamTestExportCoherenceGate().execute())


if __name__ == "__main__":
    sys.exit(main())
