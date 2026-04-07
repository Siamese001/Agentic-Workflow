"""Cross-reference ADG SQLite uncovered modules against existing test files (recursive)."""

import os
import sqlite3
from pathlib import Path

DB = "artifacts/adg/adg_indexed_03122026.sqlite"
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
uncovered = conn.execute(
    "\n    SELECT n.resolved_path\n    FROM nodes n\n    WHERE n.resolved_path LIKE '%/types/%'\n      AND n.resolved_path NOT LIKE '%__init__%'\n      AND n.resolved_path NOT LIKE 'tests/%'\n      AND n.entity_type = 'module'\n      AND NOT EXISTS (\n          SELECT 1 FROM edges e2\n          JOIN nodes src ON src.id = e2.src_id\n          WHERE e2.dst_id = n.id\n            AND e2.relation_type = 'covers'\n      )\n    ORDER BY n.resolved_path\n",
).fetchall()
conn.close()
existing_tests = set()
for root, dirs, files in os.walk("tests"):
    for f in files:
        if f.startswith("test_") and f.endswith(".py"):
            existing_tests.add(f)
print(f"Total uncovered types modules from ADG SQLite: {len(uncovered)}")
print(f"Total test files found recursively: {len(existing_tests)}")
print()
still_missing = []
for row in uncovered:
    path = row["resolved_path"]
    basename = Path(path).name.replace(".py", "")
    expected = f"test_{basename}_adg.py"
    alt = f"test_{basename}.py"
    has_test = expected in existing_tests or alt in existing_tests
    if not has_test:
        still_missing.append((path, expected))
print(f"Still need tests ({len(still_missing)}):")
for path, expected in still_missing:
    print(f"  {path}  ->  {expected}")
