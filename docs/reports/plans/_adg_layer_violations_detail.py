#!/usr/bin/env python3
"""Get exact import details for each of the 7 violating files."""
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
db = sorted((ROOT / "artifacts/adg").glob("adg_indexed_*.sqlite"), reverse=True)[0]
con = sqlite3.connect(str(db))
con.row_factory = sqlite3.Row

def q(sql, params=()):
    return con.execute(sql, params).fetchall()

VIOLATING = [
    'agentic_core/L0_routing/scripts/bulk_hierarchy_heal_util.py',
    'agentic_core/L0_routing/scripts/flatten_scripts_directory_util.py',
    'agentic_core/L0_routing/scripts/populate_ssot_folders_util.py',
    'agentic_core/L0_routing/scripts/validate_sovereign_structure_util.py',
    'agentic_core/L0_routing/utils/fix_all_tunnels_util.py',
    'agentic_core/L1_cognition/utils/constants_util.py',
    'agentic_core/L2_execution/enforcement/sovereign_filesystem_mcp.py',
]

for fpath in VIOLATING:
    print(f"\n{'='*60}")
    print(f"FILE: {fpath}")
    imports = q("""
        SELECT e.symbol, n_dst.adg_name, n_dst.layer, n_dst.resolved_path
        FROM edges e
        LEFT JOIN nodes n_dst ON n_dst.id = e.dst_id
        WHERE e.source_file = ?
          AND e.relation_type = 'imports'
          AND (n_dst.layer = 'L5' OR n_dst.adg_name LIKE '%L5_safety%')
        ORDER BY e.symbol
    """, (fpath,))
    print(f"  L5 imports ({len(imports)}):")
    for r in imports:
        print(f"    [{r['symbol']}]  from {r['resolved_path']}")

con.close()
