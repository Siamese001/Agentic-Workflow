"""Check how ADG detects each P0 signal — look at the ADG builder source."""

import glob
import os
import sqlite3

files = glob.glob("artifacts/adg/adg_indexed_*.sqlite")
latest = max(files, key=os.path.getmtime)
conn = sqlite3.connect(latest)
cur = conn.cursor()

# What symbols trigger each edge type?
for rel in [
    "records_execution_trace",
    "signs_execution_trace",
    "applies_guardrail",
    "agent_executes_agent",
    "observes_runtime_state",
    "snapshots_state",
    "writes_through",
    "validated_by_safety_plane",
]:
    cur.execute(
        """
        SELECT DISTINCT e.symbol
        FROM edges e WHERE e.relation_type=?
        LIMIT 10
    """,
        (rel,),
    )
    rows = cur.fetchall()
    syms = [r[0] for r in rows if r[0]]
    print(f"{rel:40s}: {syms[:5]}")

conn.close()

# Also scan ADG builder for pattern definitions
import pathlib

adg_src = pathlib.Path("tools/adg")
for f in adg_src.rglob("*.py"):
    txt = f.read_text(encoding="utf-8", errors="ignore")
    for sig in [
        "records_execution_trace",
        "signs_execution_trace",
        "applies_guardrail",
        "agent_executes_agent",
        "observes_runtime_state",
        "snapshots_state",
        "writes_through",
        "validated_by_safety_plane",
    ]:
        if sig in txt:
            lines = [ln.strip() for ln in txt.splitlines() if sig in ln]
            print(f"\n[{f.name}] {sig}:")
            for ln in lines[:6]:
                print(f"  {ln[:120]}")
