#!/usr/bin/env python3
"""Analyze L_UNKNOWN nodes to find missing layer mappings."""
import sqlite3
from collections import Counter
from pathlib import Path

sqlite_path = Path("artifacts/adg/adg_indexed_03222026_1546.sqlite")
if not sqlite_path.exists():
    print("SQLite file not found")
    exit(1)

conn = sqlite3.connect(sqlite_path)
cur = conn.cursor()

# Get all L_UNKNOWN nodes with their paths
cur.execute("""
    SELECT adg_name, entity_type, resolved_path
    FROM nodes
    WHERE layer = 'L_UNKNOWN'
    ORDER BY resolved_path
""")
unknown_nodes = cur.fetchall()

print(f"Total L_UNKNOWN nodes: {len(unknown_nodes)}")
print()

# Group by path prefix
path_counts = Counter()
for name, entity_type, path in unknown_nodes:
    if path:
        # Get first two path segments
        parts = path.replace("\\", "/").split("/")
        if len(parts) >= 2:
            prefix = "/".join(parts[:2])
            path_counts[prefix] += 1
        elif parts:
            path_counts[parts[0]] += 1

print("Top path prefixes in L_UNKNOWN:")
for prefix, count in path_counts.most_common(20):
    print(f"  {prefix}/*: {count}")

print()

# Check for external symbols (empty path)
external_symbols = [n for n in unknown_nodes if not n[2]]
print(f"External symbols (empty path): {len(external_symbols)}")
if external_symbols:
    print("Sample external symbols:")
    for name, entity_type, path in external_symbols[:10]:
        print(f"  {name}")

print()

# Check for actual file paths that should be mapped
file_paths = [n for n in unknown_nodes if n[2] and n[2].endswith('.py')]
print(f"Python file paths in L_UNKNOWN: {len(file_paths)}")
if file_paths:
    print("Sample Python file paths:")
    for name, entity_type, path in file_paths[:10]:
        print(f"  {path}")

conn.close()
