#!/usr/bin/env python3
"""
Analyze agents for MCP hardening and test coverage gaps.
"""
import json
from pathlib import Path
from collections import defaultdict

project_root = Path(__file__).parent.parent
discovery_file = project_root / "agent_discovery_full.json"

with open(discovery_file, 'r', encoding='utf-8') as f:
    agents = json.load(f)

# Analyze gaps
unhardened = [a for a in agents if not a.get('mcp_hardened')]
untested = [a for a in agents if not a.get('has_tests')]

print(f"Total agents: {len(agents)}")
print(f"Unhardened agents: {len(unhardened)} ({len(unhardened)/len(agents)*100:.1f}%)")
print(f"Untested agents: {len(untested)} ({len(untested)/len(agents)*100:.1f}%)")

# Group by layer
unhardened_by_layer = defaultdict(list)
for agent in unhardened:
    unhardened_by_layer[agent['layer']].append(agent['class_name'])

untested_by_layer = defaultdict(list)
for agent in untested:
    untested_by_layer[agent['layer']].append(agent['class_name'])

print("\n" + "=" * 70)
print("UNHARDENED AGENTS BY LAYER")
print("=" * 70)
for layer in sorted(unhardened_by_layer.keys()):
    agents_list = unhardened_by_layer[layer]
    print(f"\n{layer} ({len(agents_list)} agents):")
    for agent_name in sorted(agents_list)[:10]:  # Show first 10
        print(f"  - {agent_name}")
    if len(agents_list) > 10:
        print(f"  ... and {len(agents_list) - 10} more")

print("\n" + "=" * 70)
print("UNTESTED AGENTS BY LAYER")
print("=" * 70)
for layer in sorted(untested_by_layer.keys()):
    agents_list = untested_by_layer[layer]
    print(f"\n{layer} ({len(agents_list)} agents):")
    for agent_name in sorted(agents_list)[:10]:  # Show first 10
        print(f"  - {agent_name}")
    if len(agents_list) > 10:
        print(f"  ... and {len(agents_list) - 10} more")

# Priority: L5 agents MUST be hardened (security requirement)
l5_unhardened = [a for a in unhardened if a['layer'].startswith('L5')]
if l5_unhardened:
    print("\n" + "=" * 70)
    print("⚠️  CRITICAL: L5 SAFETY AGENTS WITHOUT MCP HARDENING")
    print("=" * 70)
    for agent in l5_unhardened:
        print(f"  - {agent['class_name']} ({agent['path']})")

# Output files for refactoring
print("\n" + "=" * 70)
print("REFACTORING TARGETS")
print("=" * 70)

# Save unhardened agents to file
unhardened_file = project_root / "unhardened_agents.json"
with open(unhardened_file, 'w', encoding='utf-8') as f:
    json.dump(unhardened, f, indent=2)
print(f"Saved {len(unhardened)} unhardened agents to: {unhardened_file}")

# Save untested agents to file
untested_file = project_root / "untested_agents.json"
with open(untested_file, 'w', encoding='utf-8') as f:
    json.dump(untested, f, indent=2)
print(f"Saved {len(untested)} untested agents to: {untested_file}")

# Calculate current percentages
total = len(agents)
hardened_pct = ((total - len(unhardened)) / total * 100) if total > 0 else 0
tested_pct = ((total - len(untested)) / total * 100) if total > 0 else 0

print("\n" + "=" * 70)
print("CURRENT METRICS (TABLE 1)")
print("=" * 70)
print(f"Hardened %: {hardened_pct:.1f}%")
print(f"Test %: {tested_pct:.1f}%")
