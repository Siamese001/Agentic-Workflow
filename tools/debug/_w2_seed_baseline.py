"""Seed trace_replay_eval_baseline.json with current gaps (one-time bootstrap)."""

import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SNAP = sorted((ROOT / "artifacts/adg").glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime)[-1]
BASELINE = ROOT / "artifacts/adg/ci_ratchets/trace_replay_eval_baseline.json"

print(f"Snapshot: {SNAP.name}")
c = sqlite3.connect(SNAP)
gaps = {
    f"{row[1]}:{row[0]}": True
    for row in c.execute("SELECT node_id, layer FROM mv_trace_replay_eval_gaps WHERE gap_type != 'ok'")
}
print(f"Current gap keys: {len(gaps)}")
coverage = {}
for layer, action_nodes, covered, gap_count, pct in c.execute(
    "SELECT layer, action_node_count, eval_covered_count, gap_count, coverage_pct "
    "FROM mv_eval_coverage_by_path"
):
    coverage[layer] = {
        "action_nodes": action_nodes,
        "coverage_pct": pct,
        "covered": covered,
        "gaps": gap_count,
    }
print(f"Layers in coverage: {len(coverage)}")

new_baseline = {"gaps": gaps, "coverage": coverage}
BASELINE.write_text(json.dumps(new_baseline, indent=2, sort_keys=True), encoding="utf-8")
print(f"Wrote {BASELINE.relative_to(ROOT)} ({BASELINE.stat().st_size} bytes)")
