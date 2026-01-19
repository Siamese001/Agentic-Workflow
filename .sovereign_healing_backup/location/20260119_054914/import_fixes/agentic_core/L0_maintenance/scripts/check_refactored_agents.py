#!/usr/bin/env python3
"""Check metrics for refactored agents."""
import json
from pathlib import Path
from agentic_core.utils.file_utils import safe_read_file, safe_write_file

PROJECT_ROOT = Path(__file__).parent.parent
DISCOVERY_FILE = PROJECT_ROOT / "agent_discovery_full.json"

with open(DISCOVERY_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

refactored = ['SovereignObservabilityAgent', 'NamingAgent']

for name in refactored:
    agents = [a for a in data if a['class_name'] == name]
    if agents:
        a = agents[0]
        print(f"{name}:")
        print(f"  Typed: {a['typed_pct']:.0f}%")
        print(f"  Doc: {a['documented_pct']:.0f}%")
        print(f"  Schema: {a['schema_strictness']:.0f}%")
        print()
