"""Compare new vs old MEDIUM antipattern snapshots to find delta."""

import sqlite3

NEW = r"C:\Users\amita\AppData\Local\Temp\adg_temp_xu2pk4f7\adg\adg_indexed_04162026_2149.sqlite"
OLD = r"C:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_04152026_1108.sqlite"


def medium_rows(db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute(
        "SELECT file_path, line_no, evidence FROM violations "
        "WHERE severity='MEDIUM' AND category='antipattern'"
    )
    return set(cur.fetchall())


new_rows = medium_rows(NEW)
old_rows = medium_rows(OLD)
print(f"NEW total: {len(new_rows)}")
print(f"OLD total: {len(old_rows)}")

added = new_rows - old_rows
removed = old_rows - new_rows
print(f"Added (in new, not old): {len(added)}")
print(f"Removed (in old, not new): {len(removed)}")
print(f"Net delta: {len(added) - len(removed)}")

from collections import Counter

print("\n=== ADDED by file ===")
add_files = Counter(f for f, _, _ in added)
for f, c in add_files.most_common(30):
    print(f"  {c:4d}  {f}")

print("\n=== ADDED by evidence kind ===")
add_kind = Counter(e for _, _, e in added)
for e, c in add_kind.most_common(15):
    print(f"  {c:4d}  {e[:120]}")

print("\n=== REMOVED by file ===")
rm_files = Counter(f for f, _, _ in removed)
for f, c in rm_files.most_common(20):
    print(f"  {c:4d}  {f}")
