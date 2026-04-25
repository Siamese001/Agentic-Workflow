import sqlite3, glob, os, sys

snap = sorted(glob.glob("artifacts/adg/adg_indexed_*.sqlite"))[-1]
print("snapshot:", os.path.basename(snap))
con = sqlite3.connect(f"file:{snap}?mode=ro", uri=True)
cur = con.cursor()
targets = [
    ".windsurf/scripts/post_cascade_deferred_scope_capture.py",
    "tools/priority/deferred_scope_scorer.py",
    "tools/otel/otel_mcp_server.py",
]
for path in targets:
    cur.execute(
        "SELECT COUNT(*) FROM edges e JOIN nodes n ON e.dst_id=n.id "
        "WHERE n.resolved_path LIKE ? AND e.relation_type='imports'",
        (f"%{path}%",),
    )
    print(f"{path}: fan_in(imports)={cur.fetchone()[0]}")
