"""Integration tests for the manifest runner against the live snapshot."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
RUNNER = REPO_ROOT / "ops_scripts" / "ci" / "run_adg_three_graph_tests.py"
LIVE_SNAPSHOT = sorted(
    (REPO_ROOT / "artifacts" / "adg").glob("adg_indexed_*.sqlite")
)


@pytest.fixture(scope="module")
def latest_snapshot() -> Path:
    if not LIVE_SNAPSHOT:
        pytest.skip("no live snapshot at artifacts/adg/")
    return LIVE_SNAPSHOT[-1]


def _run_runner(*args: str, env_extra: dict | None = None, timeout: int = 120):
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        [sys.executable, str(RUNNER), *args],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


class TestRunnerIntegration:
    def test_quick_suite_runs(self, latest_snapshot, tmp_path):
        out_path = tmp_path / "rollup.json"
        proc = _run_runner(
            "--suite", "quick",
            "--snapshot", str(latest_snapshot),
            "--json-out", str(out_path),
        )
        # Exit may be 0/1 depending on snapshot health; rollup must exist.
        assert proc.returncode in (0, 1)
        assert out_path.exists()
        rollup = json.loads(out_path.read_text())
        assert rollup["suite"] == "quick"
        assert rollup["snapshot_id"]
        assert isinstance(rollup["gates"], list)
        assert rollup["gates"], "no gates ran"

    def test_bucket_filter_registry(self, latest_snapshot, tmp_path):
        out_path = tmp_path / "rollup.json"
        proc = _run_runner(
            "--suite", "full",
            "--bucket", "registry",
            "--snapshot", str(latest_snapshot),
            "--json-out", str(out_path),
        )
        assert proc.returncode in (0, 1)
        rollup = json.loads(out_path.read_text())
        for g in rollup["gates"]:
            assert g["bucket"] == "registry"

    def test_strict_bypass_overrides_to_fail(self, latest_snapshot, tmp_path):
        out_path = tmp_path / "rollup.json"
        # Set the bypass env for the registry integrity gate, then run
        # in strict mode and assert overall_status=FAIL with the dedicated
        # STRICT_BYPASS_DETECTED reason.
        proc = _run_runner(
            "--suite", "quick",
            "--bucket", "registry",
            "--strict",
            "--snapshot", str(latest_snapshot),
            "--gate-id", "registry.graph_integrity",
            "--json-out", str(out_path),
            env_extra={"REGISTRY_INTEGRITY_BYPASS": "1"},
        )
        assert proc.returncode == 1
        rollup = json.loads(out_path.read_text())
        assert rollup["overall_status"] == "FAIL"
        gate = next(g for g in rollup["gates"]
                    if g["gate_id"] == "registry.graph_integrity")
        assert gate["status"] == "FAIL"
        assert gate["actual_fail_reason"].startswith("STRICT_BYPASS_DETECTED:")
        assert "REGISTRY_INTEGRITY_BYPASS" in gate["bypass_env_detected"]

    def test_unknown_bucket_errors(self, latest_snapshot):
        proc = _run_runner(
            "--suite", "quick",
            "--bucket", "kitchen_sink",  # not in choices
        )
        assert proc.returncode == 2  # argparse error
