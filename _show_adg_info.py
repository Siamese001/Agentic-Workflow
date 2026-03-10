#!/usr/bin/env python3
"""Show ADG sovereign territory coverage."""

import json
from pathlib import Path

adg_path = Path("artifacts/adg/adg_full_20260310T012640Z.json")

with open(adg_path) as f:
    data = json.load(f)

metadata = data.get("metadata", {})
nodes = data.get("nodes", [])
edges = data.get("edges", [])

print("=" * 80)
print("📊 AST DEPENDENCY GRAPH (ADG) - LATEST OUTPUT")
print("=" * 80)
print()
print(f"📁 Location: {adg_path}")
print(f"📅 Timestamp: {metadata.get('timestamp', 'N/A')}")
print(f"📦 Total Nodes: {len(nodes):,}")
print(f"🔗 Total Edges: {len(edges):,}")
print()

# Analyze sovereign territory coverage
territories = {}
for node in nodes:
    territory = node.get("sovereign_territory", "unknown")
    if territory not in territories:
        territories[territory] = {"count": 0, "modules": set()}
    territories[territory]["count"] += 1
    module = node.get("module", "")
    if module:
        territories[territory]["modules"].add(module.split(".")[0])

print("🏛️  SOVEREIGN TERRITORY COVERAGE:")
print("-" * 80)

for territory in sorted(territories.keys()):
    if territory == "unknown":
        continue
    info = territories[territory]
    print(f"\n📍 {territory}")
    print(f"   Nodes: {info['count']:,}")
    print(f"   Top-level modules: {len(info['modules'])}")
    if len(info["modules"]) <= 10:
        for mod in sorted(info["modules"]):
            print(f"      - {mod}")

if "unknown" in territories:
    print(f"\n⚠️  Unknown territory: {territories['unknown']['count']} nodes")

print()
print("=" * 80)
