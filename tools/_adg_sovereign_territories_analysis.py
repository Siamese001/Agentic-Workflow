"""ADG-based analysis of SOVEREIGN_TERRITORIES usage patterns.

Queries the ADG SQLite to determine:
1. Which files define SOVEREIGN_TERRITORIES
2. Which files import it (fan-out)
3. Import depth (direct vs transitive consumers)
4. Layer distribution of consumers
5. Proposed migration strategy based on dependency patterns
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADG_DIR = ROOT / "artifacts" / "adg"

# Find latest ADG
dbs = sorted(ADG_DIR.glob("adg_indexed_*.sqlite"))
if not dbs:
    print("ERROR: No ADG SQLite found")
    exit(1)

db_path = dbs[-1]
print(f"Using: {db_path.name}\n")

conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row

# Build path -> node lookup
path_to_node = {}
for row in conn.execute("SELECT id, resolved_path FROM nodes WHERE resolved_path IS NOT NULL"):
    path_to_node[row["resolved_path"]] = {"id": row["id"], "resolved_path": row["resolved_path"]}

print("=" * 80)
print("SOVEREIGN_TERRITORIES ADG Analysis")
print("=" * 80)
print()

# 1. Find definition file
print("## 1. DEFINITION FILE")
definition_file = "agentic_core/L5_safety/config/structure_blueprint/_constants.py"
if definition_file in path_to_node:
    def_node = path_to_node[definition_file]
    print(f"  {definition_file} (node_id={def_node['id']})")

    # Get fan-out (how many files import from this file)
    importers = conn.execute(
        "SELECT n.resolved_path, n.entity_type FROM edges e "
        "JOIN nodes n ON e.src_id=n.id "
        "WHERE e.dst_id=? AND e.relation_type='imports'",
        (def_node["id"],),
    ).fetchall()

    print(f"  Direct importers: {len(importers)}")
else:
    print(f"  NOT FOUND in ADG: {definition_file}")
    importers = []

print()

# 2. Find all files that import SOVEREIGN_TERRITORIES symbol
print("## 2. DIRECT CONSUMERS (import SOVEREIGN_TERRITORIES)")
direct_consumers = []

# Search for edges with SOVEREIGN_TERRITORIES in the symbol
sovereign_edges = conn.execute(
    "SELECT e.src_id, e.dst_id, e.symbol, n_src.resolved_path as src_path, n_dst.resolved_path as dst_path "
    "FROM edges e "
    "JOIN nodes n_src ON e.src_id=n_src.id "
    "JOIN nodes n_dst ON e.dst_id=n_dst.id "
    "WHERE e.symbol LIKE '%SOVEREIGN_TERRITORIES%' AND e.relation_type='imports'"
).fetchall()

print(f"  Found {len(sovereign_edges)} import edges with SOVEREIGN_TERRITORIES in symbol")
print()

# Group by source file
from collections import defaultdict

consumers_by_file = defaultdict(list)
for edge in sovereign_edges:
    consumers_by_file[edge["src_path"]].append(
        {
            "dst_path": edge["dst_path"],
            "symbol": edge["symbol"],
        }
    )

# Sort by number of imports
sorted_consumers = sorted(consumers_by_file.items(), key=lambda x: len(x[1]), reverse=True)

print(f"  {len(sorted_consumers)} unique files import SOVEREIGN_TERRITORIES")
print()

# Show top 20 consumers
print("### Top 20 Direct Consumers:")
for i, (src_path, imports) in enumerate(sorted_consumers[:20], 1):
    print(f"  {i:2}. {src_path} ({len(imports)} imports)")
    for imp in imports[:2]:  # Show first 2 imports
        symbol_short = imp["symbol"][:60] + "..." if len(imp["symbol"]) > 60 else imp["symbol"]
        print(f"      <- {imp['dst_path']} [{symbol_short}]")
    if len(imports) > 2:
        print(f"      ... +{len(imports) - 2} more")

print()

# 3. Layer distribution
print("## 3. LAYER DISTRIBUTION OF CONSUMERS")
layer_counts = defaultdict(int)
for src_path, _ in sorted_consumers:
    if "agentic_core/L0_" in src_path:
        layer_counts["L0_routing"] += 1
    elif "agentic_core/L1_" in src_path:
        layer_counts["L1_cognition"] += 1
    elif "agentic_core/L2_" in src_path:
        layer_counts["L2_execution"] += 1
    elif "agentic_core/L3_" in src_path:
        layer_counts["L3_orchestration"] += 1
    elif "agentic_core/L4_" in src_path:
        layer_counts["L4_state"] += 1
    elif "agentic_core/L5_" in src_path:
        layer_counts["L5_safety"] += 1
    elif "agentic_core/L6_" in src_path:
        layer_counts["L6_observability"] += 1
    elif "tests/" in src_path:
        layer_counts["tests"] += 1
    elif "ops_scripts/" in src_path:
        layer_counts["ops_scripts"] += 1
    elif "apps_" in src_path:
        layer_counts["apps_*"] += 1
    else:
        layer_counts["other"] += 1

for layer, count in sorted(layer_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {layer:20} {count:3} files")

print()

# 4. Check if PROJECT_ROOT_WHITELIST exists
print("## 4. REPLACEMENT API CHECK")
replacement_file = "agentic_core/L5_safety/config/structure_blueprint/ssot.py"
if replacement_file in path_to_node:
    repl_node = path_to_node[replacement_file]
    print(f"  ✅ {replacement_file} exists (node_id={repl_node['id']})")

    # Check for PROJECT_ROOT_WHITELIST importers
    prw_edges = conn.execute(
        "SELECT n.resolved_path FROM edges e "
        "JOIN nodes n ON e.src_id=n.id "
        "WHERE e.dst_id=? AND e.symbol LIKE '%PROJECT_ROOT_WHITELIST%'",
        (repl_node["id"],),
    ).fetchall()

    print(f"  PROJECT_ROOT_WHITELIST importers: {len(prw_edges)}")
    if len(prw_edges) > 0:
        print("  Sample importers:")
        for edge in prw_edges[:5]:
            print(f"    - {edge['resolved_path']}")
else:
    print(f"  ❌ {replacement_file} NOT FOUND in ADG")

print()

# 5. Migration complexity analysis
print("## 5. MIGRATION COMPLEXITY ANALYSIS")

# Count files by category
core_files = [p for p, _ in sorted_consumers if "agentic_core/" in p and "tests/" not in p]
test_files = [p for p, _ in sorted_consumers if "tests/" in p]
script_files = [p for p, _ in sorted_consumers if "ops_scripts/" in p or "tools/" in p]
app_files = [p for p, _ in sorted_consumers if "apps_" in p]

print(f"  Core infrastructure files:  {len(core_files):3}")
print(f"  Test files:                 {len(test_files):3}")
print(f"  Script/tool files:          {len(script_files):3}")
print(f"  App files:                  {len(app_files):3}")
print(f"  Total:                      {len(sorted_consumers):3}")

print()

# 6. Proposed migration strategy
print("=" * 80)
print("PROPOSED MIGRATION STRATEGY (ADG-backed)")
print("=" * 80)
print()

print("### Phase 1: Analyze Replacement API")
print("  1. Verify PROJECT_ROOT_WHITELIST provides equivalent functionality")
print("  2. Document migration patterns for common use cases:")
print("     - Territory lookup: SOVEREIGN_TERRITORIES.get(key)")
print("     - Root validation: key in SOVEREIGN_TERRITORIES")
print("     - Subfolder access: SOVEREIGN_TERRITORIES[key]['subfolders']")
print()

print("### Phase 2: Create Compatibility Layer (if needed)")
print("  If PROJECT_ROOT_WHITELIST is insufficient:")
print("  - Add new API in structure_blueprint for territory metadata")
print("  - Maintain SOVEREIGN_TERRITORIES temporarily with deprecation warning")
print()

print("### Phase 3: Migrate Core Files (Priority Order)")
print(f"  Total: {len(core_files)} core files")
if core_files:
    print("  Top 5 by import count:")
    core_with_counts = [(p, len(consumers_by_file[p])) for p in core_files]
    core_with_counts.sort(key=lambda x: x[1], reverse=True)
    for i, (path, count) in enumerate(core_with_counts[:5], 1):
        print(f"    {i}. {path} ({count} imports)")
print()

print("### Phase 4: Migrate Tests")
print(f"  Total: {len(test_files)} test files")
print("  - Update test assertions to use new API")
print("  - Some tests may need complete rewrite if testing SOVEREIGN_TERRITORIES internals")
print()

print("### Phase 5: Migrate Scripts & Apps")
print(f"  Scripts: {len(script_files)} files")
print(f"  Apps:    {len(app_files)} files")
print()

print("### Phase 6: Remove SOVEREIGN_TERRITORIES")
print("  - Remove from _constants.py")
print("  - Remove from __init__.py exports")
print("  - Verify zero references remain")
print()

print("### Estimated Effort")
print(f"  Core files ({len(core_files)}):     2-3 days (complex refactoring)")
print(f"  Tests ({len(test_files)}):          1-2 days (pattern replacement)")
print(f"  Scripts/apps ({len(script_files) + len(app_files)}): 0.5-1 day")
print("  Total:                  3.5-6 days")
print()

print("### Risk Assessment")
if len(core_files) > 10:
    print("  ⚠️  HIGH RISK: 10+ core infrastructure files depend on SOVEREIGN_TERRITORIES")
    print("     Breaking change requires careful staged migration")
else:
    print("  ✅ MEDIUM RISK: Manageable number of core dependencies")

print()

conn.close()
