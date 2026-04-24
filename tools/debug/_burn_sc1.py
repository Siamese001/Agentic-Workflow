"""Inspect SC-1 layer violations."""
import sqlite3
from pathlib import Path

snap = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"), key=lambda x: x.stat().st_mtime)[-1]
print(f"snap: {snap.name}\n")
c = sqlite3.connect(str(snap))
# Find SC-1 / layer_violation violations
rows = c.execute(
    """
    SELECT v.id, v.severity, v.violation_class, e.edge_kind, e.source_file, e.line_no,
           e.symbol, src.layer AS src_layer, dst.resolved_path, dst.layer AS dst_layer
    FROM violations v
    JOIN edges e ON v.edge_id = e.id
    JOIN nodes src ON e.src_id = src.id
    JOIN nodes dst ON e.dst_id = dst.id
    WHERE v.violation_class='structural_conformance'
    ORDER BY v.severity, e.source_file
    LIMIT 30
    """
).fetchall()
print(f"{len(rows)} SC rows:\n")
for vid, sev, vcls, kind, src, ln, sym, sl, dp, dl in rows:
    print(f"[{sev}] {kind}  {sl}->{dl}  {src}:{ln}  -> {dp}  sym={sym}")
