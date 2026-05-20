"""Retired legacy ops scripts must be physically absent (not blocked stubs)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]

DELETED_LEGACY_OPS = (
    REPO_ROOT / "ops_scripts" / "ci" / "prove_apps_rg_e2e_runtime.py",
    REPO_ROOT / "ops_scripts" / "apps_rg" / "narrative_pass.py",
)


@pytest.mark.parametrize("script_path", DELETED_LEGACY_OPS, ids=lambda p: p.name)
def test_legacy_ops_script_file_absent(script_path: Path) -> None:
    assert not script_path.is_file(), script_path.as_posix()


@pytest.mark.parametrize(
    "argv_tail",
    (
        ["ops_scripts/ci/prove_apps_rg_e2e_runtime.py"],
        ["ops_scripts/apps_rg/narrative_pass.py"],
    ),
)
def test_direct_python_execution_file_not_found(argv_tail: list[str]) -> None:
    proc = subprocess.run(
        [sys.executable, *argv_tail],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode != 0
    blob = (proc.stderr or "") + (proc.stdout or "")
    assert "can't open file" in blob.lower() or "No such file" in blob or "cannot find the file" in blob.lower()
