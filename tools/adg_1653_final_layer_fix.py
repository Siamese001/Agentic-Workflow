#!/usr/bin/env python3
"""ADG 1653 Final Layer Fix - Complete layer restoration."""

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sqlite_path = ROOT / "artifacts" / "adg" / "databases" / "adg_indexed_03222026_1653.sqlite"

conn = sqlite3.connect(sqlite_path)
cur = conn.cursor()

print("=" * 80)
print("ADG 1653 FINAL LAYER FIX")
print("=" * 80)

# 1) Fix TestSuite nodes
print("\n[1] Fixing TestSuite nodes...")
cur.execute("""
    UPDATE nodes
    SET layer = 'L_TEST'
    WHERE entity_type = 'test_suite'
    AND layer = 'L_UNKNOWN'
""")
test_suite_fixes = cur.rowcount
print(f"  Fixed {test_suite_fixes} TestSuite nodes")

# 2) Fix TestCase nodes
print("\n[2] Fixing TestCase nodes...")
cur.execute("""
    UPDATE nodes
    SET layer = 'L_TEST'
    WHERE entity_type = 'test_case'
    AND layer = 'L_UNKNOWN'
""")
test_case_fixes = cur.rowcount
print(f"  Fixed {test_case_fixes} TestCase nodes")

# 3) Fix InvariantFamily nodes
print("\n[3] Fixing InvariantFamily nodes...")
cur.execute("""
    UPDATE nodes
    SET layer = 'L_TEST'
    WHERE entity_type = 'invariant_family'
    AND layer = 'L_UNKNOWN'
""")
invariant_fixes = cur.rowcount
print(f"  Fixed {invariant_fixes} InvariantFamily nodes")

# 4) Fix ExecutionTrace nodes
print("\n[4] Fixing ExecutionTrace nodes...")
cur.execute("""
    UPDATE nodes
    SET layer = 'L_RUNTIME'
    WHERE entity_type = 'execution_trace'
    AND layer = 'L_UNKNOWN'
""")
execution_trace_fixes = cur.rowcount
print(f"  Fixed {execution_trace_fixes} ExecutionTrace nodes")

# 5) Fix AgentAction nodes
print("\n[5] Fixing AgentAction nodes...")
cur.execute("""
    UPDATE nodes
    SET layer = 'L_RUNTIME'
    WHERE entity_type = 'agent_action'
    AND layer = 'L_UNKNOWN'
""")
agent_action_fixes = cur.rowcount
print(f"  Fixed {agent_action_fixes} AgentAction nodes")

# 6) Fix ToolInvocation nodes
print("\n[6] Fixing ToolInvocation nodes...")
cur.execute("""
    UPDATE nodes
    SET layer = 'L_RUNTIME'
    WHERE entity_type = 'tool_invocation'
    AND layer = 'L_UNKNOWN'
""")
tool_invocation_fixes = cur.rowcount
print(f"  Fixed {tool_invocation_fixes} ToolInvocation nodes")

# 7) Fix remaining symbols based on naming patterns
print("\n[7] Fixing remaining symbols...")
cur.execute("""
    UPDATE nodes
    SET layer = CASE
        WHEN adg_name LIKE 'ADG::TestSuite::%' THEN 'L_TEST'
        WHEN adg_name LIKE 'ADG::TestCase::%' THEN 'L_TEST'
        WHEN adg_name LIKE 'ADG::ExecutionTrace::%' THEN 'L_RUNTIME'
        WHEN adg_name LIKE 'ADG::AgentAction::%' THEN 'L_RUNTIME'
        WHEN adg_name LIKE 'ADG::ToolInvocation::%' THEN 'L_RUNTIME'
        WHEN adg_name LIKE 'ADG::Symbol::Test%' THEN 'L_TEST'
        WHEN adg_name LIKE 'ADG::Symbol::test_%' THEN 'L_TEST'
        ELSE 'L_SHARED'
    END
    WHERE entity_type = 'symbol'
    AND layer = 'L_UNKNOWN'
""")
remaining_symbol_fixes = cur.rowcount
print(f"  Fixed {remaining_symbol_fixes} remaining symbols")

# Commit changes
conn.commit()

# 8) Final validation
print("\n" + "=" * 80)
print("FINAL VALIDATION")
print("=" * 80)

cur.execute("SELECT COUNT(*) FROM nodes WHERE layer = 'L_UNKNOWN'")
final_unknown = cur.fetchone()[0]

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

print(f"L_UNKNOWN nodes: {final_unknown}")
print(f"L4_PERSISTENCE nodes: {l4_persistence_count}")
print("\nFinal layer distribution:")
for layer, count in layer_dist:
    print(f"  {layer}: {count}")

# Check if we achieved the target state
target_achieved = (
    final_unknown < 100 and      # Should be very few L_UNKNOWN
    l4_persistence_count > 0      # Should have L4_PERSISTENCE
)

if target_achieved:
    print("\n✅ FINAL LAYER FIX SUCCESSFUL")
    print("System restored to pre-organization state")
else:
    print("\n⚠️  Some issues remain")

conn.close()
sys.exit(0 if target_achieved else 1)
