"""Generate agent report in dashboard table style with territory/sub-territory rows."""

import json
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent
with open(PROJECT_ROOT / "agent_discovery_full.json") as f:
    agents = json.load(f)
by_territory = defaultdict(list)
for agent in agents:
    territory = agent.get("territory", "Unknown")
    layer = agent.get("layer", "Unknown")
    if territory == "Sovereign Base Agent" and layer == "Base":
        territory = "Base Agents"
    by_territory[territory].append(agent)


def calc_pct(agents_list, key, true_val=True):
    """TODO: Add documentation for calc_pct."""
    if not agents_list:
        return 0.0
    count = sum(1 for a in agents_list if a.get(key) == true_val)
    return 100.0 * count / len(agents_list)


def calc_avg(agents_list, key):
    """TODO: Add documentation for calc_avg."""
    if not agents_list:
        return 0.0
    vals = [a.get(key, 0) or 0 for a in agents_list]
    return sum(vals) / len(vals) if vals else 0.0


rows = []
for territory in sorted(by_territory.keys()):
    agents_list = by_territory[territory]
    row = {
        "Territory": territory,
        "Total": len(agents_list),
        "Heal Cap %": calc_pct(agents_list, "has_healing"),
        "MCP Hardened %": calc_pct(agents_list, "mcp_hardened"),
        "Subatomic %": calc_pct(agents_list, "has_subatomic"),
        "Has Tools %": calc_pct(agents_list, "has_tools"),
        "Has Tests %": calc_pct(agents_list, "has_tests"),
        "Typed %": calc_avg(agents_list, "typed_pct"),
        "Documented %": calc_avg(agents_list, "documented_pct"),
        "schema %": calc_avg(agents_list, "schema_strictness"),
        "Proper Base %": calc_pct(agents_list, "proper_base_class"),
    }
    rows.append(row)
all_agents = agents
total_row = {
    "Territory": "TOTAL",
    "Total": len(all_agents),
    "Heal Cap %": calc_pct(all_agents, "has_healing"),
    "MCP Hardened %": calc_pct(all_agents, "mcp_hardened"),
    "Subatomic %": calc_pct(all_agents, "has_subatomic"),
    "Has Tools %": calc_pct(all_agents, "has_tools"),
    "Has Tests %": calc_pct(all_agents, "has_tests"),
    "Typed %": calc_avg(all_agents, "typed_pct"),
    "Documented %": calc_avg(all_agents, "documented_pct"),
    "schema %": calc_avg(all_agents, "schema_strictness"),
    "Proper Base %": calc_pct(all_agents, "proper_base_class"),
}
header = f"{'Territory':<45} {'#':>4} {'Heal%':>6} {'MCP%':>6} {'Sub%':>6} {'Tool%':>6} {'Test%':>6} {'Type%':>6} {'Doc%':>6} {'schema%':>7} {'Base%':>6}"
r = total_row
current_group = None
for r in rows:
    territory = r["Territory"]
    if territory.startswith("L0"):
        group = "L0"
    elif territory.startswith("L1"):
        group = "L1"
    elif territory.startswith("L2"):
        group = "L2"
    elif territory.startswith("L3"):
        group = "L3"
    elif territory.startswith("L4"):
        group = "L4"
    elif territory.startswith("L5"):
        group = "L5"
    elif territory.startswith("L6"):
        group = "L6"
    elif territory.startswith("Apps Lic"):
        group = "Apps Lic"
    elif territory.startswith("Apps Rg"):
        group = "Apps Rg"
    elif territory.startswith("Apps Shared"):
        group = "Apps Shared"
    else:
        group = "Other"
    if group != current_group:
        if current_group is not None:
            pass
        current_group = group
