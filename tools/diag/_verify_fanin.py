"""Verify lazy-import ADG fan-in for known-orphan targets from the review."""

from __future__ import annotations

import sqlite3
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
db = sorted((REPO / "artifacts" / "adg").glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime_ns)[-1]
print(f"DB: {db}\n")

conn = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
cur = conn.cursor()

targets = [
    "agentic_core/L5_safety/enforcement/conf_calib_gate.py",
    "agentic_core/L5_safety/enforcement/d0_injection_engine_enforcer.py",
    "agentic_core/L5_safety/enforcement/mcp_sovereign_authority_enforcer.py",
    "agentic_core/L5_safety/reasoning/guardian_decision.py",
    "agentic_core/L5_safety/enforcement/activation_gate.py",
    "agentic_core/L4_state/enforcement/violation_event_store.py",
    "agentic_core/L4_state/utils/memory/in_memory_vector_store.py",
    "agentic_core/L4_state/utils/memory/runtime_state_guard.py",
    "agentic_core/L4_state/utils/storage/filesystem_store.py",
]
print(f"{'FANIN':>6}  TARGET")
print("-" * 100)
for p in targets:
    cur.execute(
        "SELECT COUNT(*) FROM edges e JOIN nodes n ON e.dst_id=n.id "
        "WHERE e.relation_type=? AND n.resolved_path=?",
        ("imports", p),
    )
    (c,) = cur.fetchone()
    print(f"  {c:>4}  {p}")
