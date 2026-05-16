"""AST guard — generic Exit modules must not import ``apps_rg`` logic."""

from __future__ import annotations

import ast
from pathlib import Path

_SKIP_NAMES = frozenset(
    {
        "apps_rg_exit_binding.py",
        "apps_lic_exit_binding.py",
        "apps_research_exit_binding.py",
    },
)


def test_runtime_exit_non_shim_modules_avoid_apps_rg_imports() -> None:
    exit_dir = Path(__file__).resolve().parents[2] / "agentic_core" / "runtime" / "exit"
    offenders: list[str] = []
    for py in sorted(exit_dir.glob("*.py")):
        if py.name in _SKIP_NAMES:
            continue
        tree = ast.parse(py.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "apps_rg" or alias.name.startswith("apps_rg."):
                        offenders.append(f"{py.name}: import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                if mod == "apps_rg" or mod.startswith("apps_rg."):
                    offenders.append(f"{py.name}: from {mod}")
    assert not offenders, "; ".join(offenders)
