import sqlite3
from pathlib import Path

p = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"), key=lambda x: x.stat().st_mtime)[-1]
c = sqlite3.connect(p)
print(f"snap: {p.name}\n")
for mv in [
    "mv_l2_phase_coverage",
    "mv_exit_disposition_coverage",
    "mv_trace_replay_eval_gaps",
    "mv_eval_coverage_by_path",
    "mv_handoff_witness_tiers",
    "mv_cross_cutting_witness_tiers",
    "mv_graph_reverse_dependency_hotspots",
    "mv_hotspot_centrality",
]:
    cols = [r[1] for r in c.execute(f"PRAGMA table_info({mv})")]
    print(f"{mv}:")
    print(f"  cols: {cols}")
    row = c.execute(f"SELECT * FROM {mv} LIMIT 1").fetchone()
    print(f"  sample: {row}\n")
print("--- AP/defect/violation tables ---")
for r in c.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view')"):
    n = r[0]
    if (
        "antipattern" in n.lower()
        or "defect" in n.lower()
        or "violation" in n.lower()
        or "burndown" in n.lower()
    ):
        cnt = c.execute(f"SELECT COUNT(*) FROM {n}").fetchone()[0]
        print(f"  {n}: {cnt}")
