#!/usr/bin/env python3
"""Query ADG violations and categorize by type."""

import sqlite3
from collections import defaultdict
from pathlib import Path

ADG_PATH = Path("artifacts/adg/adg_indexed_04052026_1936.sqlite")

conn = sqlite3.connect(ADG_PATH)
cur = conn.cursor()

# Get all violations
cur.execute("""
    SELECT source_file, symbol, line_no
    FROM edges
    WHERE relation_type = 'violates'
    ORDER BY source_file, symbol
""")

violations = cur.fetchall()

# Group by violation type
by_type = defaultdict(list)
for source_file, symbol, line_no in violations:
    by_type[symbol].append((source_file, line_no))

print(f"Total violations: {len(violations)}")
print(f"Unique violation types: {len(by_type)}")
print()

print("Violation Types (sorted by count):")
for violation_type, files in sorted(by_type.items(), key=lambda x: len(x[1]), reverse=True):
    print(f"  {violation_type}: {len(files)} occurrences")

print()
print("Sample violations by type:")
for violation_type, files in sorted(by_type.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
    print(f"\n  {violation_type} (showing first 5):")
    for source_file, line_no in files[:5]:
        print(f"    - {source_file}:{line_no}")

conn.close()
