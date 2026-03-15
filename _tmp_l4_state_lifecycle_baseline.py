"""P3/L4 State Lifecycle Governance baseline audit."""

import glob
import sqlite3


def _count_distinct_sources(conn, relation_type, filter_clause=""):
    """Count distinct source files for a relation type."""
    filters = "AND source_file NOT LIKE '%test%' AND source_file NOT LIKE '%tests%' AND source_file NOT LIKE '%spec%' AND source_file NOT LIKE '%fixture%' AND source_file NOT LIKE '%mock%'"
    if filter_clause:
        filters = filter_clause
    cursor = conn.execute(
        f"SELECT COUNT(DISTINCT source_file) FROM edges WHERE relation_type=? {filters}",
        (relation_type,),
    )
    return cursor.fetchone()[0]


def _count_exported(conn, symbol, module_hint=""):
    """Count distinct source files exporting a symbol."""
    if module_hint:
        cursor = conn.execute(
            """
            SELECT COUNT(DISTINCT source_file)
            FROM edges
            WHERE symbol LIKE ? AND source_file LIKE ? AND source_file NOT LIKE '%test%' AND source_file NOT LIKE '%tests%' AND source_file NOT LIKE '%spec%' AND source_file NOT LIKE '%fixture%' AND source_file NOT LIKE '%mock%'
            """,
            (f"%{symbol}%", f"%{module_hint}%"),
        )
    else:
        cursor = conn.execute(
            """
            SELECT COUNT(DISTINCT source_file)
            FROM edges
            WHERE symbol LIKE ? AND source_file NOT LIKE '%test%' AND source_file NOT LIKE '%tests%' AND source_file NOT LIKE '%spec%' AND source_file NOT LIKE '%fixture%' AND source_file NOT LIKE '%mock%'
            """,
            (f"%{symbol}%",),
        )
    return cursor.fetchone()[0]


db = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))[-1]
conn = sqlite3.connect(db)
c = conn.cursor()

FILTERS = "AND source_file NOT LIKE '%test%' AND source_file NOT LIKE '%tests%' AND source_file NOT LIKE '%spec%' AND source_file NOT LIKE '%fixture%' AND source_file NOT LIKE '%mock%'"
L4_FILTER = f"AND source_file LIKE '%L4_persistence%' {FILTERS}"

print(f"DB: {db}\n")

print("=== State lifecycle governance baseline (non-test) ===")
for rel in (
    "reads_runtime_state",
    "writes_through",
    "writes_to",
    "snapshots_state",
    "state_lifecycle_emitted",
    "lifecycle_policy_applied",
    "state_archived",
    "state_deleted",
    "lifecycle_transition_recorded",
):
    total = _count_distinct_sources(conn, rel)
    l4 = _count_distinct_sources(conn, rel, L4_FILTER)
    print(f"  {rel:<45} total={total:4d}  L4={l4:4d}")

print("\n=== Key L4 state lifecycle symbols (non-test) ===")
for sym in (
    "StateLifecycleRecord",
    "apply_state_lifecycle_policy",
    "StateLifecycleContext",
    "LifecycleStatus",
    "RetentionClass",
    "state_namespace",
    "lifecycle_policy_id",
    "retention_class",
    "expiration_rule",
    "archival_rule",
    "deletion_rule",
    "created_at_tick",
    "last_accessed_tick",
    "last_mutated_tick",
    "lifecycle_status",
    "ACTIVE",
    "STALE",
    "EXPIRED",
    "ARCHIVED",
    "PENDING_DELETION",
    "DELETED",
    "SHORT_TERM",
    "MEDIUM_TERM",
    "LONG_TERM",
    "PERMANENT",
    "StateLifecycleError",
):
    count = _count_exported(conn, sym)
    print(f"  symbol:{sym:<40} sources={count:4d}")

print("\n=== L4 persistence source files (non-test) ===")
c.execute(
    f"SELECT DISTINCT source_file FROM edges WHERE source_file LIKE '%L4_persistence%' {FILTERS} ORDER BY source_file LIMIT 30"
)
for (f,) in c.fetchall():
    print(" ", f)

print("\n=== reads_runtime_state edges (non-test, up to 15) ===")
c.execute(
    f"SELECT DISTINCT source_file, relation_type, symbol FROM edges WHERE relation_type='reads_runtime_state' {FILTERS} LIMIT 15"
)
for r in c.fetchall():
    print(" ", r)

print("\n=== writes_through / writes_to edges (non-test, up to 15) ===")
c.execute(
    f"SELECT DISTINCT source_file, relation_type, symbol FROM edges WHERE relation_type IN ('writes_through', 'writes_to') {FILTERS} LIMIT 15"
)
for r in c.fetchall():
    print(" ", r)

print("\n=== snapshots_state edges (non-test, up to 15) ===")
c.execute(
    f"SELECT DISTINCT source_file, relation_type, symbol FROM edges WHERE relation_type='snapshots_state' {FILTERS} LIMIT 15"
)
for r in c.fetchall():
    print(" ", r)

conn.close()
