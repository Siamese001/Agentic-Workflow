import sqlite3
from pathlib import Path

for p in sorted(
    Path("artifacts/adg").glob("adg_indexed_*.sqlite"), key=lambda x: x.stat().st_mtime, reverse=True
)[:8]:
    c = sqlite3.connect(p)
    has_mv = any(
        r[0] == "mv_trace_replay_eval_gaps"
        for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    )
    n = (
        c.execute("SELECT COUNT(*) FROM mv_trace_replay_eval_gaps WHERE gap_type != 'ok'").fetchone()[0]
        if has_mv
        else "n/a"
    )
    print(f"  mtime={p.stat().st_mtime:.0f}  {p.name}  has_mv={has_mv}  gaps!=ok={n}")
    c.close()
