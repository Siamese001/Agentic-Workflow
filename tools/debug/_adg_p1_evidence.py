"""Inspect evidence field for P1 HIGH violations to understand actual kinds."""

import sqlite3
import json

DB = r"artifacts/adg/adg_indexed_04192026_1335.sqlite"
conn = sqlite3.connect(DB)
cur = conn.cursor()

# Sample 15 P1 HIGH violations with evidence
cur.execute("""
    SELECT id, file_path, line_no, category, evidence, violation_class
    FROM violations
    WHERE severity='HIGH'
    ORDER BY file_path, line_no
    LIMIT 15
""")
rows = cur.fetchall()

print("=== SAMPLE P1 HIGH VIOLATION EVIDENCE ===\n")
for r in rows:
    vid, fp, ln, cat, ev, vcls = r
    print(f"ID={vid}  {fp}:{ln}  cat={cat}  class={vcls}")
    if ev:
        try:
            ev_parsed = json.loads(ev)
            print(f"  evidence: {json.dumps(ev_parsed, indent=4)}")
        except (json.JSONDecodeError, ValueError):
            print(f"  evidence (raw): {ev[:400]}")
    print()

# Antipattern edges with semantic_type to see actual kinds
cur.execute("""
    SELECT e.id, e.source_file, e.line_no, e.edge_kind, e.symbol, e.semantic_type,
           n_src.adg_name, n_src.entity_type, n_src.layer
    FROM edges e
    JOIN nodes n_src ON e.src_id = n_src.id
    WHERE e.relation_type='antipattern'
    LIMIT 15
""")
rows2 = cur.fetchall()

print("\n=== SAMPLE ANTIPATTERN EDGES ===\n")
for r in rows2:
    eid, sf, ln, ek, sym, stype, name, etype, layer = r
    print(f"edge_id={eid}  {sf}:{ln}  edge_kind={ek}  symbol={sym}  semantic_type={stype}")
    print(f"  src: {name}  type={etype}  layer={layer}")
    print()

conn.close()
