#!/usr/bin/env python3
"""Find the remaining agents missing heal_repository."""

import json
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from agentic_core.utils.project_root_util import get_project_root

# Load agent discovery
project_root = get_project_root()
with open(project_root / "agent_discovery_full.json", encoding="utf-8") as f:
    data = json.load(f)

# Find agents missing heal_repository
missing = [a for a in data if not a.get("has_healing")]
print(f"Agents missing healing: {len(missing)}")

for agent in missing:
    print(f"  {agent['path']}")
