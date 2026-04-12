"""
Full audit of agent_discovery_full.json to identify any misclassifications.

Checks for:
1. Classes that don't end with 'Agent'
2. Classes in scripts/, utils/, mixins/ paths
3. Classes without heal_repository capability
4. Classes that inherit only from non-sovereign bases
"""

import json
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DISCOVERY_JSON = PROJECT_ROOT / "agent_discovery_full.json"
SOVEREIGN_BASES = {
    "SovereignBaseAgent",
    "L0RoutingBaseAgent",
    "L1CognitionBase",
    "L2ExecutionBase",
    "L3OrchestrationBase",
    "L4StateBase",
    "L5SafetyBase",
    "L6ObservabilityBase",
    "HealerMixin",
    "MCPHardenedMixin",
    "CanonBaseAgent",
}


def audit_discovery():
    """Full audit of agent discovery."""
    with open(DISCOVERY_JSON, encoding="utf-8") as f:
        agents = json.load(f)
    print(f"Total agents discovered: {len(agents)}")
    print("=" * 100)
    categories = defaultdict(list)
    for agent in agents:
        path = agent.get("path", "").replace("\\", "/")
        name = agent.get("class_name", "")
        has_healing = agent.get("has_healing", False)
        inheritance = set(agent.get("inheritance", []))
        layer = agent.get("layer", "unknown")
        ends_with_agent = name.endswith("Agent")
        has_sovereign_base = bool(inheritance & SOVEREIGN_BASES)
        in_scripts = "/scripts/" in path.lower()
        in_utils = "/utils/" in path.lower()
        is_mixin = "Mixin" in name
        is_base_agent = name.endswith("BaseAgent")
        is_true_sovereign = ends_with_agent and (has_sovereign_base or has_healing or is_base_agent)
        if not is_true_sovereign:
            categories["NOT_TRUE_SOVEREIGN"].append(
                {
                    "name": name,
                    "path": path,
                    "layer": layer,
                    "inheritance": list(inheritance),
                    "has_healing": has_healing,
                    "reason": [],
                }
            )
            if not ends_with_agent:
                categories["NOT_TRUE_SOVEREIGN"][-1]["reason"].append("No 'Agent' suffix")
            if not has_sovereign_base:
                categories["NOT_TRUE_SOVEREIGN"][-1]["reason"].append("No sovereign base")
            if not has_healing:
                categories["NOT_TRUE_SOVEREIGN"][-1]["reason"].append("No healing capability")
        if in_scripts:
            categories["IN_SCRIPTS"].append({"name": name, "path": path, "is_true": is_true_sovereign})
        if in_utils:
            categories["IN_UTILS"].append({"name": name, "path": path, "is_true": is_true_sovereign})
        if is_mixin:
            categories["IS_MIXIN"].append({"name": name, "path": path, "is_true": is_true_sovereign})
    print("\n" + "=" * 100)
    print("AUDIT RESULTS")
    print("=" * 100)
    true_sovereigns = len(agents) - len(categories["NOT_TRUE_SOVEREIGN"])
    print(f"\nTrue Sovereign Agents: {true_sovereigns}/{len(agents)}")
    if categories["NOT_TRUE_SOVEREIGN"]:
        print(f"\n⚠️  POTENTIAL MISCLASSIFICATIONS ({len(categories['NOT_TRUE_SOVEREIGN'])}):")
        print("-" * 80)
        for item in categories["NOT_TRUE_SOVEREIGN"]:
            print(f"  {item['name']}")
            print(f"    Path: {item['path']}")
            print(f"    Layer: {item['layer']}")
            print(f"    Inheritance: {item['inheritance'][:3]}")
            print(f"    Has Healing: {item['has_healing']}")
            print(f"    Issues: {', '.join(item['reason'])}")
    if categories["IN_SCRIPTS"]:
        print(f"\n📁 AGENTS IN scripts/ DIRECTORIES ({len(categories['IN_SCRIPTS'])}):")
        for item in categories["IN_SCRIPTS"]:
            status = "✅" if item["is_true"] else "❌"
            print(f"  {status} {item['name']}: {item['path']}")
    if categories["IN_UTILS"]:
        print(f"\n📁 AGENTS IN utils/ DIRECTORIES ({len(categories['IN_UTILS'])}):")
        for item in categories["IN_UTILS"]:
            status = "✅" if item["is_true"] else "❌"
            print(f"  {status} {item['name']}: {item['path']}")
    if categories["IS_MIXIN"]:
        print(f"\n🔧 MIXINS IN DISCOVERY ({len(categories['IS_MIXIN'])}):")
        for item in categories["IS_MIXIN"]:
            status = "✅" if item["is_true"] else "❌"
            print(f"  {status} {item['name']}: {item['path']}")
    print("\n" + "=" * 100)
    print("LAYER DISTRIBUTION")
    print("=" * 100)
    layer_counts = defaultdict(int)
    for agent in agents:
        layer_counts[agent.get("layer", "unknown")] += 1
    for layer in sorted(layer_counts.keys()):
        print(f"  {layer}: {layer_counts[layer]}")
    return categories


if __name__ == "__main__":
    audit_discovery()
