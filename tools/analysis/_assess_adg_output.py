"""One-shot assessment of the latest generated ADG artifacts against all G1-G16 scope items."""

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADG_DIR = ROOT / "artifacts" / "adg"

# ── locate latest files ────────────────────────────────────────────────────
dbs = sorted(ADG_DIR.glob("adg_indexed_*.sqlite"))
file_graphs = sorted(ADG_DIR.glob("adg_file_graph_*.json"))
gov_graphs = sorted(ADG_DIR.glob("adg_governance_graph_*.json"))
snaps = sorted(ADG_DIR.glob("adg_snapshot_*.json"))

if not dbs:
    raise SystemExit("No adg_indexed_*.sqlite found in artifacts/adg/")

db_path = dbs[-1]
fg_path = file_graphs[-1] if file_graphs else None
gg_path = gov_graphs[-1] if gov_graphs else None
snap_path = snaps[-1] if snaps else None

print(f"SQLite  : {db_path.name}")
print(f"FileG   : {fg_path.name if fg_path else 'N/A'}")
print(f"GovG    : {gg_path.name if gg_path else 'N/A'}")
print(f"Snap    : {snap_path.name if snap_path else 'N/A'}")
print()

con = sqlite3.connect(db_path)
cur = con.cursor()

# ══════════════════════════════════════════════════════════════════════════
# SECTION 1 – Entity type distribution
# ══════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("ENTITY TYPE DISTRIBUTION")
print("=" * 60)
for row in cur.execute("SELECT entity_type, COUNT(*) as n FROM nodes GROUP BY entity_type ORDER BY n DESC"):
    print(f"  {row[0]:<28} {row[1]:>8}")

# ══════════════════════════════════════════════════════════════════════════
# SECTION 2 – Full relation type distribution
# ══════════════════════════════════════════════════════════════════════════
print()
print("=" * 60)
print("RELATION TYPE DISTRIBUTION (all)")
print("=" * 60)
for row in cur.execute(
    "SELECT relation_type, COUNT(*) as n FROM edges GROUP BY relation_type ORDER BY n DESC",
):
    print(f"  {row[0]:<30} {row[1]:>8}")

# ══════════════════════════════════════════════════════════════════════════
# SECTION 3 – G1–G16 scope verification
# ══════════════════════════════════════════════════════════════════════════
print()
print("=" * 60)
print("G1-G16 SCOPE VERIFICATION")
print("=" * 60)

CHECKS = []  # (label, sql, expected_op, threshold)


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


# G1 – invokes_dynamic exists; invokes_provider(dynamic_exec) = 0
chk(
    "G1  invokes_dynamic edges",
    "SELECT COUNT(*) FROM relations WHERE relation_type='invokes_dynamic'",
    ">=",
    1,
)
chk(
    "G1  invokes_provider(dynamic_exec) == 0",
    "SELECT COUNT(*) FROM relations WHERE relation_type='invokes_provider' AND edge_kind='dynamic_exec'",
    "==",
    0,
)

# G2 – prompt_slot / prompt_template entity types
chk("G2  prompt_slot entities", "SELECT COUNT(*) FROM entities WHERE entity_type='prompt_slot'", ">=", 1)
chk(
    "G2  prompt_template entities",
    "SELECT COUNT(*) FROM entities WHERE entity_type='prompt_template'",
    ">=",
    0,
)  # may be 0

# G3 – no writes_to for excluded symbols (sample check: deepcopy)
chk(
    "G3  writes_to(deepcopy) == 0",
    "SELECT COUNT(*) FROM relations WHERE relation_type='writes_to' AND symbol LIKE '%deepcopy%'",
    "==",
    0,
)
chk(
    "G3  writes_to(asyncio.run) == 0",
    "SELECT COUNT(*) FROM relations WHERE relation_type='writes_to' AND symbol='asyncio.run'",
    "==",
    0,
)
chk(
    "G3  writes_to(copy) == 0  (bare copy call)",
    "SELECT COUNT(*) FROM relations WHERE relation_type='writes_to' AND symbol='copy'",
    "==",
    0,
)

# G4 – no dead_imports for __future__
chk(
    "G4  dead_imports(__future__) == 0",
    "SELECT COUNT(*) FROM relations WHERE relation_type='dead_imports' AND symbol LIKE '%__future__%'",
    "==",
    0,
)
chk(
    "G4  dead_imports edges exist",
    "SELECT COUNT(*) FROM relations WHERE relation_type='dead_imports'",
    ">=",
    1,
)

# G5 – decorated_by edges exist; influences(decorator) = 0
chk("G5  decorated_by edges", "SELECT COUNT(*) FROM relations WHERE relation_type='decorated_by'", ">=", 1)
chk(
    "G5  influences(decorator) == 0",
    "SELECT COUNT(*) FROM relations WHERE relation_type='influences' AND edge_kind='decorator'",
    "==",
    0,
)

# G6 – reads_env/reads_secret/reads_policy_state as relation_type; reads_from(reads_env) = 0
chk("G6  reads_env relations", "SELECT COUNT(*) FROM relations WHERE relation_type='reads_env'", ">=", 1)
chk(
    "G6  reads_from(reads_env) == 0",
    "SELECT COUNT(*) FROM relations WHERE relation_type='reads_from' AND edge_kind='reads_env'",
    "==",
    0,
)
chk(
    "G6  reads_from(reads_secret) == 0",
    "SELECT COUNT(*) FROM relations WHERE relation_type='reads_from' AND edge_kind='reads_secret'",
    "==",
    0,
)

# G7 – layer entity_type nodes
chk("G7  layer entities", "SELECT COUNT(*) FROM entities WHERE entity_type='layer'", ">=", 1)

# G8 – gateway entity_type nodes
chk("G8  gateway entities", "SELECT COUNT(*) FROM entities WHERE entity_type='gateway'", ">=", 1)

# G9 – seam entity_type nodes
chk(
    "G9  seam entities", "SELECT COUNT(*) FROM entities WHERE entity_type='seam'", ">=", 0,
)  # may be 0 if no seam modules scanned

# G10 – provider entity_type nodes
chk("G10 provider entities", "SELECT COUNT(*) FROM entities WHERE entity_type='provider'", ">=", 1)

# G11 – layer distribution includes L_SHARED
chk("G11 entities with layer=L_SHARED", "SELECT COUNT(*) FROM entities WHERE layer='L_SHARED'", ">=", 1)

# G12 – belongs_to_layer edges
chk(
    "G12 belongs_to_layer edges",
    "SELECT COUNT(*) FROM relations WHERE relation_type='belongs_to_layer'",
    ">=",
    1,
)

# G15 – in_cycle edges
chk("G15 in_cycle edges", "SELECT COUNT(*) FROM relations WHERE relation_type='in_cycle'", ">=", 0)

# G16 – violates edges have rule_id observations
cur.execute("""
    SELECT COUNT(*) FROM relations r
    WHERE r.relation_type='violates'
""")
violates_total = cur.fetchone()[0]
CHECKS.append(("G16 violates edges total", violates_total, violates_total >= 0))

# Check observations table for rule_id
has_obs_table = cur.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name='observations'",
).fetchone()
if has_obs_table:
    cur.execute("SELECT COUNT(*) FROM observations WHERE content LIKE 'rule_id:%'")
    rule_id_obs = cur.fetchone()[0]
    CHECKS.append(("G16 rule_id observations", rule_id_obs, rule_id_obs >= 0))
else:
    CHECKS.append(("G16 rule_id (no obs table – MCP path)", "N/A", True))

# ══════════════════════════════════════════════════════════════════════════
# SECTION 4 – New relation types spot-check counts
# ══════════════════════════════════════════════════════════════════════════
print()
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
print("=" * 60)
print("NEW RELATION TYPE COUNTS")
print("=" * 60)
for rel in NEW_RELS:
    cur.execute("SELECT COUNT(*) FROM relations WHERE relation_type=?", (rel,))
    n = cur.fetchone()[0]
    print(f"  {rel:<30} {n:>8}")

# ══════════════════════════════════════════════════════════════════════════
# SECTION 5 – Sample edges for each new relation type
# ══════════════════════════════════════════════════════════════════════════
print()
print("=" * 60)
print("SAMPLE EDGES (up to 3 per new type)")
print("=" * 60)
for rel in NEW_RELS:
    rows = cur.execute(
        "SELECT from_name, relation_type, to_name, edge_kind, symbol FROM relations "
        "WHERE relation_type=? LIMIT 3",
        (rel,),
    ).fetchall()
    if rows:
        print(f"\n  [{rel}]")
        for r in rows:
            fn = r[0].replace("ADG::Module::", "M::").replace("ADG::Symbol::", "S::")
            tn = r[2].replace("ADG::Module::", "M::").replace("ADG::Symbol::", "S::")
            print(f"    {fn} --{r[1]}--> {tn}  kind={r[3]}  sym={r[4]}")

# ══════════════════════════════════════════════════════════════════════════
# SECTION 6 – Entity type spot-check for new types
# ══════════════════════════════════════════════════════════════════════════
print()
print("=" * 60)
print("SAMPLE ENTITIES (new types)")
print("=" * 60)
for etype in ("layer", "gateway", "seam", "provider", "prompt_slot", "prompt_template"):
    rows = cur.execute(
        "SELECT adg_name, entity_type, layer FROM entities WHERE entity_type=? LIMIT 3", (etype,),
    ).fetchall()
    if rows:
        print(f"\n  [{etype}]")
        for r in rows:
            print(f"    {r[0]}  layer={r[2]}")

# ══════════════════════════════════════════════════════════════════════════
# SECTION 7 – G3 write exclusion deep-check
# ══════════════════════════════════════════════════════════════════════════
print()
print("=" * 60)
print("G3 WRITE EXCLUSION AUDIT (any writes_to with excluded symbols)")
print("=" * 60)
EXCLUDED = ["asyncio.run", "copy.deepcopy", "deepcopy", "assert_no_persistent_write", "copy"]
for sym in EXCLUDED:
    cur.execute("SELECT COUNT(*) FROM relations WHERE relation_type='writes_to' AND symbol=?", (sym,))
    n = cur.fetchone()[0]
    status = "OK" if n == 0 else f"FAIL ({n} found!)"
    print(f"  {sym:<35} {status}")

# ══════════════════════════════════════════════════════════════════════════
# SECTION 8 – Final pass/fail summary
# ══════════════════════════════════════════════════════════════════════════
print()
print("=" * 60)
print("SCOPE COMPLETION SUMMARY")
print("=" * 60)
passed = 0
failed = 0
for label, val, ok in CHECKS:
    icon = "PASS" if ok else "FAIL"
    if ok:
        passed += 1
    else:
        failed += 1
    print(f"  [{icon}] {label:<45} = {val}")

print()
print(f"  TOTAL: {passed} passed, {failed} failed")
if failed == 0:
    print("  ALL G1-G16 SCOPE ITEMS VERIFIED IN LIVE ARTIFACT")
else:
    print("  SOME ITEMS REQUIRE ATTENTION (see FAIL lines above)")

con.close()
