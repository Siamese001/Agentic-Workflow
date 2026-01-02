"""
List agents by layer for batch hardening.

Reads from agent_discovery_full.json - run full_agent_discovery.py first.
"""
import json
import sys

layer = sys.argv[1] if len(sys.argv) > 1 else 'apps_rg'
data = json.load(open('agent_discovery_full.json'))
agents = [a for a in data if a.get('layer') == layer]

print(f"{layer} agents ({len(agents)}):")
for a in agents:
    heal = 'H' if a.get('has_healing') else '-'
    mcp = 'M' if a.get('mcp_hardened') else '-'
    test = 'T' if a.get('testing') != 'None' else '-'
    print(f"  [{heal}{mcp}{test}] {a['class_name']} - {a['path']}")
