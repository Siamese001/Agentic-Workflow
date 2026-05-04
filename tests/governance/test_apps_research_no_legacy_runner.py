"""P0.1 Governance tests — apps_research legacy runner prohibition.

Enforces that:
- No legacy feature flag re-enables the legacy runner
- apps_research.scripts.run_research is not reachable from __main__.py

Plan: apps-research-spine-alignment-d4e8f2 P0.1.

Tests 17-18 in the P0 test suite. Initially RED because __main__.py
currently delegates to run_research.main at line 226.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
APP_DIR = REPO_ROOT / "apps_research"
MAIN_PY = APP_DIR / "__main__.py"
SCRIPTS_DIR = APP_DIR / "scripts"
LEGACY_RUNNER = SCRIPTS_DIR / "run_research.py"


def _src(path: Path) -> str:
    assert path.exists(), f"File missing: {path}"
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# 17. No legacy runner feature flag
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_research_no_legacy_runner_feature_flag() -> None:
    """apps_research/__main__.py must not contain a feature flag that re-enables
    the legacy runner on any code path.

    Patterns forbidden: USE_LEGACY_RUNNER, LEGACY_RUNNER_ENABLED, use_legacy,
    legacy_mode, fallback_to_legacy, etc.
    """
    if not MAIN_PY.exists():
        pytest.skip("__main__.py not found")
    src = _src(MAIN_PY)
    flag_patterns = [
        "USE_LEGACY_RUNNER",
        "LEGACY_RUNNER",
        "legacy_runner",
        "use_legacy",
        "legacy_mode",
        "fallback_to_legacy",
        "FALLBACK_RUNNER",
        "old_runner",
        "OLD_RUNNER",
    ]
    found = [p for p in flag_patterns if p in src]
    assert not found, (
        f"apps_research/__main__.py contains legacy runner feature flag(s): {found}. "
        "No feature flag may re-enable the legacy runner. The canonical agentic_core "
        "runner is the only valid execution path."
    )


# ---------------------------------------------------------------------------
# 18. Legacy script not reachable from __main__
# ---------------------------------------------------------------------------

@pytest.mark.governance
def test_apps_research_legacy_scripts_not_reachable_from_main() -> None:
    """apps_research.scripts.run_research must not be importable from __main__.py.

    After W5 quarantine, run_research.py will be archived. Before archival,
    it must not be reachable on any code path from __main__.py — no import,
    no importlib.import_module, no exec, no subprocess call.
    """
    if not MAIN_PY.exists():
        pytest.skip("__main__.py not found")
    src = _src(MAIN_PY)
    tree = ast.parse(src)

    # Check direct imports
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if "run_research" in mod or "scripts.run_research" in mod:
                pytest.fail(
                    f"apps_research/__main__.py imports from run_research at line "
                    f"{node.lineno}: from {mod} import .... "
                    "The legacy runner must not be reachable from __main__.py."
                )
        if isinstance(node, ast.Import):
            for alias in node.names:
                if "run_research" in alias.name:
                    pytest.fail(
                        f"apps_research/__main__.py imports run_research module at line "
                        f"{node.lineno}. The legacy runner must not be reachable."
                    )

    # Check importlib.import_module("apps_research.scripts.run_research")
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            call_name = ""
            if isinstance(func, ast.Name):
                call_name = func.id
            elif isinstance(func, ast.Attribute):
                call_name = func.attr
            if call_name == "import_module":
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and "run_research" in str(arg.value):
                        pytest.fail(
                            f"apps_research/__main__.py uses importlib.import_module to "
                            f"load run_research at line {getattr(node, 'lineno', '?')}."
                        )

    # String reference check (catches f-string or exec patterns)
    assert "run_research" not in src, (
        "apps_research/__main__.py contains the string 'run_research'. "
        "The legacy runner module must not be referenced from __main__.py in any form."
    )
