#!/usr/bin/env python3
"""
Run NamingAgent to scan for duplicate filenames and class names.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))

from agentic_core.L5_safety.reasoning.NamingAgent import get_naming_agent

print("=" * 80)
print("NAMING AGENT SCAN - Duplicate Detection")
print("=" * 80)

# Initialize NamingAgent
naming = get_naming_agent(project_root)

# Scan for duplicate filenames
print("\n[1] Scanning for duplicate FILENAMES...")
duplicates = naming.scan_for_duplicate_filenames()

if duplicates:
    print(f"\n❌ Found {len(duplicates)} duplicate filenames:")
    for basename, paths in sorted(duplicates.items()):
        print(f"\n  {basename} ({len(paths)} occurrences):")
        for p in paths:
            print(f"    - {p.relative_to(project_root)}")
else:
    print("\n✅ No duplicate filenames found")

# Scan for duplicate class names using discovery JSON
print("\n" + "=" * 80)
print("[2] Scanning for duplicate CLASS NAMES...")
import json
from collections import defaultdict

from agentic_core.L0_routing.config import AGENT_DISCOVERY_JSON

discovery_path = project_root / AGENT_DISCOVERY_JSON
if discovery_path.exists():
    agents = json.loads(discovery_path.read_text(encoding="utf-8"))

    by_name = defaultdict(list)
    for a in agents:
        by_name[a["class_name"]].append(a["path"])

    dup_classes = {k: v for k, v in by_name.items() if len(v) > 1}

    if dup_classes:
        print(f"\n❌ Found {len(dup_classes)} duplicate class names:")
        for name, paths in sorted(dup_classes.items()):
            print(f"\n  {name} ({len(paths)} occurrences):")
            for p in paths:
                print(f"    - {p}")
    else:
        print("\n✅ No duplicate class names found")
else:
    print("\n⚠️  agent_discovery_full.json not found - run full_agent_discovery.py first")

print("\n" + "=" * 80)
print("SCAN COMPLETE")
print("=" * 80)
