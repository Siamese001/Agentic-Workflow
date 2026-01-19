#!/usr/bin/env python3
"""
Analyze cyclomatic complexity for specific agents.
Identify high-CC methods that need refactoring.
"""
import json
from pathlib import Path
from archives.location_violations.file_utils import safe_read_file, safe_write_file

# Load agent discovery data
with open('agent_discovery_full.json', 'r') as f:
    agents = json.load(f)

# Find specific agents
target_agents = [
    'SovereignBaseAgent',
    'PerformanceAnalystAgent', 
    'StrategicObservationAgent',
    'RuntimeTelemetryAgent',
    'L6ObservabilityBaseAgent'
]

print("=" * 70)
print("CYCLOMATIC COMPLEXITY ANALYSIS")
print("=" * 70)

# Sort all agents by CC (highest first)
sorted_agents = sorted(agents, key=lambda a: a.get('cyclomatic_complexity', 0), reverse=True)

print("\nTOP 20 HIGHEST CC AGENTS:")
print("-" * 70)
for i, agent in enumerate(sorted_agents[:20]):
    cc = agent.get('cyclomatic_complexity', 0)
    name = agent['class_name']
    territory = agent.get('territory', 'Unknown')
    print(f"{i+1:2}. CC={cc:3} | {name} ({territory})")

print("\n" + "=" * 70)
print("TARGET AGENTS FOR REFACTORING:")
print("=" * 70)

for target in target_agents:
    agent = next((a for a in agents if a['class_name'] == target), None)
    if agent:
        cc = agent.get('cyclomatic_complexity', 0)
        path = agent.get('path', 'unknown')
        print(f"\n{target}:")
        print(f"  CC: {cc}")
        print(f"  Path: {path}")
        print(f"  Complexity Health: {max(0, 100 - cc * 2):.1f}%")
    else:
        print(f"\n{target}: NOT FOUND")

# Calculate current average CC
total_cc = sum(a.get('cyclomatic_complexity', 0) for a in agents)
avg_cc = total_cc / len(agents) if agents else 0
print(f"\n" + "=" * 70)
print(f"OVERALL STATS:")
print(f"  Total agents: {len(agents)}")
print(f"  Average CC: {avg_cc:.1f}")
print(f"  Current Complexity Health: {max(0, 100 - avg_cc * 2):.1f}%")
print("=" * 70)
