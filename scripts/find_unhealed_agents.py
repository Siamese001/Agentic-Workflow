"""Find standalone agents without healing capability."""
import json

with open('agent_discovery_full.json', 'r') as f:
    data = json.load(f)

# Find core agents (L0-L5) without healing
core_layers = {'L0', 'L1', 'L2', 'L3', 'L4', 'L5'}
unhealed = [a for a in data if a['layer'] in core_layers and not a['has_healing']]

print(f"Core agents without healing: {len(unhealed)}/234")
print("\nBy layer:")
for layer in sorted(core_layers):
    layer_agents = [a for a in unhealed if a['layer'] == layer]
    print(f"\n  {layer}: {len(layer_agents)} agents")
    for a in layer_agents[:10]:  # Show first 10
        inheritance = ', '.join(a['inheritance']) if a['inheritance'] else 'standalone'
        print(f"    - {a['class_name']} ({inheritance})")
