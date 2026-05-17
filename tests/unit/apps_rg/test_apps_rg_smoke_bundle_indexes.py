"""DoD-4 — RG-SMOKE-BUNDLE gate for pinned apps_rg smoke evidence bundles."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
_GATE_SCRIPT = _REPO_ROOT / "ops_scripts" / "ci" / "check_apps_rg_smoke_bundle_indexes.py"


def test_rg_smoke_bundle_gate_cli_exits_zero() -> None:
    """Runner must stay green on fresh clones (no smoke dirs) and locally when dirs exist."""
    env = os.environ.copy()
    env.pop("APPS_RG_MODULAR_R4_SECTIONS_ROOT", None)
    proc = subprocess.run(
        [sys.executable, str(_GATE_SCRIPT)],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


@pytest.mark.skipif(
    not (_REPO_ROOT / "artifacts" / "apps_rg" / "runs" / "_proof_smoke_integrated").is_dir(),
    reason="pinned integrated smoke bundle not present under artifacts",
)
def test_integrated_smoke_has_modular_sections_root_default_when_env_clean() -> None:
    integrated = _REPO_ROOT / "artifacts" / "apps_rg" / "runs" / "_proof_smoke_integrated"
    assert (integrated / "RUN_LINKS.json").is_file()

    env = os.environ.copy()
    env.pop("APPS_RG_MODULAR_R4_SECTIONS_ROOT", None)
    proc = subprocess.run(
        [sys.executable, str(_GATE_SCRIPT)],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "[RG-SMOKE-BUNDLE] FAIL" not in proc.stdout
