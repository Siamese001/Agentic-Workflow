"""Plane-2 three-graph manifest runner for certification mode."""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def run_plane2_manifest_quick(
    *,
    sqlite_path: Path,
    suite: str = "quick",
    strict: bool = True,
) -> tuple[int, Path | None]:
    """Run ``run_adg_three_graph_tests`` and return (exit_code, rollup_path)."""
    rollup = REPO_ROOT / "docs" / "reports" / "adg" / "three_graph_test_rollup.json"
    cmd = [
        sys.executable,
        str(REPO_ROOT / "ops_scripts" / "ci" / "run_adg_three_graph_tests.py"),
        "--suite",
        suite,
        "--snapshot",
        str(sqlite_path),
        "--json-out",
        str(rollup),
    ]
    if strict:
        cmd.append("--strict")
    env = os.environ.copy()
    env["ADG_SNAPSHOT"] = str(sqlite_path.resolve())
    started = time.monotonic()
    proc = subprocess.run(  # noqa: S603
        cmd,
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )
    _ = time.monotonic() - started
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "")[-400:]
        print(f"[ADG] plane-2 manifest FAIL exit={proc.returncode}\n{tail}")
    return proc.returncode, rollup if rollup.is_file() else None


def record_plane2_in_manifest(recorder: object, *, exit_code: int, duration_s: float) -> None:
    """Record ``three_bucket_manifest_quick`` on the gate manifest recorder."""
    from tools.generate._gate_manifest import GateManifestRecorder

    if not isinstance(recorder, GateManifestRecorder):
        return
    status = "pass" if exit_code == 0 else "fail"
    recorder.record(
        "three_bucket_manifest_quick",
        phase="post-ADG-subprocess",
        kind="subprocess",
        blocking_mode="hard_fail",
        status=status,
        exit_code=exit_code,
        duration_s=duration_s,
        script_rel="ops_scripts/ci/run_adg_three_graph_tests.py",
        message=f"suite=quick strict=1 exit={exit_code}",
    )
