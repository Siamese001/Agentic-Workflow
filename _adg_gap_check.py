"""Cross-reference ADG SQLite uncovered modules against existing test files (recursive)."""
import sqlite3
import os

DB = r"artifacts/adg/adg_indexed_03122026.sqlite"
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

uncovered = conn.execute("""
    SELECT n.resolved_path
    FROM nodes n
    WHERE n.resolved_path LIKE '%/types/%'
      AND n.resolved_path NOT LIKE '%__init__%'
      AND n.resolved_path NOT LIKE 'tests/%'
      AND n.entity_type = 'module'
      AND NOT EXISTS (
          SELECT 1 FROM edges e2
          JOIN nodes src ON src.id = e2.src_id
          WHERE e2.dst_id = n.id
            AND e2.relation_type = 'covers'
      )
    ORDER BY n.resolved_path
""").fetchall()
conn.close()

# Build set of existing test file basenames recursively
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
    basename = os.path.basename(path).replace(".py", "")
    expected = f"test_{basename}_adg.py"
    # Also check non-_adg variant for older tests
    alt = f"test_{basename}.py"
    has_test = expected in existing_tests or alt in existing_tests
    if not has_test:
        still_missing.append((path, expected))

print(f"Still need tests ({len(still_missing)}):")
for path, expected in still_missing:
    print(f"  {path}  ->  {expected}")
