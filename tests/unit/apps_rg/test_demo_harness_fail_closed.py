"""SP-002: executive_summary demo harness env gate (W7A)."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from apps_rg.runtime.non_product_proof_stamp import DEMO_HARNESS_ENV

REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE = "apps_rg.runtime.dry_run.executive_summary_demo"


def test_demo_harness_module_fails_without_env() -> None:
    env = os.environ.copy()
    env.pop(DEMO_HARNESS_ENV, None)
    proc = subprocess.run(
        [sys.executable, "-m", MODULE],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
    )
    assert proc.returncode == 2
    assert DEMO_HARNESS_ENV in (proc.stderr or "")


def test_demo_harness_module_runs_with_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(DEMO_HARNESS_ENV, "1")
    proc = subprocess.run(
        [sys.executable, "-m", MODULE],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0
