#!/usr/bin/env python3
"""ADG 1653 Data Integrity Fix - Correct blank layers and identity_kinds."""

import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
sqlite_path = ROOT / "artifacts" / "adg" / "databases" / "adg_indexed_03222026_1653.sqlite"

if not sqlite_path.exists():
    print(f"ERROR: SQLite database not found at {sqlite_path}")
    sys.exit(1)

conn = sqlite3.connect(sqlite_path)
cur = conn.cursor()

print("=" * 80)
print("ADG 1653 DATA INTEGRITY FIX")
print("=" * 80)

# 1) DATA INTEGRITY — LAYER FIELD CORRECTION
print("\n[1] Fixing blank layers...")
cur.execute("SELECT COUNT(*) FROM nodes WHERE layer = '' OR layer IS NULL")
blank_layers = cur.fetchone()[0]
print(f"  Found {blank_layers} nodes with blank layers")

if blank_layers > 0:
    # First, fix module nodes with blank layers using deterministic path rules
    cur.execute("""
        UPDATE nodes
        SET layer = 'L_UNKNOWN'
        WHERE entity_type = 'module'
        AND (layer = '' OR layer IS NULL)
    """)
    module_fixes = cur.rowcount
    print(f"  Initialized {module_fixes} module layers to L_UNKNOWN")

    # Now update modules with proper layer based on path
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
    print(f"  Updated {module_updates} module layers based on path")

    # Then, propagate module layers to symbols
    cur.execute("""
        UPDATE nodes
        SET layer = (
            SELECT n2.layer
            FROM nodes n2
            WHERE n2.entity_type = 'module'
            AND nodes.adg_name LIKE n2.adg_name || '::%'
            AND n2.layer != 'L_UNKNOWN'
            LIMIT 1
        )
        WHERE entity_type = 'symbol'
        AND (layer = '' OR layer IS NULL)
    """)
    symbol_fixes = cur.rowcount
    print(f"  Fixed {symbol_fixes} symbol layers")

    # For any remaining blank nodes, assign L_UNKNOWN
    cur.execute("""
        UPDATE nodes
        SET layer = 'L_UNKNOWN'
        WHERE layer = '' OR layer IS NULL
    """)
    remaining_fixes = cur.rowcount
    print(f"  Set {remaining_fixes} remaining nodes to L_UNKNOWN")

# Validate
cur.execute("SELECT COUNT(*) FROM nodes WHERE layer = '' OR layer IS NULL")
remaining_blank = cur.fetchone()[0]
if remaining_blank == 0:
    print("  ✅ All blank layers fixed")
else:
    print(f"  ❌ Still {remaining_blank} blank layers")

# 2) DATA INTEGRITY — IDENTITY_KIND COMPLETION
print("\n[2] Fixing blank identity_kinds...")
cur.execute("SELECT COUNT(*) FROM nodes WHERE identity_kind = '' OR identity_kind IS NULL")
blank_identities = cur.fetchone()[0]
print(f"  Found {blank_identities} nodes with blank identity_kind")

if blank_identities > 0:
    # First set all blank to a default value
    cur.execute("""
        UPDATE nodes
        SET identity_kind = 'inferred_symbol'
        WHERE identity_kind = '' OR identity_kind IS NULL
    """)
    initial_fixes = cur.rowcount
    print(f"  Initialized {initial_fixes} identity_kind to inferred_symbol")

    # Now apply deterministic mapping based on entity_type
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
    """)
    identity_fixes = cur.rowcount
    print(f"  Fixed {identity_fixes} identity_kind values")

# Validate
cur.execute("SELECT COUNT(*) FROM nodes WHERE identity_kind = '' OR identity_kind IS NULL")
remaining_blank_id = cur.fetchone()[0]
if remaining_blank_id == 0:
    print("  ✅ All blank identity_kinds fixed")
else:
    print(f"  ❌ Still {remaining_blank_id} blank identity_kinds")

# 3) Report ↔ SQLite parity check
print("\n[3] Checking report parity...")
cur.execute("SELECT COUNT(*) FROM nodes")
total_nodes = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM edges")
total_edges = cur.fetchone()[0]

cur.execute("SELECT relation_type, COUNT(*) FROM edges GROUP BY relation_type")
edge_distribution = dict(cur.fetchall())

print(f"  SQLite: {total_nodes} nodes, {total_edges} edges")
print(f"  Edge types: {len(edge_distribution)}")

# 4) Replay convergence check
print("\n[4] Checking replay convergence...")
replay_edges = ['emits_replay_key', 'references_policy_hash', 'mutation_signature', 'parent_snapshot_hash']
replay_counts = {}

for edge_type in replay_edges:
    cur.execute("SELECT COUNT(*) FROM edges WHERE relation_type = ?", (edge_type,))
    count = cur.fetchone()[0]
    replay_counts[edge_type] = count

print(f"  Replay edge counts: {replay_counts}")

# 5) Core edge coverage validation
print("\n[5] Validating core edge coverage...")
core_modules_query = """
    SELECT adg_name, id FROM nodes
    WHERE entity_type = 'module'
    AND layer IN ('L0', 'L2', 'L5')
"""
cur.execute(core_modules_query)
core_modules = cur.fetchall()

missing_coverage = []
for module_adg, module_id in core_modules:
    # Check determinism
    cur.execute("""
        SELECT COUNT(*) FROM edges
        WHERE src_id = ? AND relation_type IN ('determinism_seed', 'emits_determinism_digest')
    """, (module_id,))
    if cur.fetchone()[0] == 0:
        missing_coverage.append(f"{module_adg}: missing determinism")

    # Check governance
    cur.execute("""
        SELECT COUNT(*) FROM edges
        WHERE src_id = ? AND relation_type = 'policy_verification'
    """, (module_id,))
    if cur.fetchone()[0] == 0:
        missing_coverage.append(f"{module_adg}: missing governance")

    # Check execution
    cur.execute("""
        SELECT COUNT(*) FROM edges
        WHERE src_id = ? AND relation_type = 'dispatches_execution_plan'
    """, (module_id,))
    if cur.fetchone()[0] == 0:
        missing_coverage.append(f"{module_adg}: missing execution")

if not missing_coverage:
    print("  ✅ All core modules have required edge coverage")
else:
    print(f"  ❌ {len(missing_coverage)} coverage issues found")
    for issue in missing_coverage[:5]:  # Show first 5
        print(f"    {issue}")

# 6) Test surface validation
print("\n[6] Validating test surface...")
test_nodes = ['test_suite', 'test_case', 'invariant_family']
test_node_counts = {}

for node_type in test_nodes:
    cur.execute("SELECT COUNT(*) FROM nodes WHERE entity_type = ?", (node_type,))
    count = cur.fetchone()[0]
    test_node_counts[node_type] = count

print(f"  Test node counts: {test_node_counts}")

# Check test linkage
cur.execute("""
    SELECT COUNT(DISTINCT e.src_id)
    FROM edges e
    JOIN nodes n ON e.src_id = n.id
    WHERE n.entity_type = 'module'
    AND n.layer IN ('L0', 'L2', 'L5')
    AND e.relation_type IN ('defines_test_case', 'defines_test_suite')
""")
modules_with_tests = cur.fetchone()[0]

cur.execute("""
    SELECT COUNT(*) FROM nodes
    WHERE entity_type = 'module'
    AND layer IN ('L0', 'L2', 'L5')
""")
total_critical_modules = cur.fetchone()[0]

test_coverage = modules_with_tests / total_critical_modules if total_critical_modules > 0 else 0
print(f"  Test linkage: {modules_with_tests}/{total_critical_modules} ({test_coverage:.1%})")

if test_coverage >= 0.9:
    print("  ✅ Test surface coverage adequate")
else:
    print("  ❌ Test surface coverage inadequate")

# Commit changes
conn.commit()

# Final validation
print("\n" + "=" * 80)
print("1653 DATA INTEGRITY FIX RESULTS")
print("=" * 80)

# Final counts
cur.execute("SELECT COUNT(*) FROM nodes WHERE layer = '' OR layer IS NULL")
final_blank_layers = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM nodes WHERE identity_kind = '' OR identity_kind IS NULL")
final_blank_identities = cur.fetchone()[0]

success = (final_blank_layers == 0 and
          final_blank_identities == 0 and
          len(missing_coverage) == 0 and
          test_coverage >= 0.9)

print(f"Blank layers: {final_blank_layers}")
print(f"Blank identity_kinds: {final_blank_identities}")
print(f"Missing coverage: {len(missing_coverage)}")
print(f"Test coverage: {test_coverage:.1%}")

if success:
    print("\n🎉 DATA INTEGRITY FIX COMPLETED SUCCESSFULLY")
    print("System is data-correct with no blank fields")
else:
    print("\n⚠️  DATA INTEGRITY FIX INCOMPLETE")
    print("Some issues remain - review detailed output")

conn.close()
sys.exit(0 if success else 1)
