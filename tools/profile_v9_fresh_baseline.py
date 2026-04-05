"""H7: Fresh-process baselines for local and full mode (post-H6).

Spawns two completely separate subprocesses — one for local mode, one for full
mode — so import cache, allocator state, and OS file cache cannot bleed between
runs.  Each subprocess runs the real generate_full_adg pipeline via CLI and
reports its own wall time and peak RSS.

The subprocess wrapper script instruments time.perf_counter() and psutil around
the actual generate_full_adg() call, writes a small JSON result file, then exits.

Usage:
    python tools/profile_v9_fresh_baseline.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import textwrap
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent

_PROBE = textwrap.dedent("""
import sys, os, json, time
sys.path.insert(0, r'{repo_root}')
os.environ.setdefault('ADG_SKIP_SELF_TEST', '1')

import psutil
from pathlib import Path
from datetime import datetime, timezone, timedelta

from tools.generate_full_adg import generate_full_adg

ROOT = Path(r'{repo_root}')
adg_dir = ROOT / 'artifacts' / 'adg'
est = timezone(timedelta(hours=-4))
ts = datetime.now(est).strftime('%m%d%Y_%H%M') + '_probe'

proc = psutil.Process()
rss_pre = proc.memory_info().rss / 1024 / 1024

t0 = time.perf_counter()
generate_full_adg(
    adg_dir, ts,
    archive_old=False,
    parallel=False,
    enable_zip={enable_zip},
    enable_reports={enable_reports},
    enable_analysis={enable_analysis},
)
elapsed = time.perf_counter() - t0
rss_peak = proc.memory_info().rss / 1024 / 1024

result = dict(
    mode='{mode}',
    total_s=round(elapsed, 3),
    rss_pre_mb=round(rss_pre, 1),
    rss_post_mb=round(rss_peak, 1),
    rss_delta_mb=round(rss_peak - rss_pre, 1),
)
out = Path(r'{out_path}')
out.write_text(__import__('json').dumps(result, indent=2))
print('RESULT_FILE=' + str(out))
""").strip()


def run_fresh(mode: str, enable_zip: bool, enable_reports: bool, enable_analysis: bool) -> dict:
    with tempfile.TemporaryDirectory() as td:
        out_path = Path(td) / f"result_{mode}.json"
        script = _PROBE.format(
            repo_root=str(ROOT).replace("\\", "\\\\"),
            mode=mode,
            enable_zip=str(enable_zip),
            enable_reports=str(enable_reports),
            enable_analysis=str(enable_analysis),
            out_path=str(out_path).replace("\\", "\\\\"),
        )
        script_path = Path(td) / f"probe_{mode}.py"
        script_path.write_text(script)

        env = os.environ.copy()
        env["PYTHONHASHSEED"] = "0"          # fixed seed for reproducibility
        env["ADG_SKIP_REDIS"] = "1"          # no Redis during profiling
        env["ADG_SKIP_GIT"] = "1"            # no auto-commit during profiling
        env["ADG_SKIP_SELF_TEST"] = "1"      # no self-test overhead

        print(f"  Spawning fresh process [{mode}]...")
        t_wall_start = time.perf_counter()
        proc = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
            env=env,
        )
        t_wall_total = time.perf_counter() - t_wall_start

        if proc.returncode != 0:
            print(f"  [ERROR] Process failed (mode={mode}):")
            print(proc.stdout[-3000:])
            print(proc.stderr[-2000:])
            raise RuntimeError(f"Probe failed for mode={mode}")

        if not out_path.exists():
            raise RuntimeError(
                f"Result file not written for mode={mode}. stdout:\n{proc.stdout[-2000:]}"
            )

        result = json.loads(out_path.read_text())
        result["wall_from_parent_s"] = round(t_wall_total, 3)
        return result


def main() -> None:
    print("=== ADG v9 Fresh-Process Baselines (post-H6) ===")
    print()

    results = {}

    print("Run 1: LOCAL mode (zip=OFF reports=OFF analysis=OFF)...")
    results["local"] = run_fresh("local", enable_zip=False, enable_reports=False, enable_analysis=False)
    print(f"  Done: {results['local']['total_s']:.2f}s  RSS delta: {results['local']['rss_delta_mb']:+.0f} MB")

    print()
    print("Run 2: FULL mode (zip=ON reports=ON analysis=ON)...")
    results["full"] = run_fresh("full", enable_zip=True, enable_reports=True, enable_analysis=True)
    print(f"  Done: {results['full']['total_s']:.2f}s  RSS delta: {results['full']['rss_delta_mb']:+.0f} MB")

    print()
    print("=" * 64)
    print("FRESH-PROCESS BASELINES (post-H6, PYTHONHASHSEED=0)")
    print("=" * 64)

    local = results["local"]
    full = results["full"]
    delta = full["total_s"] - local["total_s"]

    print(f"  local total:    {local['total_s']:>8.2f}s  (wall from parent: {local['wall_from_parent_s']:.2f}s)")
    print(f"  full  total:    {full['total_s']:>8.2f}s  (wall from parent: {full['wall_from_parent_s']:.2f}s)")
    print(f"  full - local:   {delta:>+8.2f}s  (directly measured mode delta)")
    print()
    print(f"  local peak RSS: {local['rss_post_mb']:.0f} MB  (pre: {local['rss_pre_mb']:.0f} MB)")
    print(f"  full  peak RSS: {full['rss_post_mb']:.0f} MB  (pre: {full['rss_pre_mb']:.0f} MB)")

    profile = {
        "version": "v9",
        "note": "H7: fresh-process baselines post-H6, PYTHONHASHSEED=0, separate subprocesses",
        "local": local,
        "full": full,
        "delta_full_minus_local_s": round(delta, 3),
    }
    out_path = ROOT / "artifacts" / "adg_p8_v9_fresh_baselines.json"
    out_path.write_text(json.dumps(profile, indent=2))
    print()
    print(f"Profile written: {out_path}")


if __name__ == "__main__":
    main()
