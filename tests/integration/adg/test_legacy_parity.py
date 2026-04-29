"""Legacy parity test — manifest runner and legacy script agree on PASS/FAIL.

For every gate marked ``legacy: true`` in the manifest, this test invokes
the script directly AND through the manifest runner, then asserts both
agree on the exit code's pass/fail interpretation.

This is the contract that lets the harness ship without removing the
existing scripts: the runner is a faithful wrapper. If a future edit makes
them disagree, this test catches it.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
RUNNER = REPO_ROOT / "ops_scripts" / "ci" / "run_adg_three_graph_tests.py"
MANIFEST = REPO_ROOT / "ops_scripts" / "ci" / "adg_gate_manifest.yaml"
LIVE_SNAPSHOT = sorted(
    (REPO_ROOT / "artifacts" / "adg").glob("adg_indexed_*.sqlite")
)


@pytest.fixture(scope="module")
def latest_snapshot():
    if not LIVE_SNAPSHOT:
        pytest.skip("no live snapshot")
    return LIVE_SNAPSHOT[-1]


def _load_manifest():
    return yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))


def _legacy_gates():
    manifest = _load_manifest()
    return [g for g in manifest["gates"] if g.get("legacy")]


@pytest.mark.parametrize("gate", _legacy_gates(), ids=lambda g: g["gate_id"])
def test_legacy_runner_parity(gate, latest_snapshot, tmp_path):
    """Direct invocation and runner invocation agree on pass/fail."""
    script = REPO_ROOT / gate["script"]
    if not script.exists():
        pytest.skip(f"legacy script missing: {gate['script']}")

    env = os.environ.copy()
    # Snapshot pin via env so legacy gates that don't accept --snapshot
    # still find the right file.
    env["ADG_SNAPSHOT"] = str(latest_snapshot)

    direct = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(REPO_ROOT), env=env,
        capture_output=True, text=True, timeout=120, check=False,
    )

    rollup_out = tmp_path / "rollup.json"
    runner = subprocess.run(
        [
            sys.executable, str(RUNNER),
            "--suite", "full",
            "--gate-id", gate["gate_id"],
            "--snapshot", str(latest_snapshot),
            "--json-out", str(rollup_out),
        ],
        cwd=str(REPO_ROOT), env=env,
        capture_output=True, text=True, timeout=120, check=False,
    )
    assert rollup_out.exists(), runner.stdout + runner.stderr
    rollup = json.loads(rollup_out.read_text())

    # Find the gate's row in the rollup.
    rows = [g for g in rollup["gates"] if g["gate_id"] == gate["gate_id"]]
    assert rows, f"runner did not produce a row for {gate['gate_id']}"
    runner_status = rows[0]["status"]

    # Parity contract: direct exit 0 <=> runner status in {PASS, WARN, SKIP}.
    direct_pass = direct.returncode == 0
    runner_pass = runner_status in ("PASS", "WARN", "SKIP")
    assert direct_pass == runner_pass, (
        f"parity mismatch for {gate['gate_id']}: "
        f"direct_exit={direct.returncode} (pass={direct_pass}) "
        f"runner_status={runner_status} (pass={runner_pass})\n"
        f"direct.stdout: {direct.stdout[-400:]}\n"
        f"runner.stdout: {runner.stdout[-400:]}"
    )
