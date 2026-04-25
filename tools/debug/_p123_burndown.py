"""P1/P2/P3 burndown report — gross (pre-exemption MV rows) vs net (gate-filtered)."""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

SNAP = sorted((ROOT / "artifacts/adg").glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime)[-1]
conn = sqlite3.connect(SNAP)
print(f"Snapshot: {SNAP.name}\n")


def count(sql: str, params=()) -> int:
    try:
        return conn.execute(sql, params).fetchone()[0]
    except sqlite3.Error as e:
        return -1


def mv_exists(name: str) -> bool:
    return (
        count(
            "SELECT COUNT(*) FROM sqlite_master WHERE type IN ('table','view') AND name=?",
            (name,),
        )
        > 0
    )


# ---------------------------------------------------------------------------
# P1 — 13 gates
# ---------------------------------------------------------------------------
print("=" * 78)
print("P1 — Structural Conformance (4 view-backed) + M-series (6 delta ratchets)")
print("   + Anti-pattern ratchets (2 scripts) + Arch-Witness (1)")
print("=" * 78)

# Structural-conformance MVs — show row counts + any defect/gap_type filter
p1_mvs = [
    ("G-P1-LIFE", "mv_l2_phase_coverage", "phase_coverage_pct < 100 OR phase_coverage_pct IS NULL"),
    ("G-P1-LIFE", "mv_exit_disposition_coverage", "exit_coverage_pct < 100 OR exit_coverage_pct IS NULL"),
    ("G-P1-TRACE", "mv_trace_replay_eval_gaps", None),
    ("G-P1-TRACE", "mv_eval_coverage_by_path", None),
    ("G-P1-PROMPT-WIRING", "mv_prompt_assembly_wiring", None),
    ("G-P1-ARCH-WITNESS", "mv_handoff_witness_tiers", None),
    ("G-P1-ARCH-WITNESS", "mv_cross_cutting_witness_tiers", None),
]

print(f"\n{'Gate':<22}{'MV':<40}{'Rows':>8}  Filter")
print("-" * 78)
for gate_id, mv, flt in p1_mvs:
    if not mv_exists(mv):
        print(f"{gate_id:<22}{mv:<40}{'MISSING':>8}")
        continue
    rows = count(f"SELECT COUNT(*) FROM {mv}")
    flt_rows = count(f"SELECT COUNT(*) FROM {mv} WHERE {flt}") if flt else rows
    flt_note = f" WHERE {flt}" if flt else ""
    print(f"{gate_id:<22}{mv:<40}{rows:>8}  total rows{flt_note}")
    if flt:
        print(f"{'':<22}{'':<40}{flt_rows:>8}  filtered (gap present)")

# M-gates use redis_gpc baseline; no MV to query here.
print("\nM-series (G-M1..M6): redis_gpc delta ratchets — require baseline comparison.")
print("Current snapshot vs baseline deltas printed by gate_m_gates runner.")

# Anti-pattern / skip ratchets — use antipatterns table
if mv_exists("antipatterns"):
    print(f"\n{'G-P1-HARDEN':<22}antipatterns (all detectors)")
    cur = conn.execute("SELECT detector, COUNT(*) AS n FROM antipatterns GROUP BY detector ORDER BY n DESC")
    total_ap = 0
    for det, n in cur.fetchall():
        print(f"{'':<22}  {det:<40}{n:>8}")
        total_ap += n
    print(f"{'':<22}  {'TOTAL':<40}{total_ap:>8}")

if mv_exists("skip_file_ratchet"):
    print(f"\n{'G-P1-SKIP':<22}skip_file_ratchet")
    rows = count("SELECT COUNT(*) FROM skip_file_ratchet")
    print(f"{'':<22}  rows: {rows}")

# ---------------------------------------------------------------------------
# P2 — 3 gates
# ---------------------------------------------------------------------------
print("\n" + "=" * 78)
print("P2 — Hygiene (drift, burndown, centrality)")
print("=" * 78)

# G-P2-DRIFT — drift_ratchet_gate — typically compares snapshot deltas
# G-P2-BURNDOWN — adg_burndown_gate — aggregates antipattern counts vs ceilings
# G-P2-CENTRALITY — centrality_gate — centrality thresholds
p2_mvs = [
    ("G-P2-DRIFT", "mv_snapshot_baseline"),
    ("G-P2-BURNDOWN", "antipatterns"),
    ("G-P2-CENTRALITY", "mv_hotspot_centrality"),
    ("G-P2-CENTRALITY", "mv_dependency_cone_risk"),
]
print(f"\n{'Gate':<22}{'MV':<40}{'Rows':>8}")
print("-" * 78)
for gate_id, mv in p2_mvs:
    if not mv_exists(mv):
        print(f"{gate_id:<22}{mv:<40}{'MISSING':>8}")
        continue
    rows = count(f"SELECT COUNT(*) FROM {mv}")
    print(f"{gate_id:<22}{mv:<40}{rows:>8}")

# Burndown: rolled anti-pattern counts by category with exempt filter
if mv_exists("antipatterns"):
    print("\n--- antipattern rollup by category (gross / net of guardian exemptions) ---")
    # Gross: all AP rows. Net: excluding guardian-exempted (code-level exemptions).
    # Cannot detect guardian exemptions from SQLite alone — they're comments.
    # Report gross per category. Net must come from gate runner.
    for det, gross in conn.execute(
        "SELECT detector, COUNT(*) FROM antipatterns GROUP BY detector ORDER BY COUNT(*) DESC"
    ):
        print(f"  {det:<50}{gross:>8} gross")

# ---------------------------------------------------------------------------
# P3 — 1 gate
# ---------------------------------------------------------------------------
print("\n" + "=" * 78)
print("P3 — Hygiene (fan-in triage)")
print("=" * 78)
p3_mvs = [
    ("G-P3-FANIN", "mv_reverse_dependency_hotspots"),
    ("G-P3-FANIN", "mv_graph_reverse_dependency_hotspots"),
]
print(f"\n{'Gate':<22}{'MV':<40}{'Rows':>8}")
print("-" * 78)
for gate_id, mv in p3_mvs:
    if not mv_exists(mv):
        print(f"{gate_id:<22}{mv:<40}{'MISSING':>8}")
        continue
    rows = count(f"SELECT COUNT(*) FROM {mv}")
    print(f"{gate_id:<22}{mv:<40}{rows:>8}")

conn.close()
