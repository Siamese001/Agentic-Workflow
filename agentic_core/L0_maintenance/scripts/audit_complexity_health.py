#!/usr/bin/env python3
"""
Audit complexity health % across all agents.
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DISCOVERY_FILE = PROJECT_ROOT / "agent_discovery_full.json"


def main():
    """Audit complexity health metrics."""
    print("=" * 70)
    print("COMPLEXITY HEALTH AUDIT")
    print("=" * 70)

    # Load agent discovery
    with open(DISCOVERY_FILE, encoding="utf-8") as f:
        agents = json.load(f)

    total = len(agents)

    # Analyze complexity
    # Complexity health is typically calculated as: max(0, 100 - (complexity - 10) * 7)
    # Where complexity >= 10 starts reducing health

    complexity_data = []
    for a in agents:
        cc = a.get("cyclomatic_complexity", 1)
        # Calculate complexity health (100% for CC <= 10, decreases after)
        if cc <= 10:
            health = 100.0
        else:
            health = max(0, 100 - (cc - 10) * 7)

        complexity_data.append(
            {"name": a["class_name"], "path": a["path"], "complexity": cc, "health": health}
        )

    # Sort by health (lowest first)
    complexity_data.sort(key=lambda x: (x["health"], -x["complexity"]))

    # Calculate stats
    avg_complexity = sum(d["complexity"] for d in complexity_data) / total
    avg_health = sum(d["health"] for d in complexity_data) / total

    at_100 = sum(1 for d in complexity_data if d["health"] == 100.0)
    below_100 = sum(1 for d in complexity_data if d["health"] < 100.0)

    print(f"\nTotal agents: {total}")
    print(f"Average cyclomatic complexity: {avg_complexity:.1f}")
    print(f"Average complexity health: {avg_health:.1f}%")
    print(f"\nAgents at 100% health: {at_100}/{total} ({at_100 / total * 100:.1f}%)")
    print(f"Agents below 100% health: {below_100}/{total} ({below_100 / total * 100:.1f}%)")

    print("\n" + "=" * 70)
    print("AGENTS WITH LOW COMPLEXITY HEALTH")
    print("=" * 70)

    low_health = [d for d in complexity_data if d["health"] < 100.0]

    if not low_health:
        print("\n✅ All agents have 100% complexity health!")
    else:
        print(f"\n{len(low_health)} agents need complexity reduction:")
        print("-" * 70)

        for i, agent in enumerate(low_health[:30], 1):
            print(f"\n{i}. {agent['name']}")
            print(f"   Path: {agent['path']}")
            print(f"   Cyclomatic Complexity: {agent['complexity']}")
            print(f"   Complexity Health: {agent['health']:.1f}%")

            # Suggest target
            if agent["complexity"] > 10:
                reduction_needed = agent["complexity"] - 10
                print(f"   → Reduce by {reduction_needed} to reach 100% health")

    print("\n" + "=" * 70)
    print("COMPLEXITY DISTRIBUTION")
    print("=" * 70)

    ranges = [
        (1, 5, "Very Low (1-5)"),
        (6, 10, "Low (6-10)"),
        (11, 15, "Medium (11-15)"),
        (16, 20, "High (16-20)"),
        (21, 50, "Very High (21-50)"),
        (51, 1000, "Critical (51+)"),
    ]

    for low, high, label in ranges:
        count = sum(1 for d in complexity_data if low <= d["complexity"] <= high)
        if count > 0:
            print(f"  {label}: {count} agents")


if __name__ == "__main__":
    main()
