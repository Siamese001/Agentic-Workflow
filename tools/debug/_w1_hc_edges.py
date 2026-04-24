"""Find the edge_kind and guardian-match state for each HIGH+CRITICAL violation."""
import sqlite3
from pathlib import Path
p = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"),
           key=lambda x: x.stat().st_mtime)[-1]
c = sqlite3.connect(p)
print(f"snap: {p.name}\n")
print(f"{'Sev':<10}{'EdgeKind':<26}{'Evidence':<25}{'File:Line'}")
print("-" * 130)
for r in c.execute("""
    SELECT v.severity, COALESCE(e.edge_kind,'(no-edge)'), v.evidence, v.file_path, v.line_no,
           v.edge_id, e.relation_type
    FROM violations v
    LEFT JOIN edges e ON v.edge_id = e.id
    WHERE v.severity IN ('HIGH','CRITICAL')
    ORDER BY v.severity DESC, v.file_path
"""):
    sev, ek, ev, fp, ln, eid, rel = r
    print(f"{sev:<10}{str(ek):<26}{str(ev)[:23]:<25}{fp}:{ln}  (edge_id={eid}, rel={rel})")
