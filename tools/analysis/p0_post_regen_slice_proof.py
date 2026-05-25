"""After full ADG regen: prove P0 slice gates on latest canonical sqlite.

Writes: artifacts/adg/p0_slices/post_regen_slice_proof.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

SLICE_BEFORE = {
    "L2_lpg_drift_ratchet": {"canonical_before": 28, "shadow_proof": 0},
    "G_REACH_l0_reachability": {"canonical_before": 2810, "shadow_delta": -23},
}


def main() -> int:
    from importlib import import_module

    from ops_scripts.ci._adg_wiring_gate_base import (  # guardian: allow-layer-violation -- L_TOOLS->L_OPS ADG proof harness
        connect_snapshot,
        latest_snapshot,
    )

    snap = latest_snapshot()
    conn = connect_snapshot(snap)
    try:
        lpg = import_module("ops_scripts.ci.check_lpg_drift_ratchet")
        reach = import_module("ops_scripts.ci.check_graph_reach")
        uwg = import_module("ops_scripts.ci.check_uwg_bypass_ratchet")
        lpg_n = len(lpg.LpgDriftRatchetGate().run(conn))
        reach_n = len(reach.GraphReachGate().run(conn))
        uwg_n = len(uwg.UwgBypassRatchetGate().run(conn))
        ws = conn.execute(
            "SELECT COUNT(*) FROM mv_write_sovereignty_paths WHERE is_uwg_routed = 0"
        ).fetchone()[0]
    finally:
        conn.close()

    out = {
        "snapshot": snap.relative_to(ROOT).as_posix(),
        "slices": {
            "L2_lpg_drift_ratchet": {
                "before_canonical": SLICE_BEFORE["L2_lpg_drift_ratchet"]["canonical_before"],
                "after": lpg_n,
                "delta": lpg_n - SLICE_BEFORE["L2_lpg_drift_ratchet"]["canonical_before"],
                "shadow_proof_was": SLICE_BEFORE["L2_lpg_drift_ratchet"]["shadow_proof"],
                "claim_met": lpg_n == 0,
            },
            "G_REACH_l0_reachability": {
                "before_canonical": SLICE_BEFORE["G_REACH_l0_reachability"]["canonical_before"],
                "after": reach_n,
                "delta": reach_n - SLICE_BEFORE["G_REACH_l0_reachability"]["canonical_before"],
                "shadow_delta_was": SLICE_BEFORE["G_REACH_l0_reachability"]["shadow_delta"],
                "claim_met": reach_n <= 2810 - 20,
            },
            "S2_uwg_bypass_ratchet": {"after": uwg_n, "claim_met": False, "note": "not in slice scope"},
            "3_write_sovereignty": {"after": int(ws), "claim_met": False, "note": "not in slice scope"},
        },
    }
    out_dir = ROOT / "artifacts/adg/p0_slices"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "post_regen_slice_proof.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))
    ok = out["slices"]["L2_lpg_drift_ratchet"]["claim_met"] and out["slices"]["G_REACH_l0_reachability"]["claim_met"]
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
