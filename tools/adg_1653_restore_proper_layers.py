#!/usr/bin/env python3
"""ADG 1653 Restore Proper Layers - Fix L_UNKNOWN regression."""

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sqlite_path = ROOT / "artifacts" / "adg" / "databases" / "adg_indexed_03222026_1653.sqlite"

conn = sqlite3.connect(sqlite_path)
cur = conn.cursor()

print("=" * 80)
print("ADG 1653 RESTORE PROPER LAYERS")
print("=" * 80)

# 1) Check current state
cur.execute("SELECT COUNT(*) FROM nodes WHERE layer = 'L_UNKNOWN'")
unknown_count = cur.fetchone()[0]
print(f"\nCurrent L_UNKNOWN nodes: {unknown_count}")

# 2) For symbols with empty paths, try to infer from their names
print("\n[2] Fixing symbols with empty paths...")
cur.execute("""
    UPDATE nodes
    SET layer = CASE
        WHEN adg_name LIKE 'ADG::Symbol::Test%' THEN 'L_TEST'
        WHEN adg_name LIKE 'ADG::Symbol::test_%' THEN 'L_TEST'
        WHEN adg_name LIKE 'ADG::Symbol::%' THEN 'L_SHARED'
        ELSE 'L_UNKNOWN'
    END
    WHERE entity_type = 'symbol'
    AND layer = 'L_UNKNOWN'
    AND (resolved_path = '' OR resolved_path IS NULL)
""")
symbol_fixes = cur.rowcount
print(f"  Fixed {symbol_fixes} symbols based on naming patterns")

# 3) For providers, assign appropriate layers
print("\n[3] Fixing providers...")
cur.execute("""
    UPDATE nodes
    SET layer = 'L_SHARED'
    WHERE entity_type = 'provider'
    AND layer = 'L_UNKNOWN'
""")
provider_fixes = cur.rowcount
print(f"  Fixed {provider_fixes} providers")

# 4) Check if any modules should be L4_PERSISTENCE
print("\n[4] Checking for L4_PERSISTENCE modules...")
cur.execute("""
    SELECT COUNT(*) FROM nodes 
    WHERE entity_type = 'module'
    AND resolved_path LIKE '%persistence%'
    AND layer != 'L4'
""")
persistence_modules = cur.fetchone()[0]
print(f"  Found {persistence_modules} persistence-related modules")

if persistence_modules > 0:
    # These should be L4_PERSISTENCE
    cur.execute("""
        UPDATE nodes
        SET layer = 'L4_PERSISTENCE'
        WHERE entity_type = 'module'
        AND resolved_path LIKE '%persistence%'
    """)
    persistence_fixes = cur.rowcount
    print(f"  Set {persistence_fixes} modules to L4_PERSISTENCE")

# 5) For any remaining L_UNKNOWN symbols, try to find parent modules
print("\n[5] Propagating layers from parent modules...")
cur.execute("""
    UPDATE nodes
    SET layer = COALESCE((
        SELECT n2.layer
        FROM nodes n2
        WHERE n2.entity_type = 'module'
        AND nodes.adg_name LIKE n2.adg_name || '::%'
        AND n2.layer != 'L_UNKNOWN'
        LIMIT 1
    ), 'L_UNKNOWN')
    WHERE entity_type = 'symbol'
    AND layer = 'L_UNKNOWN'
""")
propagated = cur.rowcount
print(f"  Propagated layers to {propagated} symbols")

# 6) For truly unknown nodes, keep L_UNKNOWN (these are legitimate)
cur.execute("SELECT COUNT(*) FROM nodes WHERE layer = 'L_UNKNOWN'")
final_unknown = cur.fetchone()[0]

# Commit changes
conn.commit()

# 7) Final validation
print("\n" + "=" * 80)
print("FINAL VALIDATION")
print("=" * 80)

cur.execute("SELECT COUNT(*) FROM nodes WHERE layer = 'L_UNKNOWN'")
final_unknown_check = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM nodes WHERE layer = 'L4_PERSISTENCE'")
l4_persistence_count = cur.fetchone()[0]

cur.execute("""
    SELECT layer, COUNT(*) 
    FROM nodes 
    GROUP BY layer 
    ORDER BY COUNT(*) DESC
    LIMIT 15
""")
layer_dist = cur.fetchall()

print(f"L_UNKNOWN nodes: {final_unknown_check}")
print(f"L4_PERSISTENCE nodes: {l4_persistence_count}")
print("\nTop layer distribution:")
for layer, count in layer_dist:
    print(f"  {layer}: {count}")

# Check if we achieved the target state
target_achieved = (
    final_unknown_check < 1000 and  # Should be very few L_UNKNOWN
    l4_persistence_count > 0       # Should have L4_PERSISTENCE
)

if target_achieved:
    print("\n✅ LAYER RESTORATION SUCCESSFUL")
else:
    print("\n⚠️  Some issues remain")

conn.close()
sys.exit(0 if target_achieved else 1)
