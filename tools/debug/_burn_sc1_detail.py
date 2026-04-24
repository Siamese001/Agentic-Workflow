"""Enumerate the 8 SC-1 gravity violations."""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
from tools.adg.core.guardian_filter import is_layer_violation_exempted  # noqa: E402

_FORBIDDEN = {
    "L0": {"L1", "L2", "L3", "L6"},
    "L1": {"L2", "L3", "L6"},
    "L2": {"L0", "L1", "L6"},
    "L3": {"L6"},
}

snap = sorted(Path("artifacts/adg").glob("adg_indexed_*.sqlite"), key=lambda x: x.stat().st_mtime)[-1]
print(f"snap: {snap.name}\n")
c = sqlite3.connect(str(snap))
rows = c.execute(
    """
    SELECT e.source_file, e.line_no, n_src.layer, n_dst.layer, e.relation_type, e.symbol, n_dst.resolved_path
    FROM edges e
    JOIN nodes n_src ON e.src_id = n_src.id
    JOIN nodes n_dst ON e.dst_id = n_dst.id
    WHERE e.relation_type = 'imports'
      AND n_src.layer IS NOT NULL
      AND n_dst.layer IS NOT NULL
      AND n_src.layer != n_dst.layer
    """
).fetchall()

found = []
for src_file, ln, sl, dl, rel, sym, dst_path in rows:
    if dl not in _FORBIDDEN.get(sl, set()):
        continue
    if is_layer_violation_exempted(src_file, ln, repo_root=Path.cwd()):
        continue
    found.append((sl, dl, src_file, ln, sym, dst_path))

print(f"{len(found)} SC-1 gravity violations (non-exempted):\n")
for sl, dl, src, ln, sym, dst in found:
    print(f"[{sl}->{dl}] {src}:{ln}  sym={sym}  dst={dst}")
