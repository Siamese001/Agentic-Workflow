"""Production callers of dispatch surfaces must not include shadow runtime CLIs."""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]

ALLOWED_DISPATCH_APPS_RG_RUN = frozenset(
    {
        "apps_rg/__main__.py",
        "agentic_core/runtime/entry/apps_rg_dispatch.py",
        "apps_rg/runtime/dispatch/apps_rg_dispatch.py",  # apps_rg_parse helper, not public CLI
    }
)

ALLOWED_CANONICAL_DISPATCH_PREFIXES = (
    "apps_rg/__main__.py",
    "agentic_core/runtime/entry/apps_rg_dispatch.py",
    "apps_rg/runtime/dispatch/apps_rg_dispatch.py",
)

FORBIDDEN_CANONICAL_CALLER_SUFFIXES = (
    "apps_rg/runtime/dispatch/",
    "apps_rg/runtime/package/",
    "apps_rg/runtime/reports/",
    "apps_rg/runtime/assembly/",
)


def _py_files_under_apps_and_ops() -> list[Path]:
    roots = [REPO_ROOT / "apps_rg", REPO_ROOT / "ops_scripts"]
    out: list[Path] = []
    for root in roots:
        if not root.is_dir():
            continue
        for path in root.rglob("*.py"):
            if "tests" in path.parts or "__pycache__" in path.parts:
                continue
            out.append(path)
    return out


def _find_calls(path: Path, symbol: str) -> list[int]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    lines: list[int] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Name) and fn.id == symbol:
                lines.append(node.lineno)
            elif isinstance(fn, ast.Attribute) and fn.attr == symbol:
                lines.append(node.lineno)
    return lines


def test_dispatch_apps_rg_run_callers_are_canonical_bridge_only() -> None:
    offenders: list[str] = []
    for path in _py_files_under_apps_and_ops():
        rel = path.relative_to(REPO_ROOT).as_posix()
        if rel.startswith("tests/"):
            continue
        if "test_" in path.name:
            continue
        hits = _find_calls(path, "dispatch_apps_rg_run")
        if not hits:
            continue
        if rel not in ALLOWED_DISPATCH_APPS_RG_RUN:
            offenders.append(f"{rel}:{hits}")
    assert not offenders, f"Unexpected dispatch_apps_rg_run callers: {offenders}"


def test_run_canonical_apps_rg_from_cli_primitives_not_in_shadow_runtime_modules() -> None:
    offenders: list[str] = []
    for path in _py_files_under_apps_and_ops():
        rel = path.relative_to(REPO_ROOT).as_posix()
        if rel.startswith("tests/"):
            continue
        if "test_" in path.name:
            continue
        hits = _find_calls(path, "run_canonical_apps_rg_from_cli_primitives")
        if not hits:
            continue
        if any(rel.startswith(p) for p in ALLOWED_CANONICAL_DISPATCH_PREFIXES):
            continue
        if any(part in rel for part in FORBIDDEN_CANONICAL_CALLER_SUFFIXES):
            offenders.append(f"{rel}:{hits}")
    assert not offenders, f"Shadow runtime modules call canonical_dispatch: {offenders}"
