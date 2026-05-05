"""P0.1 Governance tests — apps_underwriting_ai no legacy runner.

Enforces that the legacy runner pattern (direct UnderwritingEngine
instantiation, ExecutionAdapter invocation, or inline pipeline calls)
is absent from the public entrypoint path after W1.

Plan: apps-underwriting-ai-spine-hardening-d7f3b2 P0.1 / P0.4.

Tests 18–19 (legacy runner group). Both are xfail(strict=True) on the
current codebase. They become GREEN after W1 rewrites __main__.py.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = REPO_ROOT / "apps_underwriting_ai"
MAIN_PY = APP_DIR / "__main__.py"


def _src() -> str:
    assert MAIN_PY.exists(), f"apps_underwriting_ai/__main__.py missing: {MAIN_PY}"
    return MAIN_PY.read_text(encoding="utf-8")


def _tree() -> ast.Module:
    return ast.parse(_src())


# ---------------------------------------------------------------------------
# 18. No ExecutionAdapter in __main__.py
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_underwriting_ai_main_does_not_use_execution_adapter() -> None:
    """__main__.py must not import or instantiate ExecutionAdapter.

    ExecutionAdapter is an internal integration adapter; after W1 the shim
    delegates all execution to the agentic_core runner via the registered
    capability ID. ExecutionAdapter may be used internally but must not appear
    in __main__.py.
    """
    src = _src()
    assert "ExecutionAdapter" not in src, (
        "apps_underwriting_ai/__main__.py references ExecutionAdapter. "
        "After W1, execution is delegated through the agentic_core runner "
        "and the registered capability — ExecutionAdapter must not appear in the shim."
    )


# ---------------------------------------------------------------------------
# 19. No UnderwritingEngine instantiation in __main__.py
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_underwriting_ai_main_does_not_instantiate_underwriting_engine() -> None:
    """__main__.py must not instantiate UnderwritingEngine directly.

    Engine instantiation belongs inside the governed execution substrate,
    not in the CLI shim. After W1, __main__.py only resolves the registered
    capability and calls the agentic_core runner.
    """
    tree = _tree()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            name = None
            if isinstance(func, ast.Name):
                name = func.id
            elif isinstance(func, ast.Attribute):
                name = func.attr
            if name in ("UnderwritingEngine", "ExecutionAdapter"):
                pytest.fail(
                    f"apps_underwriting_ai/__main__.py instantiates {name} at line "
                    f"{getattr(node, 'lineno', '?')}. "
                    "Engine instantiation is forbidden in the pure shim."
                )
