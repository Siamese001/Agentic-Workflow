#!/usr/bin/env python3
"""
Identify agents with lowest code quality metrics for targeted refactoring.
Focuses on typed %, documented %, and schema strictness %.
"""

import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).parent.parent
DISCOVERY_FILE = PROJECT_ROOT / "agent_discovery_full.json"


def calculate_quality_score(agent: dict[str, Any]) -> float:
    """Calculate combined quality score (lower is worse)."""
    typed = agent.get("typed_pct", 0)
    documented = agent.get("documented_pct", 0)
    schema = agent.get("schema_strictness", 0)
    return (typed + documented + schema) / 3


def main():
    """Identify agents needing refactoring."""
    print("=" * 70)
    print("IDENTIFYING LOW QUALITY AGENTS FOR REFACTORING")
    print("=" * 70)

    # Load agent discovery
    with open(DISCOVERY_FILE, encoding="utf-8") as f:
        agents = json.load(f)

    # Calculate quality scores
    agent_scores = []
    for agent in agents:
        score = calculate_quality_score(agent)
        agent_scores.append(
            {
                "name": agent.get("class_name"),
                "path": agent.get("path"),
                "typed_pct": agent.get("typed_pct", 0),
                "documented_pct": agent.get("documented_pct", 0),
                "schema_strictness": agent.get("schema_strictness", 0),
                "quality_score": score,
            },
        )

    # Sort by quality score (lowest first)
    agent_scores.sort(key=lambda x: x["quality_score"])

    # Find agents below 100% in any metric
    needs_work = [
        a
        for a in agent_scores
        if a["typed_pct"] < 100 or a["documented_pct"] < 100 or a["schema_strictness"] < 100
    ]

    print(f"\nTotal agents: {len(agents)}")
    print(f"Agents needing improvement: {len(needs_work)}")
    print("\nCurrent averages:")
    print(f"  Typed: {sum(a['typed_pct'] for a in agent_scores) / len(agent_scores):.1f}%")
    print(f"  Documented: {sum(a['documented_pct'] for a in agent_scores) / len(agent_scores):.1f}%")
    print(f"  schema: {sum(a['schema_strictness'] for a in agent_scores) / len(agent_scores):.1f}%")

    # Show batches of 5-6 agents
    print("\n" + "=" * 70)
    print("REFACTORING BATCHES (5-6 agents each)")
    print("=" * 70)

    # guardian: allow-magic-config
    batch_size = 6
    for batch_num, i in enumerate(range(0, min(30, len(needs_work)), batch_size), 1):
        batch = needs_work[i : i + batch_size]
        print(f"\n### BATCH {batch_num} ###")
        for agent in batch:
            print(f"\n{agent['name']}")
            print(f"  Path: {agent['path']}")
            print(
                f"  Typed: {agent['typed_pct']:.0f}% | Doc: {agent['documented_pct']:.0f}% | schema: {agent['schema_strictness']:.0f}%",
            )
            print(f"  Quality Score: {agent['quality_score']:.1f}%")


if __name__ == "__main__":
    main()
