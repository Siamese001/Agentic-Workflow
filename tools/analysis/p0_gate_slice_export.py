"""Export P0 gate violations from latest ADG sqlite without full regen.

After import-surface edits, prove on shadow snapshots (no full ADG):

  python tools/analysis/p0_incremental_lpg_proof.py
  python tools/analysis/p0_incremental_reach_proof.py
  python tools/analysis/p0_reach_delta.py

Usage:
  python tools/analysis/p0_gate_slice_export.py L2_lpg_drift_ratchet
  python tools/analysis/p0_gate_slice_export.py --all
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

GATE_RUNNERS: dict[str, tuple[str, str]] = {
    "L2_lpg_drift_ratchet": ("ops_scripts.ci.check_lpg_drift_ratchet", "LpgDriftRatchetGate"),
    "G_REACH_l0_reachability": ("ops_scripts.ci.check_graph_reach", "GraphReachGate"),
    "S2_uwg_bypass_ratchet": ("ops_scripts.ci.check_uwg_bypass_ratchet", "UwgBypassRatchetGate"),
}


def _export(gate_id: str) -> dict:
    mod_path, cls_name = GATE_RUNNERS[gate_id]
    from importlib import import_module

    from ops_scripts.ci._adg_wiring_gate_base import (  # guardian: allow-layer-violation -- L_TOOLS->L_OPS ADG gate export harness
        connect_snapshot,
        latest_snapshot,
    )

    mod = import_module(mod_path)
    gate_cls = getattr(mod, cls_name)
    conn = connect_snapshot(latest_snapshot())
    try:
        gate = gate_cls()
        violations = gate.run(conn)
    finally:
        conn.close()
    rows = []
    for v in violations:
        rows.append(
            {
                "subject": v.subject,
                "rule": v.rule,
                "detail": v.detail,
                "extra": v.extra,
            }
        )
    return {"gate_id": gate_id, "count": len(rows), "violations": rows}


def main() -> int:
    targets = list(GATE_RUNNERS) if "--all" in sys.argv else [sys.argv[1]] if len(sys.argv) > 1 else ["L2_lpg_drift_ratchet"]
    out_dir = ROOT / "artifacts" / "adg" / "p0_slices"
    out_dir.mkdir(parents=True, exist_ok=True)
    for gate_id in targets:
        payload = _export(gate_id)
        out = out_dir / f"{gate_id}.json"
        out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"[p0_gate_slice] {gate_id}: {payload['count']} -> {out.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
