#!/usr/bin/env python3
"""Seed wiring-ci ratchet baselines against the latest ADG snapshot (post-regen absorb)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

SEED_SCRIPTS = [
    "ops_scripts/ci/check_module_loc_ratchet.py",
    "ops_scripts/ci/check_uwg_bypass_ratchet.py",
    "ops_scripts/ci/check_unused_imports_ratchet.py",
    "ops_scripts/ci/check_layer_skip.py",
    "ops_scripts/ci/check_cyclomatic_ceiling.py",
    "ops_scripts/ci/check_w4_silent_writes.py",
    "ops_scripts/ci/check_w4_exit_disposition.py",
    "ops_scripts/ci/check_w4_replay_surface_gaps.py",
    "ops_scripts/ci/check_w4_tool_call_parity.py",
    "ops_scripts/ci/check_w5_taint_actionable.py",
    "ops_scripts/ci/check_w5_untyped_seam.py",
    "ops_scripts/ci/check_graph_reach.py",
]


def _resolve_snapshot() -> Path:
    override = os.environ.get("ADG_SNAPSHOT", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    from tools.adg.shared_modules.path_resolver import latest_sqlite  # noqa: PLC0415

    snap = latest_sqlite()
    if snap is None:
        raise FileNotFoundError("no adg_indexed_*.sqlite under artifacts/adg")
    return snap


def main() -> int:
    snapshot = _resolve_snapshot()
    if not snapshot.is_file():
        print(f"[seed] missing snapshot: {snapshot}", file=sys.stderr)
        return 2
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT)
    env["ADG_SNAPSHOT"] = str(snapshot)
    rc = 0
    for rel in SEED_SCRIPTS:
        cmd = [sys.executable, str(REPO_ROOT / rel), "--seed"]
        print(f"[seed] {' '.join(cmd)}")
        proc = subprocess.run(cmd, cwd=str(REPO_ROOT), env=env, check=False)  # noqa: S603
        if proc.returncode != 0:
            rc = proc.returncode
            print(f"[seed] FAIL {rel} exit={proc.returncode}", file=sys.stderr)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
