#!/usr/bin/env python3
"""Check MCP hardening percentage in agent discovery data."""
import json
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.dashboard_ssot_definitions import calc_hardened_pct
from archives.location_violations.file_utils import safe_read_file, safe_write_file

# Load agent discovery
with open(project_root / "agent_discovery_full.json", 'r', encoding='utf-8') as f:
    agents = json.load(f)

print(f"Total agents: {len(agents)}")

# Count MCP hardened
mcp_hardened = sum(1 for a in agents if a.get('mcp_hardened', False))
print(f"MCP hardened: {mcp_hardened}")

# Calculate percentage
pct = calc_hardened_pct(agents)
print(f"MCP Hardened %: {pct:.1f}%")

# Check if 100%
if pct == 100.0:
    print("\n✅ 100% MCP Hardening achieved!")
else:
    print(f"\n❌ Only {pct:.1f}% MCP Hardening")
    
    # Find non-hardened agents
    non_hardened = [a for a in agents if not a.get('mcp_hardened', False)]
    if non_hardened:
        print(f"\nNon-hardened agents ({len(non_hardened)}):")
        for a in non_hardened[:10]:
            print(f"  - {a['class_name']} ({a['path']})")
