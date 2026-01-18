"""
Final audit of bulk extraction results.
Excludes archived files to get accurate active codebase metrics.
"""
import json
from pathlib import Path
from collections import defaultdict

# Load current registry
with open(AGENT_DISCOVERY_JSON) as f:
    all_agents = json.load(f)

# Filter to active codebase only (exclude archives)
active_agents = [a for a in all_agents if not a['path'].startswith(ARCHIVES_DIR)]

print("="*80)
print("FINAL BULK EXTRACTION AUDIT")
print("="*80)
print()

print("📊 AGENT COUNTS")
print(f"  Total agents (including archives): {len(all_agents)}")
print(f"  Active agents (excluding archives): {len(active_agents)}")
print()

# Check for multi-class files in active codebase
agents_by_file = defaultdict(list)
for agent in active_agents:
    agents_by_file[agent['path']].append(agent['class_name'])

multi_class_files = {
    path: agents 
    for path, agents in agents_by_file.items() 
    if len(agents) > 1
}

print("📁 MULTI-CLASS FILES (Active Codebase Only)")
print(f"  Count: {len(multi_class_files)}")
print()

if multi_class_files:
    print("  Files still containing multiple agents:")
    for path, agents in sorted(multi_class_files.items()):
        print(f"\n  {path} ({len(agents)} agents):")
        for agent in agents:
            print(f"    - {agent}")
else:
    print("  ✅ No multi-class files remaining!")

print()
print("="*80)
print("LAYER DISTRIBUTION (Active Only)")
print("="*80)

from collections import Counter

from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)
layer_counts = Counter(a.get('layer', 'unknown') for a in active_agents)

for layer in sorted(layer_counts.keys()):
    print(f"  {layer}: {layer_counts[layer]}")

print()
print("="*80)
print("EXTRACTION IMPACT")
print("="*80)

# Load extraction log
with open('surgical_extraction_log.json') as f:
    log = json.load(f)

print(f"  Files processed: {len(set(m['old_module'] for m in log['extractions'].values()))}")
print(f"  Agents extracted: {len(log['extractions'])}")
print(f"  New files created: {len(log['extractions'])}")
print(f"  Imports remapped: {len(log['import_remaps'])} files")

print()
print("="*80)
print("STATUS")
print("="*80)

expected_baseline = 285
actual_count = len(active_agents)
delta = actual_count - expected_baseline

if delta == 0:
    print(f"  ✅ Agent count matches baseline: {actual_count}")
elif delta < 0:
    print(f"  ⚠️  Agent count below baseline: {actual_count} (expected {expected_baseline})")
    print(f"     Delta: {delta} agents lost")
else:
    print(f"  ⚠️  Agent count above baseline: {actual_count} (expected {expected_baseline})")
    print(f"     Delta: +{delta} agents")

if len(multi_class_files) == 0:
    print(f"  ✅ All agents in 1:1 file structure")
else:
    print(f"  ⚠️  {len(multi_class_files)} multi-class files remain")

print()

# Final verdict
if delta == 0 and len(multi_class_files) == 0:
    print("🎉 EXTRACTION COMPLETE - ALL OBJECTIVES MET")
elif abs(delta) <= 2 and len(multi_class_files) <= 1:
    print("✅ EXTRACTION MOSTLY SUCCESSFUL - Minor cleanup needed")
else:
    print("⚠️  EXTRACTION INCOMPLETE - Further investigation required")
