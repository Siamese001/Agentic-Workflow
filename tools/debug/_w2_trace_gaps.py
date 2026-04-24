"""Break down mv_trace_replay_eval_gaps by layer, path prefix, and gap type."""

import sqlite3
from collections import Counter
from pathlib import Path

p = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"), key=lambda x: x.stat().st_mtime)[-1]
c = sqlite3.connect(p)
print(f"snap: {p.name}\n")

cols = [r[1] for r in c.execute("PRAGMA table_info(mv_trace_replay_eval_gaps)")]
print(f"cols: {cols}\n")

total = c.execute("SELECT COUNT(*) FROM mv_trace_replay_eval_gaps").fetchone()[0]
print(f"total rows: {total}\n")

print("=== by gap_type ===")
for r in c.execute(
    "SELECT gap_type, COUNT(*) FROM mv_trace_replay_eval_gaps GROUP BY gap_type ORDER BY COUNT(*) DESC"
):
    print(f"  {r[0]:<30}{r[1]}")

print("\n=== by layer ===")
for r in c.execute(
    "SELECT layer, COUNT(*) FROM mv_trace_replay_eval_gaps GROUP BY layer ORDER BY COUNT(*) DESC"
):
    print(f"  {r[0]:<15}{r[1]}")

print("\n=== top 20 path prefixes ===")
by_prefix: Counter = Counter()
for (f,) in c.execute("SELECT file FROM mv_trace_replay_eval_gaps"):
    if f:
        parts = f.split("/")
        by_prefix["/".join(parts[:3])] += 1
for k, n in by_prefix.most_common(20):
    print(f"  {n:5d}  {k}")

print("\n=== sample 10 ===")
for r in c.execute(
    "SELECT layer, file, has_trace, has_replay_link, has_eval, gap_type FROM mv_trace_replay_eval_gaps LIMIT 10"
):
    print(f"  [{r[0]}] t={r[2]} r={r[3]} e={r[4]}  {r[1]}  ({r[5]})")
