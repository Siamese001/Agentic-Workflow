#!/usr/bin/env python3
"""
ADG follow-up queries:
1. Were the 7 layer violations pre-existing before the refactor?
2. Is ALLOW_ROOT_PY_TERRITORIES exported from structure_blueprint_config?
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
adg_dir = ROOT / "artifacts" / "adg"
sqlite_files = sorted(adg_dir.glob("adg_indexed_*.sqlite"), reverse=True)
DB_PATH = sqlite_files[0]
print(f"ADG: {DB_PATH.name}\n")

con = sqlite3.connect(str(DB_PATH))
con.row_factory = sqlite3.Row

def q(sql, params=()):
    return con.execute(sql, params).fetchall()

def section(t):
    print(f"\n{'='*72}\n  {t}\n{'='*72}")

# ─── Q1: What specifically do the 7 violating files import from L5? ───────────
section("Q1: Exact violation edges for each of the 7 files")

VIOLATING_FILES = [
    '%bulk_hierarchy_heal_util%',
    '%flatten_scripts_directory_util%',
    '%populate_ssot_folders_util%',
    '%validate_sovereign_structure_util%',
    '%fix_all_tunnels_util%',
    '%constants_util%',
    '%sovereign_filesystem_mcp%',
]

for pat in VIOLATING_FILES:
    fname = pat.strip('%')
    rows = q("""
        SELECT e.source_file, n_dst.adg_name, e.symbol, n_src.layer, n_dst.layer as dst_layer
        FROM edges e
        LEFT JOIN nodes n_src ON n_src.id = e.src_id
        LEFT JOIN nodes n_dst ON n_dst.id = e.dst_id
        WHERE e.relation_type = 'violates'
          AND e.source_file LIKE ?
    """, (pat,))
    if rows:
        for r in rows:
            print(f"  {r['source_file']}")
            print(f"    layer={r['layer']} violates ADG::Layer::{r['dst_layer']}  target={r['adg_name']}")

# ─── Q2: Were violations pre-existing? Check all L0→L5 violations globally ───
section("Q2: All L0/L1/L2 -> L5 import violations in graph (global count)")

all_l0_l5 = q("""
    SELECT e.source_file, n_dst.adg_name, e.relation_type
    FROM edges e
    LEFT JOIN nodes n_src ON n_src.id = e.src_id
    LEFT JOIN nodes n_dst ON n_dst.id = e.dst_id
    WHERE e.relation_type = 'violates'
      AND n_src.layer IN ('L0', 'L1', 'L2')
      AND (n_dst.layer = 'L5' OR n_dst.adg_name LIKE '%L5%')
    ORDER BY n_src.layer, e.source_file
    LIMIT 30
""")
print(f"  Total L0/L1/L2->L5 violation edges in graph: {len(all_l0_l5)}")
for r in all_l0_l5[:15]:
    print(f"    {r['source_file']} violates {r['adg_name']}")

# Also - total violation count to understand scope
total_violations = q("SELECT COUNT(*) as n FROM edges WHERE relation_type='violates'")[0]['n']
print(f"\n  Total graph-wide violations: {total_violations}")
print(f"  The 7 files = {7/total_violations*100:.1f}% of all violations")

# ─── Q3: Check if structure_blueprint_config is in an exempt path ─────────────
section("Q3: Is structure_blueprint_config exempt from layer gravity?")

# Check if structure_blueprint_config has a special layer assignment
sbc_node = q("""
    SELECT adg_name, entity_type, layer, identity_kind, resolved_path
    FROM nodes
    WHERE adg_name LIKE '%structure_blueprint_config%'
      AND entity_type = 'module'
    LIMIT 5
""")
print(f"  structure_blueprint_config module nodes: {len(sbc_node)}")
for n in sbc_node:
    print(f"    layer={n['layer']}  identity={n['identity_kind']}  path={n['resolved_path']}")

# ─── Q4: How many files total import from structure_blueprint_config ───────────
section("Q4: How many non-L5 files import structure_blueprint_config?")

all_sbc_importers = q("""
    SELECT n_src.layer, COUNT(DISTINCT e.source_file) as cnt
    FROM edges e
    LEFT JOIN nodes n_src ON n_src.id = e.src_id
    LEFT JOIN nodes n_dst ON n_dst.id = e.dst_id
    WHERE e.relation_type = 'imports'
      AND (n_dst.adg_name LIKE '%structure_blueprint_config%'
           OR n_dst.resolved_path LIKE '%structure_blueprint_config%')
    GROUP BY n_src.layer
    ORDER BY n_src.layer
""")
print("  Importers by layer:")
for r in all_sbc_importers:
    print(f"    layer={r['layer']}: {r['cnt']} file(s)")

# ─── Q5: ALLOW_ROOT_PY_TERRITORIES - is it exported? ─────────────────────────
section("Q5: ALLOW_ROOT_PY_TERRITORIES in graph")

arpt_nodes = q("""
    SELECT id, adg_name, entity_type, layer, resolved_path
    FROM nodes
    WHERE adg_name LIKE '%ALLOW_ROOT_PY%'
    ORDER BY adg_name
""")
print(f"  ALLOW_ROOT_PY_TERRITORIES nodes: {len(arpt_nodes)}")
for n in arpt_nodes:
    print(f"    [{n['entity_type']}] {n['adg_name']}  layer={n['layer']}  path={n['resolved_path']}")

# Check exports edges for it
arpt_exports = q("""
    SELECT e.source_file, n_dst.adg_name, e.relation_type
    FROM edges e
    LEFT JOIN nodes n_dst ON n_dst.id = e.dst_id
    WHERE n_dst.adg_name LIKE '%ALLOW_ROOT_PY%'
      AND e.relation_type IN ('exports', 'imports')
    LIMIT 10
""")
print(f"  Export/import edges for ALLOW_ROOT_PY_TERRITORIES: {len(arpt_exports)}")
for e in arpt_exports:
    print(f"    [{e['relation_type']}] {e['source_file']} -> {e['adg_name']}")

# ─── Q6: Check exports from structure_blueprint_config ────────────────────────
section("Q6: structure_blueprint_config exports (what it makes public)")

sbc_exports = q("""
    SELECT e.source_file, n_dst.adg_name, e.symbol
    FROM edges e
    LEFT JOIN nodes n_src ON n_src.id = e.src_id
    LEFT JOIN nodes n_dst ON n_dst.id = e.dst_id
    WHERE e.relation_type = 'exports'
      AND e.source_file LIKE '%structure_blueprint_config%'
      AND e.source_file NOT LIKE '%tests%'
    ORDER BY e.symbol
    LIMIT 40
""")
print(f"  Exported symbols from structure_blueprint_config: {len(sbc_exports)}")
for e in sbc_exports:
    print(f"    {e['symbol']}")

con.close()
