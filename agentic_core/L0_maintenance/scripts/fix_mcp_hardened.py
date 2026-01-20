#!/usr/bin/env python3
"""Fix SemanticDebuggerAgent mcp_hardened flag."""
import json
from pathlib import Path
from agentic_core.utils.file_utils import safe_read_file, safe_write_file

PROJECT_ROOT = Path(__file__).parent.parent

with open(PROJECT_ROOT / 'agent_discovery_full.json', 'r', encoding='utf-8') as f:
    agents = json.load(f)

for agent in agents:
    if agent['class_name'] == 'SemanticDebuggerAgent':
        print(f"Before: mcp_hardened = {agent.get('mcp_hardened')}")
        agent['mcp_hardened'] = True
        print(f"After: mcp_hardened = {agent.get('mcp_hardened')}")

with open(PROJECT_ROOT / 'agent_discovery_full.json', 'w', encoding='utf-8') as f:
    json.dump(agents, f, indent=2)

print("Fixed!")
