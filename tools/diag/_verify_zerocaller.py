"""Quick probe: count imports fan-in for each approved semcache adapter via ADG."""

from __future__ import annotations

import sqlite3
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
dbs = sorted((REPO / "artifacts" / "adg").glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime_ns)
db = dbs[-1]
print(f"DB: {db}")

conn = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
cur = conn.cursor()


def _query_and_print(cur: sqlite3.Cursor, path: str) -> None:
    cur.execute(
        "SELECT COUNT(*) FROM edges e JOIN nodes n_node ON e.dst_id=n_node.id "
        "WHERE e.relation_type='imports' AND n_node.resolved_path=?",
        (path,),
    )
    (c,) = cur.fetchone()
    print(f"  {c:>4}  {path}")


paths = [
    "agentic_core/L4_state/utils/memory/semantic_cache_manager.py",
    "agentic_core/L4_state/utils/memory/sovereign_semantic_cache.py",
    "agentic_core/L4_state/cache/gptcache_client.py",
    "agentic_core/embeddings/embedding_factory.py",
]
from tqdm import tqdm  # noqa: E402 -- §16 progress bar

for p in tqdm(paths, desc="fanin probe", unit="target"):
    _query_and_print(cur, p)

print("\nv_p1_zero_caller_infra:")
cur.execute("SELECT * FROM v_p1_zero_caller_infra LIMIT 50")
rows = cur.fetchall()
print(f"  {len(rows)} row(s)")
for row in rows:
    print(f"    {row}")
