#!/usr/bin/env python3
"""ADG 1653 Fix Empty Fields - Handle empty strings properly."""

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sqlite_path = ROOT / "artifacts" / "adg" / "databases" / "adg_indexed_03222026_1653.sqlite"

conn = sqlite3.connect(sqlite_path)
cur = conn.cursor()

print("=" * 80)
print("ADG 1653 FIX EMPTY FIELDS")
print("=" * 80)

# Check foreign key constraints
cur.execute("PRAGMA foreign_keys")
print(f"Foreign keys enabled: {cur.fetchone()[0]}")

# 1) Fix empty layers
print("\n[1] Fixing empty layers...")
cur.execute("SELECT COUNT(*) FROM nodes WHERE layer = ''")
empty_layers = cur.fetchone()[0]
print(f"  Found {empty_layers} nodes with empty layers")

if empty_layers > 0:
    # Disable foreign keys temporarily
    cur.execute("PRAGMA foreign_keys = OFF")
    
    # Update all empty layers at once
    cur.execute("""
        UPDATE nodes 
        SET layer = 'L_UNKNOWN'
        WHERE layer = ''
    """)
    
    updated = cur.rowcount
    print(f"  Fixed {updated} empty layers")
    
    # Re-enable foreign keys
    cur.execute("PRAGMA foreign_keys = ON")

# 2) Fix empty identity_kinds
print("\n[2] Fixing empty identity_kinds...")
cur.execute("SELECT COUNT(*) FROM nodes WHERE identity_kind = ''")
empty_identities = cur.fetchone()[0]
print(f"  Found {empty_identities} nodes with empty identity_kind")

if empty_identities > 0:
    # Disable foreign keys temporarily
    cur.execute("PRAGMA foreign_keys = OFF")
    
    # Update all empty identity_kinds at once
    cur.execute("""
        UPDATE nodes 
        SET identity_kind = 'inferred_symbol'
        WHERE identity_kind = ''
    """)
    
    updated = cur.rowcount
    print(f"  Fixed {updated} empty identity_kinds")
    
    # Now apply proper mapping
    cur.execute("""
        UPDATE nodes 
        SET identity_kind = CASE entity_type
            WHEN 'symbol' THEN 'inferred_symbol'
            WHEN 'module' THEN 'repo_module'
            WHEN 'test_suite' THEN 'repo_module'
            WHEN 'test_case' THEN 'repo_module'
            WHEN 'invariant_family' THEN 'repo_module'
            WHEN 'replay_key' THEN 'synthetic'
            WHEN 'policy_hash' THEN 'synthetic'
            WHEN 'determinism_digest' THEN 'synthetic'
            ELSE 'inferred_symbol'
        END
        WHERE identity_kind = 'inferred_symbol'
        AND entity_type IN ('symbol', 'module', 'test_suite', 'test_case', 'invariant_family', 'replay_key', 'policy_hash', 'determinism_digest')
    """)
    
    # Re-enable foreign keys
    cur.execute("PRAGMA foreign_keys = ON")
    
    print(f"  Fixed {updated} empty identity_kinds")

# 3) Now apply proper layer propagation
print("\n[3] Applying proper layer propagation...")
cur.execute("SELECT COUNT(*) FROM nodes WHERE layer = 'L_UNKNOWN'")
unknown_layers = cur.fetchone()[0]
print(f"  Found {unknown_layers} nodes with L_UNKNOWN")

if unknown_layers > 0:
    # Update modules based on path
    cur.execute("""
        UPDATE nodes 
        SET layer = CASE 
            WHEN resolved_path LIKE 'agentic_core/L0_%' THEN 'L0'
            WHEN resolved_path LIKE 'agentic_core/L1_%' THEN 'L1'
            WHEN resolved_path LIKE 'agentic_core/L2_%' THEN 'L2'
            WHEN resolved_path LIKE 'agentic_core/L3_%' THEN 'L3'
            WHEN resolved_path LIKE 'agentic_core/L4_%' THEN 'L4'
            WHEN resolved_path LIKE 'agentic_core/L5_%' THEN 'L5'
            WHEN resolved_path LIKE 'agentic_core/L6_%' THEN 'L6'
            ELSE 'L_UNKNOWN'
        END
        WHERE entity_type = 'module' 
        AND layer = 'L_UNKNOWN'
        AND resolved_path LIKE 'agentic_core/%'
    """)
    module_updates = cur.rowcount
    print(f"  Updated {module_updates} module layers")
    
    # Propagate to symbols
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
    symbol_updates = cur.rowcount
    print(f"  Updated {symbol_updates} symbol layers")

# Commit all changes
conn.commit()

# Final validation
print("\n" + "=" * 80)
print("FINAL VALIDATION")
print("=" * 80)

cur.execute("SELECT COUNT(*) FROM nodes WHERE layer = '' OR layer IS NULL")
blank_layers = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM nodes WHERE identity_kind = '' OR identity_kind IS NULL")
blank_identities = cur.fetchone()[0]

cur.execute("SELECT layer, COUNT(*) FROM nodes GROUP BY layer ORDER BY COUNT(*) DESC LIMIT 10")
layer_dist = cur.fetchall()

cur.execute("SELECT identity_kind, COUNT(*) FROM nodes GROUP BY identity_kind ORDER BY COUNT(*) DESC LIMIT 10")
identity_dist = cur.fetchall()

print(f"Blank layers: {blank_layers}")
print(f"Blank identity_kinds: {blank_identities}")
print("\nTop layer distribution:")
for layer, count in layer_dist:
    print(f"  {layer}: {count}")

print("\nTop identity_kind distribution:")
for identity, count in identity_dist:
    print(f"  {identity}: {count}")

success = (blank_layers == 0 and blank_identities == 0)

if success:
    print("\n✅ ALL EMPTY FIELDS FIXED SUCCESSFULLY")
else:
    print("\n❌ SOME ISSUES REMAIN")

conn.close()
sys.exit(0 if success else 1)
