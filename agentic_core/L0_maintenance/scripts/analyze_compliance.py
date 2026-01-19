#!/usr/bin/env python3
"""Analyze agent compliance for MCP hardening and test coverage."""
import json
from pathlib import Path
from archives.location_violations.file_utils import safe_read_file, safe_write_file

project_root = Path(__file__).parent.parent
discovery_file = project_root / "agent_discovery_full.json"

with open(discovery_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total agents: {len(data)}")

# MCP Hardening analysis
non_mcp = [a for a in data if not a.get('mcp_hardened', False)]
print(f"\nNon-MCP hardened: {len(non_mcp)}")
if non_mcp:
    print("\n--- Non-MCP Hardened Agents ---")
    for a in non_mcp:
        print(f"  {a['class_name']} ({a['path']})")

# Test coverage analysis
no_tests = [a for a in data if not a.get('has_tests', False)]
print(f"\nAgents without tests: {len(no_tests)}")
if no_tests:
    print("\n--- Agents Without Tests (first 30) ---")
    for a in no_tests[:30]:
        print(f"  {a['class_name']} ({a['path']})")
    if len(no_tests) > 30:
        print(f"  ... and {len(no_tests) - 30} more")

# Summary by territory
print("\n--- Compliance by Territory ---")
territories = {}
for a in data:
    t = a.get('territory', 'Unknown')
    if t not in territories:
        territories[t] = {'total': 0, 'mcp': 0, 'tests': 0}
    territories[t]['total'] += 1
    if a.get('mcp_hardened', False):
        territories[t]['mcp'] += 1
    if a.get('has_tests', False):
        territories[t]['tests'] += 1

for t, stats in sorted(territories.items()):
    mcp_pct = (stats['mcp'] / stats['total']) * 100 if stats['total'] > 0 else 0
    test_pct = (stats['tests'] / stats['total']) * 100 if stats['total'] > 0 else 0
    print(f"  {t}: MCP {mcp_pct:.0f}% ({stats['mcp']}/{stats['total']}), Tests {test_pct:.0f}% ({stats['tests']}/{stats['total']})")
