#!/usr/bin/env python3
"""Find which L0 Maintenance/Core agent is not MCP hardened."""
import json
from pathlib import Path
from archives.location_violations.file_utils import safe_read_file, safe_write_file

project_root = Path(__file__).parent.parent

with open(project_root / "agent_discovery_full.json", 'r', encoding='utf-8') as f:
    data = json.load(f)

l0_agents = [a for a in data if a.get('territory') == 'L0 Maintenance/Core']
print(f"L0 Maintenance/Core agents: {len(l0_agents)}")

non_hardened = [a for a in l0_agents if not a.get('mcp_hardened', False)]
print(f"\nNon-MCP hardened: {len(non_hardened)}")

if non_hardened:
    print("\nAgents WITHOUT MCP hardening:")
    for a in non_hardened:
        print(f"  ❌ {a['class_name']}")
        print(f"     Path: {a['path']}")
        print(f"     Inheritance: {a.get('inheritance', [])}")
else:
    print("\n✅ All L0 Maintenance/Core agents are MCP hardened")

# Also check the percentage
hardened_count = len([a for a in l0_agents if a.get('mcp_hardened', False)])
total_count = len(l0_agents)
percentage = (hardened_count / total_count * 100) if total_count > 0 else 0

print(f"\nMCP Hardening: {hardened_count}/{total_count} = {percentage:.1f}%")
