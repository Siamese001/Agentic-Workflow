#!/usr/bin/env python3
"""Check LAYER_PREFIX_EXEMPT_TERRITORIES - where defined, where imported, gap status."""
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

db = sorted((ROOT / "artifacts/adg").glob("adg_indexed_*.sqlite"), reverse=True)[0]
con = sqlite3.connect(str(db))
con.row_factory = sqlite3.Row

def q(sql, params=()):
    return con.execute(sql, params).fetchall()

print("=== ADG: LAYER_PREFIX_EXEMPT_TERRITORIES nodes ===")
nodes = q("""
    SELECT id, adg_name, entity_type, layer, resolved_path
    FROM nodes WHERE adg_name LIKE '%LAYER_PREFIX_EXEMPT%'
""")
for n in nodes:
    print(f"  [{n['entity_type']}] {n['adg_name']}")
    print(f"    layer={n['layer']}  path={n['resolved_path']}")

print("\n=== ADG: import edges for LAYER_PREFIX_EXEMPT_TERRITORIES ===")
edges = q("""
    SELECT e.source_file, n_dst.adg_name, e.symbol, e.relation_type
    FROM edges e
    LEFT JOIN nodes n_dst ON n_dst.id = e.dst_id
    WHERE e.symbol LIKE '%LAYER_PREFIX_EXEMPT%'
""")
for e in edges:
    print(f"  [{e['relation_type']}] {e['source_file']}  [{e['symbol']}]")

con.close()

print("\n=== Runtime check: is it in structure_blueprint? ===")
from agentic_core.L5_safety.config import structure_blueprint as sb
from agentic_core.L5_safety.config import structure_blueprint_config as sbc

has_sb = hasattr(sb, 'LAYER_PREFIX_EXEMPT_TERRITORIES')
has_sbc = hasattr(sbc, 'LAYER_PREFIX_EXEMPT_TERRITORIES')
print(f"  structure_blueprint:        hasattr={has_sb}")
print(f"  structure_blueprint_config: hasattr={has_sbc}")

if has_sb:
    val = sb.LAYER_PREFIX_EXEMPT_TERRITORIES
    print(f"  value type: {type(val).__name__}  value: {val}")
    print(f"  in pkg __all__: {'LAYER_PREFIX_EXEMPT_TERRITORIES' in getattr(sb, '__all__', [])}")

print("\n=== Find which file defines it ===")
import ast
import os

target = 'LAYER_PREFIX_EXEMPT_TERRITORIES'
for dirpath, _, fnames in os.walk(str(ROOT / "agentic_core")):
    for fname in fnames:
        if not fname.endswith('.py'):
            continue
        fpath = Path(dirpath) / fname
        try:
            tree = ast.parse(fpath.read_text(encoding='utf-8', errors='replace'))
        except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AugAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for t in targets:
                    if isinstance(t, ast.Name) and t.id == target:
                        rel = fpath.relative_to(ROOT)
                        print(f"  DEFINED in: {rel}:{node.lineno}")