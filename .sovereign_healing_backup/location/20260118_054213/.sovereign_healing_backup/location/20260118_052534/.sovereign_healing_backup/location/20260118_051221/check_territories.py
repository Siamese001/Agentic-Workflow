import json

with open('agent_discovery_full.json', 'r') as f:
    data = json.load(f)

# Count agents by layer
layers = {}
for agent in data:
    layer = agent.get('layer', 'Unknown')
    layers[layer] = layers.get(layer, 0) + 1

print("Agents by Layer:")
for layer, count in sorted(layers.items()):
    print(f"  {layer}: {count} agents")

print(f"\nTotal: {len(data)} agents")

# Check for L3, L4 agents
l3_agents = [a for a in data if a.get('layer', '').startswith('L3')]
l4_agents = [a for a in data if a.get('layer', '').startswith('L4')]

print(f"\nL3 agents: {len(l3_agents)}")
if l3_agents:
    print("Sample L3 agents:")
    for a in l3_agents[:5]:
        print(f"  {a['class_name']}: {a.get('path', '')[:60]}")

print(f"\nL4 agents: {len(l4_agents)}")
if l4_agents:
    print("Sample L4 agents:")
    for a in l4_agents[:5]:
        print(f"  {a['class_name']}: {a.get('path', '')[:60]}")

# Check territory distribution
territories = {}
for agent in data:
    territory = agent.get('territory', 'Unknown')
    territories[territory] = territories.get(territory, 0) + 1

print("\n\nAgents by Territory:")
for territory, count in sorted(territories.items()):
    print(f"  {territory}: {count} agents")
