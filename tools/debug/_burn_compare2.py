import sqlite3
from pathlib import Path

for name in ["adg_indexed_04242026_0622.sqlite", "adg_indexed_04242026_0625.sqlite", "adg_indexed_04242026_0620.sqlite"]:
    p = Path(f"artifacts/adg/{name}")
    if not p.exists():
        print(f"{name}: MISSING"); continue
    c = sqlite3.connect(str(p))
    try:
        n_nodes = c.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        n_edges = c.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
        # find replay_key
        row = c.execute("SELECT id FROM nodes WHERE resolved_path LIKE '%replay_key.py' AND entity_type='module'").fetchone()
        imps = 0
        if row:
            imps = c.execute(
                "SELECT COUNT(*) FROM edges e JOIN nodes s ON s.id=e.src_id WHERE e.dst_id=? AND e.relation_type='imports'",
                (row[0],)
            ).fetchone()[0]
        # what does __init__ import?
        init_row = c.execute("SELECT id FROM nodes WHERE resolved_path='agentic_core/L4_state/cache/__init__.py'").fetchone()
        init_imports = 0
        if init_row:
            init_imports = c.execute(
                "SELECT COUNT(*) FROM edges WHERE src_id=? AND relation_type='imports'",
                (init_row[0],)
            ).fetchone()[0]
        print(f"{name}: size={p.stat().st_size:>12}  nodes={n_nodes}  edges={n_edges}  replay_key_importers={imps}  __init___imports={init_imports}")
    finally:
        c.close()
