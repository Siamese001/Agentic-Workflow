"""W7 HITL sentinel — no ad hoc input() outside cli_hitl_adapter.py.

AST scan of every .py file under apps_rg/ and tests/governance/:
- input() calls are ONLY permitted in apps_rg/hitl/cli_hitl_adapter.py.
- All other apps_rg modules (including __main__, L2 steps, helpers) must
  have zero input() calls.

Plan: apps-rg-canonical-wireup-c8a4f2 W7 sentinel.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
APPS_RG_DIR = REPO_ROOT / "apps_rg"
ALLOWED_INPUT_FILE = APPS_RG_DIR / "hitl" / "cli_hitl_adapter.py"


def _find_input_calls(path: Path) -> list[int]:
    """Return line numbers of input() calls in path."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError:
        return []
    lines: list[int] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "input":
                lines.append(node.lineno)
    return lines


@pytest.mark.governance
def test_apps_rg_no_input_outside_cli_hitl_adapter() -> None:
    """No apps_rg module except cli_hitl_adapter.py may call input()."""
    violations: list[str] = []
    for py_file in sorted(APPS_RG_DIR.rglob("*.py")):
        if py_file.resolve() == ALLOWED_INPUT_FILE.resolve():
            continue
        lines = _find_input_calls(py_file)
        if lines:
            rel = py_file.relative_to(REPO_ROOT)
            violations.append(f"{rel} — input() at lines {lines}")

    assert not violations, (
        "Found input() calls outside the single allowed chokepoint "
        f"(apps_rg/hitl/cli_hitl_adapter.py):\n"
        + "\n".join(f"  {v}" for v in violations)
    )


@pytest.mark.governance
def test_apps_rg_cli_hitl_adapter_exists() -> None:
    """The single input() chokepoint file must exist."""
    assert ALLOWED_INPUT_FILE.exists(), (
        f"cli_hitl_adapter.py not found at {ALLOWED_INPUT_FILE}. "
        "W7 P-HITL2 required."
    )


@pytest.mark.governance
def test_apps_rg_cli_hitl_adapter_has_exactly_one_input_call() -> None:
    """cli_hitl_adapter.py itself must have exactly one input() call."""
    assert ALLOWED_INPUT_FILE.exists(), "cli_hitl_adapter.py missing"
    lines = _find_input_calls(ALLOWED_INPUT_FILE)
    assert len(lines) == 1, (
        f"Expected exactly 1 input() call in cli_hitl_adapter.py, "
        f"found {len(lines)} at lines {lines}. "
        "The adapter must consolidate all interactive I/O into one call."
    )
