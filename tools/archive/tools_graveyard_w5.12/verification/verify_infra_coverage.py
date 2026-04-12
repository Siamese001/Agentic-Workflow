#!/usr/bin/env python3
"""Verify infrastructure coverage in new ADG."""

import glob
import os
import sqlite3

# Find latest ADG
adg_dir = "artifacts/adg"
sqlite_files = glob.glob(f"{adg_dir}/adg_indexed_*.sqlite")
latest = max(sqlite_files, key=os.path.getmtime)
print(f"Using ADG: {latest}")

conn = sqlite3.connect(latest)
cursor = conn.cursor()

# Count infrastructure modules
cursor.execute("""
    SELECT COUNT(*) FROM nodes
    WHERE entity_type = 'module'
    AND resolved_path LIKE 'infrastructure/%'
""")
module_count = cursor.fetchone()[0]

# Count infrastructure symbols
cursor.execute("""
    SELECT COUNT(*) FROM nodes
    WHERE entity_type = 'symbol'
    AND resolved_path LIKE 'infrastructure/%'
""")
symbol_count = cursor.fetchone()[0]

# Get layer assignment
cursor.execute("""
    SELECT layer, COUNT(*) FROM nodes
    WHERE entity_type = 'module'
    AND resolved_path LIKE 'infrastructure/%'
    GROUP BY layer
""")
layer_info = cursor.fetchall()

# List infrastructure modules
cursor.execute("""
    SELECT resolved_path FROM nodes
    WHERE entity_type = 'module'
    AND resolved_path LIKE 'infrastructure/%'
    ORDER BY resolved_path
""")
modules = cursor.fetchall()

print("\n=== Infrastructure Coverage ===")
print(f"Modules: {module_count}")
print(f"Symbols: {symbol_count}")
print("\nLayer assignment:")
for layer, count in layer_info:
    print(f"  {layer}: {count}")

print("\nModules found:")
for m in modules:
    print(f"  - {m[0]}")

conn.close()
