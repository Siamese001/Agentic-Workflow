"""Query ADG for each cleanup wave's target list.

Wave 1: A12 gate_self_consistency with enforcement_without_claim
Wave 2: Tier 1 redundancy gates — verify actual SQL/logic
Wave 3: Tier 2 P-view consumers — verify centralized usage
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ADG_DIR = REPO / "artifacts" / "adg"


def _latest_enriched() -> Path:
    candidates = sorted(
        f
        for f in ADG_DIR.iterdir()
        if f.name.startswith("adg_indexed") and f.suffix == ".sqlite" and "tmp" not in f.name
    )
    for path in reversed(candidates):
        # progress_bar: bounded loop — §16 exempt (small fixed-cost iteration)
        try:
            con = sqlite3.connect(path)
            tables = {
                r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view')")
            }
            con.close()
            if {"gate_self_consistency"} <= tables:
                return path
        except sqlite3.DatabaseError:
            continue
    raise RuntimeError("No enriched snapshot")


def main() -> int:
    snap = _latest_enriched()
    print(f"# Wave Targets — from {snap.name}\n")
    con = sqlite3.connect(snap)

    # --- Wave 1: A12 doc-drift ---
    print("## Wave 1 — A12 doc-drift (enforcement_without_claim)\n")
    rows = con.execute(
        """
        SELECT path, consistency, claims, logic_patterns
        FROM gate_self_consistency
        WHERE consistency = 'enforcement_without_claim'
        ORDER BY path
        """
    ).fetchall()
    print(f"Count: {len(rows)}\n")
    print("| # | Gate Path | Claims | Logic Patterns |")
    print("|---|-----------|--------|----------------|")
    for i, (path, _cons, claims, patterns) in enumerate(rows, 1):
        rel = path.replace(str(REPO) + "\\", "").replace(str(REPO) + "/", "")
        rel = rel.replace("\\", "/")
        c = claims[:40] if claims else "(empty)"
        p = patterns[:60] if patterns else "(empty)"
        print(f"| {i} | `{rel}` | {c} | {p} |")
    print()

    # Breakdown of all gate_self_consistency states
    print("### gate_self_consistency breakdown\n")
    breakdown = con.execute(
        "SELECT consistency, COUNT(*) FROM gate_self_consistency GROUP BY consistency ORDER BY 2 DESC"
    ).fetchall()
    for k, cnt in breakdown:
        print(f"- {k}: {cnt}")

    # --- Wave 2: Tier 1 redundancy ---
    print("\n## Wave 2 — Tier 1 redundancy verification\n")
    wave2_gates = [
        "check_dead_folder_detector.py",
        "check_dead_symbols_ratchet.py",
        "check_graph_watchlist_delta.py",
        "check_w6_fanin_collapse.py",
        "check_observability_on_high_fanin.py",
        "check_trace_stub_modules.py",
        "check_external_service_literal_ssot.py",
        "check_ssot_magic_constants.py",
        "check_w4_silent_writes.py",
        "check_cache_prefix_stability.py",
    ]
    print(f"Gates to verify: {len(wave2_gates)}")
    print("Action: read each gate's SQL/logic, classify as RETIRE / THIN / KEEP")
    for g in wave2_gates:
        print(f"- ops_scripts/ci/{g}")

    # --- Wave 3: Tier 2 P-view consumer check ---
    print("\n## Wave 3 — Tier 2 P-view consumer verification\n")
    wave3_gates = [
        "check_layer_skip.py",
        "check_w5_untyped_seam.py",
        "check_w4_uwg_bypass_pview.py",
        "check_lpg_drift_ratchet.py",
        "check_l1_plan_contract_fields.py",
        "check_waiver_provenance.py",
        "check_w4_exit_disposition.py",
        "check_w5_structured_output.py",
        "check_w4_replay_surface_gaps.py",
    ]
    print(f"Gates to verify: {len(wave3_gates)}")
    print("Action: confirm each gate SELECTs from the right P-view / MV (not re-derives)")
    for g in wave3_gates:
        print(f"- ops_scripts/ci/{g}")

    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
