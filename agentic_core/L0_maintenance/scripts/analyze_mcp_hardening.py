#!/usr/bin/env python3
"""Analyze MCP hardening coverage and identify agents needing fixes."""
import json
from pathlib import Path
from collections import defaultdict
from agentic_core.utils.file_utils import safe_read_file, safe_write_file

# Load agent discovery data
data = json.load(open('agent_discovery_full.json'))

# Categorize agents
total = len(data)
hardened = [a for a in data if a.get('mcp_hardened')]
not_hardened = [a for a in data if not a.get('mcp_hardened')]

print("=" * 80)
print("MCP HARDENING COVERAGE ANALYSIS")
print("=" * 80)
print()
print(f"Total agents: {total}")
print(f"MCP hardened: {len(hardened)} ({len(hardened)/total*100:.1f}%)")
print(f"Not hardened: {len(not_hardened)} ({len(not_hardened)/total*100:.1f}%)")
print()

if not_hardened:
    print("AGENTS MISSING MCP HARDENING:")
    print("-" * 80)
    
    # Group by layer
    by_layer = defaultdict(list)
    for agent in not_hardened:
        layer = agent.get('layer', 'Unknown')
        by_layer[layer].append(agent)
    
    for layer in sorted(by_layer.keys()):
        agents = by_layer[layer]
        print(f"\n{layer}: {len(agents)} agents")
        for agent in agents:
            name = agent.get('class_name', 'unknown')
            path = agent.get('path', 'unknown')
            inheritance = agent.get('inheritance', [])
            print(f"  - {name}")
            print(f"    Path: {path}")
            print(f"    Current inheritance: {', '.join(inheritance) if inheritance else 'None'}")

print()
print("=" * 80)
print(f"TARGET: 100% MCP hardening ({total} agents)")
print(f"CURRENT: {len(hardened)/total*100:.1f}% ({len(hardened)} agents)")
print(f"GAP: {len(not_hardened)} agents need MCPHardenedMixin")
print("=" * 80)
