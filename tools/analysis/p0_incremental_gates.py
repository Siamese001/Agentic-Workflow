"""Run the four TRACK P0 gates against latest ADG sqlite (no full regen).

Usage:
  python tools/analysis/p0_incremental_gates.py
  python tools/analysis/p0_incremental_gates.py --shadow artifacts/adg/shadow_lpg_proof.sqlite
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def _count_lpg(conn) -> int:
    from ops_scripts.ci.check_lpg_drift_ratchet import LpgDriftRatchetGate  # guardian: allow-layer-violation -- L_TOOLS->L_OPS gate harness

    return len(LpgDriftRatchetGate().run(conn))


def _count_reach(conn) -> int:
    from ops_scripts.ci.check_graph_reach import GraphReachGate  # guardian: allow-layer-violation -- L_TOOLS->L_OPS gate harness

    return len(GraphReachGate().run(conn))


def _count_uwg(conn) -> int:
    from ops_scripts.ci.check_uwg_bypass_ratchet import UwgBypassRatchetGate  # guardian: allow-layer-violation -- L_TOOLS->L_OPS gate harness

    return len(UwgBypassRatchetGate().run(conn))


def _count_write_sovereignty(conn) -> int:
    try:
        row = conn.execute(
            "SELECT COUNT(*) FROM mv_write_sovereignty_paths WHERE is_uwg_routed = 0"
        ).fetchone()
    except Exception:
        return -1
    return int(row[0]) if row else 0


def main() -> int:
    from ops_scripts.ci._adg_wiring_gate_base import (  # guardian: allow-layer-violation -- L_TOOLS->L_OPS ADG gate counter harness
        connect_snapshot,
        latest_snapshot,
    )

    snap = latest_snapshot()
    if "--shadow" in sys.argv:
        idx = sys.argv.index("--shadow")
        snap = ROOT / sys.argv[idx + 1]

    conn = connect_snapshot(snap)
    try:
        rows = [
            ("L2_lpg_drift_ratchet", _count_lpg(conn)),
            ("G_REACH_l0_reachability", _count_reach(conn)),
            ("S2_uwg_bypass_ratchet", _count_uwg(conn)),
            ("3_write_sovereignty", _count_write_sovereignty(conn)),
        ]
    finally:
        conn.close()

    rel = snap.relative_to(ROOT).as_posix() if snap.is_relative_to(ROOT) else str(snap)
    print(f"[p0_incremental_gates] snapshot={rel}")
    for gate_id, count in rows:
        print(f"  {gate_id}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
