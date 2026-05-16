"""Smoke tests for apps_rg spine binding fixture + CLI."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from agentic_core.runtime.bindings.app_binding_loader import load_app_binding_package
from agentic_core.runtime.bindings.app_binding_validation import validate_app_binding_package

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PKG = REPO_ROOT / "tests/_core_contract/fixtures/apps_rg_binding_package"


def test_binding_fixture_load_validate_pass() -> None:
    pkg = load_app_binding_package(FIXTURE_PKG)
    assert validate_app_binding_package(pkg).status == "PASS"


def test_python_m_apps_rg_help_exits_zero() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "apps_rg", "--help"],
        cwd=str(REPO_ROOT),
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
