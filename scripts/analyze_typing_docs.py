#!/usr/bin/env python3
"""Analyze agents with low typed % and documented %."""
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
data = json.load(open(PROJECT_ROOT / 'agent_discovery_full.json'))

# Find agents with low typing
low_typed = [a for a in data if a.get('typed_pct', 100) < 100]
low_doc = [a for a in data if a.get('documented_pct', 100) < 100]

print(f"Total agents: {len(data)}")
print(f"Agents with typed_pct < 100%: {len(low_typed)}")
print(f"Agents with documented_pct < 100%: {len(low_doc)}")

print("\n" + "=" * 70)
print("LOW TYPED (< 100%) - sorted by typed_pct")
print("=" * 70)
for a in sorted(low_typed, key=lambda x: x.get('typed_pct', 0)):
    print(f"  {a['typed_pct']:.0f}% | {a['class_name']}")
    print(f"       {a['path']}")

print("\n" + "=" * 70)
print("LOW DOCUMENTED (< 100%) - sorted by documented_pct")
print("=" * 70)
for a in sorted(low_doc, key=lambda x: x.get('documented_pct', 0)):
    print(f"  {a['documented_pct']:.0f}% | {a['class_name']}")
    print(f"       {a['path']}")
