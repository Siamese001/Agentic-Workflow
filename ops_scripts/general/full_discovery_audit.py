"""
Full audit of agent_discovery_full.json to identify possible misclassifications.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict
from pathlib import Path

from tqdm import tqdm

SOVEREIGN_BASES = {
    "SovereignBaseAgent",
    "L0RoutingBaseAgent",
    "L1CognitionBase",
    "L2ExecutionBase",
    "L3OrchestrationBase",
    "L4StateBase",
    "L5SafetyBase",
    "L6ObservabilityBase",
    "HealingPolicyMixin",
    "MCPOperationMixin",
    "CanonBaseAgent",
}


def _resolve_repo_root(explicit_root: str | None = None) -> Path:
    if explicit_root:
        return Path(explicit_root).expanduser().resolve()
    env_root = os.getenv("AGENTIC_WORKFLOW_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    for candidate in Path(__file__).resolve().parents:
        if (candidate / ".git").exists():
            return candidate
    return Path.cwd().resolve()


def _load_agents(discovery_json: Path) -> list[dict]:
    if not discovery_json.exists():
        raise FileNotFoundError(f"Discovery file not found: {discovery_json}")
    with discovery_json.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError(f"Expected a list of agent entries in {discovery_json}")
    return data


def audit_discovery(discovery_json: Path) -> dict[str, list[dict]]:
    agents = _load_agents(discovery_json)

    print(f"Total agents discovered: {len(agents)}")
    print("=" * 100)

    categories: dict[str, list[dict]] = defaultdict(list)

    for agent in tqdm(agents, desc="Processing", unit="item"):
        path = str(agent.get("path", "")).replace("\\", "/")
        name = str(agent.get("class_name", ""))
        has_healing = bool(agent.get("has_healing", False))
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
            reasons: list[str] = []
            if not ends_with_agent:
                reasons.append("No 'Agent' suffix")
            if not has_sovereign_base:
                reasons.append("No sovereign base")
            if not has_healing:
                reasons.append("No healing capability")
            categories["NOT_TRUE_SOVEREIGN"].append(
                {
                    "name": name,
                    "path": path,
                    "layer": layer,
                    "inheritance": sorted(inheritance),
                    "has_healing": has_healing,
                    "reason": reasons,
                }
            )

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
    layer_counts: dict[str, int] = defaultdict(int)
    for agent in agents:
        layer_counts[str(agent.get("layer", "unknown"))] += 1
    for layer in sorted(layer_counts):
        print(f"  {layer}: {layer_counts[layer]}")

    return categories


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit agent discovery results for likely sovereign-agent misclassifications.",
    )
    parser.add_argument("--repo-root", help="Override automatic repository root detection.")
    parser.add_argument(
        "--discovery-json",
        help="Path to agent_discovery_full.json. Defaults to the file under the detected repo root.",
    )
    args = parser.parse_args(argv)

    repo_root = _resolve_repo_root(args.repo_root)
    discovery_json = (
        Path(args.discovery_json).expanduser().resolve()
        if args.discovery_json
        else repo_root / "agent_discovery_full.json"
    )

    try:
        audit_discovery(discovery_json)
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
