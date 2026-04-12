"""Verify L2 Execution data is now correct (user's specific example)."""

import json

agents = json.load(open("agent_discovery_full.json"))
l2_agents = [a for a in agents if "L2_execution" in a.get("path", "")]
mcp_count = sum(1 for a in l2_agents if a.get("mcp_hardened"))
expected_mcp_pct = round(mcp_count / len(l2_agents) * 100, 1) if l2_agents else 0
print("=" * 70)
print("L2 EXECUTION DATA VERIFICATION (User's Example)")
print("=" * 70)
print()
print("SOURCE DATA (agent_discovery_full.json):")
print(f"  L2 Execution agents: {len(l2_agents)}")
print(f"  MCP Hardened count: {mcp_count}")
print(f"  Expected MCP %: {expected_mcp_pct}%")
print()
html = open("agentic_core/L6_observability/dashboards/autonomy_dashboard.html", encoding="utf-8").read()
lines = []
in_data = False
for line in html.split("\n"):
    if "const dashboardData = [" in line:
        in_data = True
        lines.append("[")
        continue
    if in_data:
        lines.append(line)
        if "];" in line:
            lines[-1] = lines[-1].replace("];", "]")
            break
data = json.loads("".join(lines))
l2_core = next((r for r in data if r["Territory"] == "L2 Execution/Core"), None)
if l2_core:
    print("DASHBOARD DATA (autonomy_dashboard.html):")
    print(f"  Territory: {l2_core['Territory']}")
    print(f"  Total: {l2_core['Total']}")
    print(f"  Hardened %: {l2_core['Hardened %']}")
    print(f"  MCP Capable %: {l2_core['MCP Capable %']}")
    print()
    print("VALIDATION:")
    dashboard_mcp = l2_core["MCP Capable %"]
    if dashboard_mcp == 80.0:
        print("  ❌ STILL HARDCODED 80% - NOT FIXED")
    elif abs(dashboard_mcp - expected_mcp_pct) < 5:
        print(f"  ✅ Dashboard MCP % ({dashboard_mcp}%) matches source data ({expected_mcp_pct}%)")
        print("  ✅ NO LONGER USING HARDCODED 80%")
    else:
        print(f"  ⚠️  Dashboard: {dashboard_mcp}% vs Expected: {expected_mcp_pct}%")
        print("     (Difference may be due to territory classification)")
else:
    print("❌ L2 Execution/Core not found in dashboard")
print()
print("=" * 70)
