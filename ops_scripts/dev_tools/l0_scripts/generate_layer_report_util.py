from pathlib import Path

"Generate agent report by L0-L6 layers from agent_discovery_full.json."
import json
from collections import defaultdict
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).parent.parent
with open(PROJECT_ROOT / "agent_discovery_full.json") as f:
    agents = json.load(f)
by_layer = defaultdict(list)
for agent in agents:
    layer = agent.get("layer", "Unknown")
    by_layer[layer].append(agent)
layer_order = ["L0", "L1", "L2", "L3", "L4", "L5", "L6", "Base", "Apps", "Utils", TESTS_DIR, "Unknown"]
for layer in tqdm(layer_order, desc="Processing", unit="item"):
    if layer not in by_layer:
        continue
    agents_in_layer = by_layer[layer]
    for a in sorted(agents_in_layer, key=lambda x: x["class_name"]):
        name = a["class_name"]
        territory = a.get("territory", "Unknown")[:25]
        category = a.get("category", "Unknown")[:12]
        healing = "H" if a.get("has_healing") else "-"
        mcp = "M" if a.get("mcp_hardened") else "-"
        subatomic = "S" if a.get("has_subatomic") else "-"
        loc = a.get("loc", 0)
total = 0
for layer in layer_order:
    if layer in by_layer:
        count = len(by_layer[layer])
        total += count
        bar = "#" * (count // 2)
healing_count = sum(1 for a in agents if a.get("has_healing"))
mcp_count = sum(1 for a in agents if a.get("mcp_hardened"))
subatomic_count = sum(1 for a in agents if a.get("has_subatomic"))
tools_count = sum(1 for a in agents if a.get("has_tools"))
