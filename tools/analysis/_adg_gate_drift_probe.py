"""Probe gate_self_consistency + A12 edges."""

# W6 ADG consumer mode declaration (per .windsurf/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import sqlite3

c = sqlite3.connect("artifacts/adg/adg_indexed_04252026_0843.sqlite")
print("=== gate_self_consistency inconsistent rows ===")
for r in c.execute(
    "SELECT gate_file, claim_phrase, sql_snippet FROM gate_self_consistency WHERE consistent=0"
):
    print(r)

print("\n=== edges where relation_type=gate_self_test (first 30) ===")
for r in c.execute(
    "SELECT src_id, tgt_id, relation_type, confidence FROM edges "
    "WHERE relation_type='gate_self_test' LIMIT 30"
):
    print(r)

total = c.execute("SELECT COUNT(*) FROM edges WHERE relation_type='gate_self_test'").fetchone()[0]
print(f"\ntotal gate_self_test edges: {total}")

# Break down edges by target node kind
print("\n=== edges grouped by target adg_name (gate_self_test) ===")
rows = c.execute(
    """
    SELECT n_src.adg_name as src_name, n_tgt.adg_name as tgt_name, e.confidence
    FROM edges e
    JOIN nodes n_src ON e.src_id = n_src.id
    JOIN nodes n_tgt ON e.tgt_id = n_tgt.id
    WHERE e.relation_type='gate_self_test'
    LIMIT 30
    """
).fetchall()
for r in rows:
    print(r)
