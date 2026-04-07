"""Find the 3 remaining uncovered modules and their details."""

import glob
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

db = sorted(glob.glob(str(PROJECT_ROOT / "artifacts/adg/adg_indexed_*.sqlite")))[-1]
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row

src_mods = {
    r["resolved_path"]
    for r in conn.execute(
        "SELECT DISTINCT resolved_path FROM nodes "
        "WHERE entity_type='module' "
        "AND resolved_path LIKE 'agentic_core/%' "
        "AND resolved_path NOT LIKE '%__pycache__%' "
        "AND resolved_path NOT LIKE '%::%'",
    )
}

covered_raw = {
    r["src_file"].split("::")[0]
    for r in conn.execute(
        "SELECT DISTINCT n2.resolved_path as src_file "
        "FROM edges e "
        "JOIN nodes n1 ON e.src_id=n1.id "
        "JOIN nodes n2 ON e.dst_id=n2.id "
        "WHERE e.relation_type='imports' "
        "AND n1.resolved_path LIKE 'tests/%' "
        "AND n2.resolved_path LIKE 'agentic_core/%' "
        "AND n2.resolved_path NOT LIKE '%__pycache__%'",
    )
}
covered = covered_raw & src_mods
uncovered = sorted(src_mods - covered)

print(f"Uncovered modules ({len(uncovered)}):")
for m in uncovered:
    path = PROJECT_ROOT / m
    size = path.stat().st_size if path.exists() else -1
    print(f"  {m}  (size={size})")
    # Show stub path that would cover it
    parts = Path(m).parts
    stem = Path(m).stem
    parent_parts = list(parts[:-1])
    stub_dir = Path("tests") / "unit" / Path(*parent_parts)
    stub_name = f"test_{stem}_adg.py"
    stub_path = stub_dir / stub_name
    abs_stub = PROJECT_ROOT / stub_path
    print(f"    -> stub: {stub_path}  exists={abs_stub.exists()}")

conn.close()
