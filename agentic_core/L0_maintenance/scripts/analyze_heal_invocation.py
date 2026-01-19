#!/usr/bin/env python3
"""Analyze heal invocation coverage and identify agents needing fixes."""
import json
from pathlib import Path
from collections import defaultdict
from archives.location_violations.file_utils import safe_read_file, safe_write_file

# Load agent discovery data
data = json.load(open('agent_discovery_full.json'))

# Categorize agents
has_healing = [a for a in data if a.get('has_healing')]
has_invocation = [a for a in data if a.get('invocation') == 'Yes']
needs_invocation = [a for a in data if a.get('has_healing') and a.get('invocation') != 'Yes']

print("=" * 80)
print("HEAL INVOCATION COVERAGE ANALYSIS")
print("=" * 80)
print()
print(f"Total agents: {len(data)}")
print(f"Agents with healing capability: {len(has_healing)} ({len(has_healing)/len(data)*100:.1f}%)")
print(f"Agents with heal invocation: {len(has_invocation)} ({len(has_invocation)/len(data)*100:.1f}%)")
print(f"Agents needing invocation: {len(needs_invocation)}")
print()

if needs_invocation:
    print("AGENTS MISSING HEAL INVOCATION:")
    print("-" * 80)
    
    # Group by layer
    by_layer = defaultdict(list)
    for agent in needs_invocation:
        layer = agent.get('layer', 'Unknown')
        by_layer[layer].append(agent)
    
    for layer in sorted(by_layer.keys()):
        agents = by_layer[layer]
        print(f"\n{layer}: {len(agents)} agents")
        for agent in agents:
            path = agent.get('path', 'unknown')
            name = agent.get('class_name', 'unknown')
            print(f"  - {name}")
            print(f"    Path: {path}")
            print(f"    Has healing: {agent.get('has_healing')}")
            print(f"    Invocation: {agent.get('invocation', 'No')}")

print()
print("=" * 80)
print(f"TARGET: 100% heal invocation ({len(data)} agents)")
print(f"CURRENT: {len(has_invocation)/len(data)*100:.1f}% ({len(has_invocation)} agents)")
print(f"GAP: {len(needs_invocation)} agents need heal_repository() calls added")
print("=" * 80)
