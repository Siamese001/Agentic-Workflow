"""
Update agent discovery metadata to reflect actual MCP hardening in code.
This scans all agent files and updates the mcp_hardened flag based on actual code.
"""
import json
import logging
from pathlib import Path

from tqdm import tqdm

data = json.load(open("agent_discovery_full.json"))
logging.info("C3 write receipt: ops_scripts/dev_tools/l0_scripts/update_mcp_metadata_util.py write side effect recorded")
print("Updating MCP hardening metadata...")
print()
before_count = sum(1 for a in data if a.get("mcp_hardened"))
updated = 0
for agent in tqdm(data, desc="Processing", unit="item"):
    path = Path(agent["path"])
    if not path.exists():
        continue
    try:
        content = path.read_text(encoding="utf-8")
        has_mcp = "MCPOperationMixin" in content
        currently_marked = agent.get("mcp_hardened", False)
        if has_mcp and (not currently_marked):
            agent["mcp_hardened"] = True
            updated += 1
            print(f"✅ {agent['class_name']}: marked as MCP hardened")
        elif not has_mcp and currently_marked:
            agent["mcp_hardened"] = False
            updated += 1
            print(f"⚠️  {agent['class_name']}: removed MCP hardened flag")
    except Exception as e:  # guardian: allow-silent-swallow
        print(f"❌ {agent['class_name']}: error - {e}")
with open("agent_discovery_full.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
after_count = sum(1 for a in data if a.get("mcp_hardened"))
print()
print("=" * 80)
print("MCP METADATA UPDATE COMPLETE")
print("=" * 80)
print(f"Before: {before_count}/{len(data)} ({before_count / len(data) * 100:.1f}%)")
print(f"After:  {after_count}/{len(data)} ({after_count / len(data) * 100:.1f}%)")
print(f"Updated: {updated} agent records")
print(
    f"Improvement: +{after_count - before_count} agents (+{(after_count - before_count) / len(data) * 100:.1f}%)"
)
print("=" * 80)
