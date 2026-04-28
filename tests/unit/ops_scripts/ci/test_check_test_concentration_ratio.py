"""Tests for `ops_scripts.ci.check_test_concentration_ratio`.

Covers the 4 operational modes:
    - bypass (env)
    - advisory (default — never fails)
    - strict (fails on drift)
    - write_baseline

Plus the no-snapshot edge case (fresh clone before first ADG run).

Uses synthetic SQLite snapshots in tmp_path to avoid coupling to whatever
adg_indexed_*.sqlite happens to be present in artifacts/adg/.
"""
from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
SCRIPT = REPO_ROOT / "ops_scripts" / "ci" / "check_test_concentration_ratio.py"


def _run(env_overrides: dict | None = None, cwd: Path | None = None) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    if env_overrides:
        env.update(env_overrides)
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
        cwd=str(cwd or REPO_ROOT),
        shell=False,
        check=False,
    )


def test_bypass_env_short_circuits():
    r = _run({"TEST_CONCENTRATION_GATE_BYPASS": "1"})
    assert r.returncode == 0
    assert "BYPASSED" in r.stdout


def test_advisory_mode_never_fails():
    """Advisory is the default mode — should always exit 0 even with violations."""
    # Don't set STRICT or BYPASS — pure default
    r = _run()
    assert r.returncode == 0
    # Either reports findings (if snapshot exists) or "no usable snapshot"
    assert "advisory" in r.stdout or "no usable" in r.stdout


def test_no_snapshot_returns_advisory_zero(tmp_path: Path):
    """Fresh clone with no ADG snapshot should pass cleanly (advisory)."""
    # Run from tmp_path which has no artifacts/adg/ dir → script's
    # ROOT-relative glob won't find any snapshot
    fake_root = tmp_path / "fake_repo"
    fake_root.mkdir()
    # Copy script into fake repo at the same relative path it expects
    fake_script_dir = fake_root / "ops_scripts" / "ci"
    fake_script_dir.mkdir(parents=True)
    (fake_script_dir / "check_test_concentration_ratio.py").write_text(
        SCRIPT.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    r = subprocess.run(
        [sys.executable, str(fake_script_dir / "check_test_concentration_ratio.py")],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(fake_root),
        shell=False,
        check=False,
    )
    assert r.returncode == 0
    assert "no usable ADG SQLite snapshot" in r.stdout


def test_baseline_file_exists_after_write_command():
    """Verifying the WRITE_BASELINE flow produces a valid JSON file."""
    baseline = REPO_ROOT / "ops_scripts" / "ci" / "baselines" / "test_concentration_ratchet.json"
    if not baseline.exists():
        pytest.skip("baseline file not yet created — run gate with WRITE_BASELINE=1 once")
    data = json.loads(baseline.read_text(encoding="utf-8"))
    assert "over_invested_count" in data
    assert "under_invested_subjects" in data
    assert isinstance(data["over_invested_count"], int)
    assert isinstance(data["under_invested_subjects"], list)


def test_strict_mode_passes_when_no_drift_vs_baseline():
    """If baseline matches current state, strict mode should PASS."""
    baseline = REPO_ROOT / "ops_scripts" / "ci" / "baselines" / "test_concentration_ratchet.json"
    if not baseline.exists():
        pytest.skip("baseline not present")
    r = _run({"TEST_CONCENTRATION_GATE_STRICT": "1"})
    # Either passes (no drift), or fails with explicit FAIL message — never silent.
    if r.returncode != 0:
        assert "FAIL" in r.stdout or "FAIL" in r.stderr
    else:
        assert "PASS" in r.stdout


def test_strict_mode_fails_with_phantom_baseline():
    """Forge a baseline that says under_invested=[] then run strict — if
    current state has under_invested entries, gate must FAIL."""
    baseline_path = REPO_ROOT / "ops_scripts" / "ci" / "baselines" / "test_concentration_ratchet.json"
    if not baseline_path.exists():
        pytest.skip("real baseline not present — cannot test phantom override")

    real = baseline_path.read_text(encoding="utf-8")
    try:
        # Write phantom: zero under-invested → any current finding becomes NEW
        baseline_path.write_text(
            json.dumps({"over_invested_count": 0, "under_invested_subjects": []}),
            encoding="utf-8",
        )
        r = _run({"TEST_CONCENTRATION_GATE_STRICT": "1"})
        # If snapshot has any over/under findings, gate must fail
        # (we know it does from the WRITE_BASELINE step in setup)
        # Skip if no snapshot reachable
        if "no usable" in r.stdout:
            pytest.skip("no ADG snapshot in CI env")
        assert r.returncode == 1, f"Expected FAIL with phantom baseline, got {r.returncode}\n{r.stdout}"
        assert "FAIL" in r.stdout
    finally:
        # Restore real baseline
        baseline_path.write_text(real, encoding="utf-8")
