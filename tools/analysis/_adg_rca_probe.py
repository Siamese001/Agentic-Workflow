"""Probe the ADG snapshot to RCA gaps that miss tech-debt patterns."""

# W6 ADG consumer mode declaration (per .codex/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import sqlite3, glob, os

db = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"), key=os.path.getmtime)[-1]
con = sqlite3.connect(db)
con.row_factory = sqlite3.Row
cur = con.cursor()


def section(title):
    print(f"\n=== {title} ===")


section("violations by category")
for r in cur.execute("SELECT category, COUNT(*) FROM violations GROUP BY category ORDER BY 2 DESC"):
    print(f"  {r[1]:6d}  {r[0]}")

section("violations by violation_class")
for r in cur.execute(
    "SELECT violation_class, COUNT(*) FROM violations GROUP BY violation_class ORDER BY 2 DESC"
):
    print(f"  {r[1]:6d}  {r[0]}")

section("violations by severity")
for r in cur.execute("SELECT severity, COUNT(*) FROM violations GROUP BY severity"):
    print(f"  {r[1]:6d}  {r[0]}")

section("top 20 violation evidence kinds")
for r in cur.execute("SELECT evidence, COUNT(*) FROM violations GROUP BY evidence ORDER BY 2 DESC LIMIT 20"):
    print(f"  {r[1]:6d}  {r[0]}")

section("imports — dynamic_resolution flag distribution")
for r in cur.execute(
    "SELECT dynamic_resolution, COUNT(*) FROM edges WHERE relation_type='imports' GROUP BY dynamic_resolution"
):
    print(f"  {r[1]:6d}  dynamic={r[0]}")

# Check whether import edges have a "resolved" flag — i.e. did the ADG mark
# any import as pointing at a non-existent module?
section("imports — distinct evidence/notes columns?")
print("  edges table columns:", [r[1] for r in cur.execute("PRAGMA table_info(edges)")])

# Check if there are any import edges where dst_id is null (signal of unresolved)
section("imports — dst_id NULL count (proxy for unresolved imports)")
n = cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type='imports' AND dst_id IS NULL").fetchone()[0]
print(f"  {n} imports edges have dst_id IS NULL")

# What about import edges where the dst module's resolved_path is empty?
section("imports — count where dst node has NULL resolved_path")
q = """
SELECT COUNT(*) FROM edges e
JOIN nodes n ON e.dst_id = n.id
WHERE e.relation_type = 'imports' AND (n.resolved_path IS NULL OR n.resolved_path = '')
"""
print(f"  {cur.execute(q).fetchone()[0]} imports point at nodes with empty resolved_path")

# Are there any nodes whose adg_name is recognized but file does not exist on disk?
section("nodes — adg_name pointing at non-existent file_path (sample)")
from pathlib import Path

REPO = Path(".").resolve()
missing = []
for r in cur.execute("SELECT id, adg_name, resolved_path FROM nodes WHERE entity_type='module' LIMIT 10000"):
    rp = r["resolved_path"]
    if rp and not (REPO / rp).exists():
        missing.append((r["adg_name"], rp))
print(
    f"  {len(missing)} module nodes claim a resolved_path that does not exist on disk (out of 10000 sampled)"
)
for adg_name, rp in missing[:10]:
    print(f"    {adg_name}  ->  {rp}")

# Are duplicate file pairs (P4) detectable from ADG alone?
section("are there nodes sharing identical file content hash? (no — ADG schema has no body_hash column)")
print(
    "  edges/nodes columns lack any 'body_hash' or 'content_sha' field; ADG does not currently fingerprint module bodies."
)

# Stale __all__ — is there a 'declared_export' edge?
section("are exports tracked? (P7: stale __all__)")
n_exp = cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type='exports'").fetchone()[0]
print(f"  {n_exp} 'exports' edges. Each represents one __all__ entry binding to a symbol.")
# Are there exports edges with dst_id NULL = stale __all__ entry pointing nowhere?
n_stale = cur.execute(
    "SELECT COUNT(*) FROM edges WHERE relation_type='exports' AND dst_id IS NULL"
).fetchone()[0]
print(f"  {n_stale} 'exports' edges have dst_id IS NULL (would be the P7 signal)")

# How many violations have evidence mentioning import / class / def?
section("violations with evidence containing 'import' or 'class' (text-search proxy)")
n1 = cur.execute("SELECT COUNT(*) FROM violations WHERE evidence LIKE '%import%'").fetchone()[0]
n2 = cur.execute("SELECT COUNT(*) FROM violations WHERE evidence LIKE '%class %'").fetchone()[0]
print(f"  evidence LIKE %import%:  {n1}")
print(f"  evidence LIKE %class %:  {n2}")
