#!/usr/bin/env python3
"""Investigate the newly regenerated ADG."""

import sqlite3
from pathlib import Path

SQLITE_PATH = Path("C:/Git/Agentic-Workflow/artifacts/adg/adg_indexed_03232026_0655.sqlite")

conn = sqlite3.connect(SQLITE_PATH)
cursor = conn.cursor()

print("=== INVESTIGATING NEW ADG ===")

# Check null/empty layers
cursor.execute("SELECT COUNT(*) FROM nodes WHERE layer = '' OR layer IS NULL")
null_layers = cursor.fetchone()[0]
print(f"Null/empty layers: {null_layers}")

# Check layer distribution
cursor.execute("SELECT layer, COUNT(*) FROM nodes GROUP BY layer ORDER BY COUNT(*) DESC LIMIT 20")
layer_dist = cursor.fetchall()
print(f"Layer distribution: {layer_dist}")

# Check critical layers
critical_layers = ["L0_FOUNDATION", "L2_COORDINATION", "L5_EXECUTION"]
for layer in critical_layers:
    cursor.execute("SELECT COUNT(*) FROM nodes WHERE layer = ?", (layer,))
    count = cursor.fetchone()[0]
    print(f"{layer}: {count}")

# Check if our gap closure was applied
cursor.execute("SELECT COUNT(*) FROM nodes WHERE layer = 'L_UNKNOWN'")
unknown_count = cursor.fetchone()[0]
print(f"L_UNKNOWN nodes: {unknown_count}")

conn.close()
