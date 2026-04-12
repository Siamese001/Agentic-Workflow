#!/usr/bin/env python3
"""Check current HIGH severity violations."""

import sqlite3

conn = sqlite3.connect("artifacts/adg/adg_indexed_03292026_1406.sqlite")
cursor = conn.cursor()

# Check current HIGH severity count
cursor.execute("SELECT COUNT(*) FROM violations WHERE severity = 'HIGH'")
high_count = cursor.fetchone()[0]
print(f"HIGH severity violations: {high_count}")

# Get list
cursor.execute(
    "SELECT file_path, line_no, evidence FROM violations WHERE severity = 'HIGH' ORDER BY file_path, line_no"
)
violations = cursor.fetchall()
print("\nAll HIGH violations:")
for v in violations[:20]:
    print(f"  {v[0]}:{v[1]} - {v[2]}")

if len(violations) > 20:
    print(f"  ... and {len(violations) - 20} more")

conn.close()
