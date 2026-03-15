"""P2/L4 State Versioning baseline audit."""

import glob
import sqlite3

db = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))[-1]
conn = sqlite3.connect(db)
c = conn.cursor()

FILTERS = "AND source_file NOT LIKE '%test%' AND source_file NOT LIKE '%tests%' AND source_file NOT LIKE '%spec%' AND source_file NOT LIKE '%fixture%' AND source_file NOT LIKE '%mock%'"
L4_FILTER = f"AND source_file LIKE '%L4%' {FILTERS}"

print(f"DB: {db}\n")

print("=== Runtime edge counts (non-test) ===")
for rel in (
    "snapshots_state",
    "reads_runtime_state",
    "observes_runtime_state",
    "writes_through",
    "records_execution_trace",
    "state_transition_committed",
    "state_version_increments",
    "conflict_detected",
    "snapshot_policy_applied",
):
    c.execute(f"SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type=? {FILTERS}", (rel,))
    total = c.fetchone()[0]
    c.execute(f"SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type=? {L4_FILTER}", (rel,))
    l4 = c.fetchone()[0]
    print(f"  {rel:<45} total={total:4d}  L4={l4:4d}")

print("\n=== L4 key symbols (non-test) ===")
for sym in (
    "StateTransitionRecord",
    "StateVersionRegistry",
    "StateSnapshot",
    "commit_versioned_state_transition",
    "StateConflictError",
    "StateVersionMissingError",
    "StateSnapshotMissingError",
    "state_transition_id",
    "state_namespace",
    "previous_version",
    "new_version",
    "mutation_hash",
    "actor_id",
    "cause_hash",
    "snapshot_required_flag",
    "state_version",
    "source_hash",
    "get_state_version_registry",
    "get_state_transition_store",
):
    c.execute(f"SELECT COUNT(DISTINCT source_file) FROM edges WHERE symbol LIKE ? {FILTERS}", (f"%{sym}%",))
    n = c.fetchone()[0]
    print(f"  symbol:{sym:<40} sources={n:4d}")

print("\n=== L4 non-test source files ===")
c.execute(
    f"SELECT DISTINCT source_file FROM edges WHERE source_file LIKE '%L4%' {FILTERS} ORDER BY source_file LIMIT 60"
)
for (f,) in c.fetchall():
    print(" ", f)

print("\n=== L4 state mutation / versioning symbols ===")
c.execute(
    f"SELECT DISTINCT source_file, symbol FROM edges WHERE (symbol LIKE '%state%' OR symbol LIKE '%State%' OR symbol LIKE '%version%' OR symbol LIKE '%Version%') {L4_FILTER} LIMIT 40"
)
for r in c.fetchall():
    print(" ", r)

print("\n=== snapshots_state edges (non-test, up to 20) ===")
c.execute(
    f"SELECT DISTINCT source_file, relation_type, symbol FROM edges WHERE relation_type='snapshots_state' {FILTERS} LIMIT 20"
)
for r in c.fetchall():
    print(" ", r)

print("\n=== reads_runtime_state edges (non-test, up to 20) ===")
c.execute(
    f"SELECT DISTINCT source_file, relation_type, symbol FROM edges WHERE relation_type='reads_runtime_state' {FILTERS} LIMIT 20"
)
for r in c.fetchall():
    print(" ", r)

conn.close()
