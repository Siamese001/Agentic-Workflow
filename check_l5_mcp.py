#!/usr/bin/env python3
"""Check L5 MCP hardening status."""
import json

with open('agent_discovery_full.json', 'r', encoding='utf-8') as f:
    agents = json.load(f)

l5_agents = [a for a in agents if a.get('layer', '').startswith('L5')]
unhardened = [a for a in l5_agents if not a.get('mcp_hardened', False)]

print(f'L5 agents: {len(l5_agents)}')
print(f'Unhardened L5 agents: {len(unhardened)}')
if unhardened:
    for a in unhardened[:10]:
        print(f"  - {a['class_name']}: mcp_hardened={a.get('mcp_hardened', 'MISSING')}")
