"""
Debug dashboard agent count discrepancy.

The dashboard shows 289 agents, but the dry run analysis says 266 files.
This investigates the difference between:
- Agent count (classes discovered)
- File count (unique files containing agents)
"""
import json
from collections import defaultdict

# Load agent registry
with open('agent_discovery_full.json', 'r') as f:
    registry = json.load(f)

print("=" * 80)
print("DASHBOARD COUNT INVESTIGATION")
print("=" * 80)

# Count agents vs files
total_agents = len(registry)
unique_files = len(set(agent['path'] for agent in registry))

print(f"\n📊 COUNTS")
print(f"Total agents (classes): {total_agents}")
print(f"Unique files: {unique_files}")
print(f"Difference: {total_agents - unique_files} agents")

# Group by file to show multi-agent files
agents_by_file = defaultdict(list)
for agent in registry:
    path = agent['path'].replace('\\', '/')
    agents_by_file[path].append(agent['class_name'])

multi_agent_files = {
    path: agents 
    for path, agents in agents_by_file.items() 
    if len(agents) > 1
}

print(f"\n📁 FILE ANALYSIS")
print(f"Single-agent files: {unique_files - len(multi_agent_files)}")
print(f"Multi-agent files: {len(multi_agent_files)}")
print(f"Total files: {unique_files}")

# Calculate agents from multi-agent files
agents_in_multi_files = sum(len(agents) for agents in multi_agent_files.values())
agents_in_single_files = total_agents - agents_in_multi_files

print(f"\n🔢 AGENT DISTRIBUTION")
print(f"Agents in single-agent files: {agents_in_single_files}")
print(f"Agents in multi-agent files: {agents_in_multi_files}")
print(f"Total agents: {total_agents}")

# Verify the math
print(f"\n✅ VERIFICATION")
print(f"Single-agent files: {unique_files - len(multi_agent_files)}")
print(f"+ Multi-agent files: {len(multi_agent_files)}")
print(f"= Total files: {unique_files}")
print()
print(f"Agents in single files: {agents_in_single_files}")
print(f"+ Agents in multi files: {agents_in_multi_files}")
print(f"= Total agents: {total_agents}")

# Show the relationship
print(f"\n💡 EXPLANATION")
print(f"The dashboard shows {total_agents} agents (CORRECT)")
print(f"The dry run shows {unique_files} files (ALSO CORRECT)")
print(f"The difference of {total_agents - unique_files} is because:")
print(f"  • {len(multi_agent_files)} files contain multiple agents")
print(f"  • Those files contain {agents_in_multi_files} agents total")
print(f"  • Average agents per multi-agent file: {agents_in_multi_files / len(multi_agent_files):.1f}")

print(f"\n🎯 CONCLUSION")
print(f"Both numbers are correct:")
print(f"  • 289 = Number of AGENT CLASSES (what dashboard counts)")
print(f"  • {unique_files} = Number of FILES containing agents")
print(f"  • The dashboard does NOT include tools - it only counts agent classes")

# Check if any tools are in the registry
tools_count = sum(1 for agent in registry if 'tool' in agent['class_name'].lower() and 'agent' not in agent['class_name'].lower())
print(f"\n🔧 TOOLS CHECK")
print(f"Classes with 'tool' in name (but not 'agent'): {tools_count}")
if tools_count > 0:
    print("Tool classes found:")
    for agent in registry:
        if 'tool' in agent['class_name'].lower() and 'agent' not in agent['class_name'].lower():
            print(f"  • {agent['class_name']} - {agent['path']}")

print(f"\n{'=' * 80}")
