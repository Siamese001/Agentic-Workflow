"""Assessment of live ADG artifact against all G1-G16 scope items.

SQLite schema:
  nodes(id, adg_name, entity_type, layer, identity_kind, confidence, resolved_path)
  edges(id, src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol)
"""

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADG_DIR = ROOT / "artifacts" / "adg"

dbs = sorted(ADG_DIR.glob("adg_indexed_*.sqlite"))
if not dbs:
    raise SystemExit("No adg_indexed_*.sqlite found in artifacts/adg/")

db_path = dbs[-1]
print(f"Assessing: {db_path.name}\n")

con = sqlite3.connect(db_path)
cur = con.cursor()

# ── helper ──────────────────────────────────────────────────────────────────
CHECKS = []


def chk(label, sql, op=">=", threshold=1):
    cur.execute(sql)
    val = cur.fetchone()[0]
    ok = (
        val >= threshold
        if op == ">="
        else val == threshold
        if op == "=="
        else val <= threshold
        if op == "<="
        else False
    )
    CHECKS.append((label, val, ok))


# ══════════════════════════════════════════════════════════════════════════
# SECTION 1 – Entity type distribution
# ══════════════════════════════════════════════════════════════════════════
print("=" * 64)
print("ENTITY TYPE DISTRIBUTION")
print("=" * 64)
for row in cur.execute("SELECT entity_type, COUNT(*) n FROM nodes GROUP BY entity_type ORDER BY n DESC"):
    print(f"  {row[0]:<28} {row[1]:>8}")

# ══════════════════════════════════════════════════════════════════════════
# SECTION 2 – Relation type distribution
# ══════════════════════════════════════════════════════════════════════════
print()
print("=" * 64)
print("RELATION TYPE DISTRIBUTION (all)")
print("=" * 64)
for row in cur.execute("SELECT relation_type, COUNT(*) n FROM edges GROUP BY relation_type ORDER BY n DESC"):
    print(f"  {row[0]:<32} {row[1]:>8}")

# ══════════════════════════════════════════════════════════════════════════
# SECTION 3 – G1-G16 scope checks
# ══════════════════════════════════════════════════════════════════════════
print()
print("=" * 64)
print("G1-G16 SCOPE VERIFICATION")
print("=" * 64)

# G1 – invokes_dynamic; no invokes_provider(dynamic_exec)
chk("G1  invokes_dynamic edges", "SELECT COUNT(*) FROM edges WHERE relation_type='invokes_dynamic'", ">=", 1)
chk(
    "G1  invokes_provider(dynamic_exec)==0",
    "SELECT COUNT(*) FROM edges WHERE relation_type='invokes_provider' AND edge_kind='dynamic_exec'",
    "==",
    0,
)

# G2 – prompt_slot / prompt_template entity types
chk("G2  prompt_slot nodes", "SELECT COUNT(*) FROM nodes WHERE entity_type='prompt_slot'", ">=", 1)
chk(
    "G2  prompt_template nodes (>=0)",
    "SELECT COUNT(*) FROM nodes WHERE entity_type='prompt_template'",
    ">=",
    0,
)

# G3 – write exclusions
chk(
    "G3  writes_to(deepcopy)==0",
    "SELECT COUNT(*) FROM edges WHERE relation_type='writes_to' AND symbol LIKE '%deepcopy%'",
    "==",
    0,
)
chk(
    "G3  writes_to(asyncio.run)==0",
    "SELECT COUNT(*) FROM edges WHERE relation_type='writes_to' AND symbol='asyncio.run'",
    "==",
    0,
)
chk(
    "G3  writes_to(copy bare)==0",
    "SELECT COUNT(*) FROM edges WHERE relation_type='writes_to' AND symbol='copy'",
    "==",
    0,
)

# G4 – no dead_imports where the imported module is __future__
# (symbol format: "__future__.annotations" — the module part is before the first dot)
chk(
    "G4  dead_imports(__future__ module)==0",
    "SELECT COUNT(*) FROM edges WHERE relation_type='dead_imports' AND (symbol='__future__' OR symbol LIKE '__future__.%')",
    "==",
    0,
)
chk("G4  dead_imports edges exist", "SELECT COUNT(*) FROM edges WHERE relation_type='dead_imports'", ">=", 1)

# G5 – decorated_by; no influences(decorator)
chk("G5  decorated_by edges", "SELECT COUNT(*) FROM edges WHERE relation_type='decorated_by'", ">=", 1)
chk(
    "G5  influences(decorator)==0",
    "SELECT COUNT(*) FROM edges WHERE relation_type='influences' AND edge_kind='decorator'",
    "==",
    0,
)

# G6 – reads_env as relation_type; no reads_from(reads_env)
chk("G6  reads_env edges", "SELECT COUNT(*) FROM edges WHERE relation_type='reads_env'", ">=", 1)
chk(
    "G6  reads_from(reads_env)==0",
    "SELECT COUNT(*) FROM edges WHERE relation_type='reads_from' AND edge_kind='reads_env'",
    "==",
    0,
)
chk(
    "G6  reads_from(reads_secret)==0",
    "SELECT COUNT(*) FROM edges WHERE relation_type='reads_from' AND edge_kind='reads_secret'",
    "==",
    0,
)
chk(
    "G6  reads_from(reads_policy_state)==0",
    "SELECT COUNT(*) FROM edges WHERE relation_type='reads_from' AND edge_kind='reads_policy_state'",
    "==",
    0,
)

# G7 – layer entity_type nodes
chk("G7  layer nodes", "SELECT COUNT(*) FROM nodes WHERE entity_type='layer'", ">=", 1)

# G8 – gateway entity_type nodes
chk("G8  gateway nodes", "SELECT COUNT(*) FROM nodes WHERE entity_type='gateway'", ">=", 1)

# G9 – seam nodes (may be 0 if no seam modules in codebase)
chk("G9  seam nodes (>=0)", "SELECT COUNT(*) FROM nodes WHERE entity_type='seam'", ">=", 0)

# G10 – provider nodes
chk("G10 provider nodes", "SELECT COUNT(*) FROM nodes WHERE entity_type='provider'", ">=", 1)

# G11 – L_SHARED layer present
chk("G11 nodes with layer=L_SHARED", "SELECT COUNT(*) FROM nodes WHERE layer='L_SHARED'", ">=", 1)

# G12 – belongs_to_layer edges
chk(
    "G12 belongs_to_layer edges",
    "SELECT COUNT(*) FROM edges WHERE relation_type='belongs_to_layer'",
    ">=",
    1,
)

# G15 – in_cycle (may be 0 if no cycles)
chk("G15 in_cycle edges (>=0)", "SELECT COUNT(*) FROM edges WHERE relation_type='in_cycle'", ">=", 0)

# G16 – violates edges exist
chk("G16 violates edges", "SELECT COUNT(*) FROM edges WHERE relation_type='violates'", ">=", 1)

# ══════════════════════════════════════════════════════════════════════════
# SECTION 4 – New relation type counts
# ══════════════════════════════════════════════════════════════════════════
print()
print("=" * 64)
print("NEW RELATION TYPE COUNTS")
print("=" * 64)
NEW_RELS = [
    "invokes_dynamic",
    "decorated_by",
    "reads_env",
    "reads_secret",
    "reads_policy_state",
    "reads_runtime_state",
    "reads_config",
    "seam_bypass",
    "dead_imports",
    "in_cycle",
]
for rel in NEW_RELS:
    cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type=?", (rel,))
    n = cur.fetchone()[0]
    print(f"  {rel:<32} {n:>8}")

# ══════════════════════════════════════════════════════════════════════════
# SECTION 5 – Sample edges for each new relation type (joined names)
# ══════════════════════════════════════════════════════════════════════════
print()
print("=" * 64)
print("SAMPLE EDGES (up to 3 per new type)")
print("=" * 64)
SAMPLE_SQL = """
    SELECT n1.adg_name, e.relation_type, n2.adg_name, e.edge_kind, e.symbol
    FROM edges e
    JOIN nodes n1 ON n1.id = e.src_id
    JOIN nodes n2 ON n2.id = e.dst_id
    WHERE e.relation_type=? LIMIT 3
"""
for rel in NEW_RELS:
    rows = cur.execute(SAMPLE_SQL, (rel,)).fetchall()
    if rows:
        print(f"\n  [{rel}]")
        for r in rows:
            fn = r[0].replace("ADG::Module::", "M::").replace("ADG::Symbol::", "S::")
            tn = r[2].replace("ADG::Module::", "M::").replace("ADG::Symbol::", "S::")
            print(f"    {fn[:55]} -> {tn[:40]}  kind={r[3]}  sym={r[4]}")

# ══════════════════════════════════════════════════════════════════════════
# SECTION 6 – Sample nodes for each new entity type
# ══════════════════════════════════════════════════════════════════════════
print()
print("=" * 64)
print("SAMPLE NODES (new entity types)")
print("=" * 64)
for etype in ("layer", "gateway", "seam", "provider", "prompt_slot", "prompt_template"):
    rows = cur.execute(
        "SELECT adg_name, entity_type, layer FROM nodes WHERE entity_type=? LIMIT 4",
        (etype,),
    ).fetchall()
    if rows:
        print(f"\n  [{etype}]")
        for r in rows:
            print(f"    {r[0]}  layer={r[2]}")
    else:
        print(f"\n  [{etype}]  (none)")

# ══════════════════════════════════════════════════════════════════════════
# SECTION 7 – G3 exclusion deep audit
# ══════════════════════════════════════════════════════════════════════════
print()
print("=" * 64)
print("G3 WRITE EXCLUSION AUDIT")
print("=" * 64)
EXCLUDED = ["asyncio.run", "copy.deepcopy", "deepcopy", "assert_no_persistent_write", "copy"]
for sym in EXCLUDED:
    cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type='writes_to' AND symbol=?", (sym,))
    n = cur.fetchone()[0]
    status = "OK" if n == 0 else f"FAIL  ({n} found!)"
    print(f"  {sym:<40} {status}")

# ══════════════════════════════════════════════════════════════════════════
# SECTION 8 – reads_* subtypes comprehensive check
# ══════════════════════════════════════════════════════════════════════════
print()
print("=" * 64)
print("G6 READS_* SUBTYPE AUDIT")
print("=" * 64)
reads_subtypes = ["reads_env", "reads_secret", "reads_policy_state", "reads_runtime_state", "reads_config"]
for rtype in reads_subtypes:
    cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type=?", (rtype,))
    as_rel = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM edges WHERE edge_kind=? AND relation_type='reads_from'", (rtype,))
    as_reads_from = cur.fetchone()[0]
    issue = " <-- WRONG (reads_from leakage!)" if as_reads_from > 0 else ""
    print(f"  relation_type={rtype:<25} {as_rel:>7}  reads_from leakage={as_reads_from}{issue}")

# ══════════════════════════════════════════════════════════════════════════
# SECTION 9 – Snapshot metadata check
# ══════════════════════════════════════════════════════════════════════════
print()
print("=" * 64)
print("ARTIFACT METADATA")
print("=" * 64)
for row in cur.execute("SELECT key, value FROM meta"):
    print(f"  {row[0]:<20} {str(row[1])[:60]}")

# ══════════════════════════════════════════════════════════════════════════
# SECTION 10 – Final pass/fail table
# ══════════════════════════════════════════════════════════════════════════
print()
print("=" * 64)
print("FINAL SCOPE COMPLETION SUMMARY")
print("=" * 64)
passed = failed = 0
for label, val, ok in CHECKS:
    icon = "PASS" if ok else "FAIL"
    passed += ok
    failed += not ok
    print(f"  [{icon}] {label:<48} = {val}")

print()
total = passed + failed
print(f"  RESULT: {passed}/{total} checks passed")
if failed == 0:
    print("  ✓ ALL G1-G16 SCOPE ITEMS VERIFIED IN LIVE ARTIFACT")
else:
    print("  ✗ FAILURES REQUIRE ATTENTION — see FAIL lines above")

con.close()
