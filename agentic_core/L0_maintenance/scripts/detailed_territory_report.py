from pathlib import Path

"""Generate detailed agent report by territory."""
import json

PROJECT_ROOT = Path(__file__).parent.parent
with open(PROJECT_ROOT / "agent_discovery_full.json") as f:
    agents = json.load(f)
by_territory = defaultdict(list)
for agent in agents:
    layer = agent.get("layer", "Unknown")
    territory = agent.get("territory", "Unknown")
    path = agent.get("path", "")
    if layer in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]:
        key = f"CORE_{layer}"
    elif layer == "Base":
        key = "BASE_AGENTS"
    elif "apps_lic" in path.lower() or "Apps Lic" in territory:
        key = "APPS_LIC"
    elif "apps_rg" in path.lower() or "Apps Rg" in territory:
        key = "APPS_RG"
    elif "apps_shared" in path.lower() or "Apps Shared" in territory:
        key = "APPS_SHARED"
    elif layer == "Apps":
        if "lic" in path.lower():
            key = "APPS_LIC"
        elif "rg" in path.lower():
            key = "APPS_RG"
        else:
            key = "APPS_OTHER"
    else:
        key = f"OTHER_{layer}"
    by_territory[key].append(agent)
sections = [
    ("CORE_L0", "L0 - MAINTENANCE"),
    ("CORE_L1", "L1 - COGNITION"),
    ("CORE_L2", "L2 - EXECUTION"),
    ("CORE_L3", "L3 - ORCHESTRATION"),
    ("CORE_L4", "L4 - STATE"),
    ("CORE_L5", "L5 - SAFETY"),
    ("CORE_L6", "L6 - OBSERVABILITY"),
    ("BASE_AGENTS", "BASE AGENTS"),
    ("APPS_LIC", "APPS - LIC"),
    ("APPS_RG", "APPS - RG"),
    ("APPS_SHARED", "APPS - SHARED"),
    ("APPS_OTHER", "APPS - OTHER"),
    ("OTHER_Utils", "UTILS"),
    ("OTHER_tests", "TESTS"),
    ("OTHER_Unknown", "UNKNOWN"),
]
total = 0
for key, _title in sections:
    if key not in by_territory:
        continue
    agents_list = by_territory[key]
    total += len(agents_list)
    for a in sorted(agents_list, key=lambda x: x["class_name"]):
        name = a["class_name"]
        category = a.get("category", "-")[:10]
        healing = "H" if a.get("has_healing") else "-"
        mcp = "M" if a.get("mcp_hardened") else "-"
        subatomic = "S" if a.get("has_subatomic") else "-"
        loc = a.get("loc", 0)
for key, _title in sections:
    if key in by_territory:
        count = len(by_territory[key])
        bar = "#" * (count // 3)
