#!/usr/bin/env python3
"""Check base agent naming conventions."""
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
data = json.load(open(PROJECT_ROOT / 'agent_discovery_full.json'))

print("Base Agents by Territory:")
print("=" * 60)
bases = [a for a in data if 'Base' in a.get('territory', '')]
for a in bases:
    print(f"  {a['class_name']:40} -> {a['territory']}")

print("\n" + "=" * 60)
print("Base Agent Class Names:")
for a in bases:
    print(f"  {a['class_name']}")
