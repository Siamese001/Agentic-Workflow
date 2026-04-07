"""
Batch refactor agents to add type hints and improve docstrings.
Targets agents with 50-83% quality scores.
"""

import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).parent.parent
DISCOVERY_FILE = PROJECT_ROOT / "agent_discovery_full.json"
TARGET_AGENTS = [
    "CodeFormatterAgent",
    "DocstringComplianceAgent",
    "InferenceTypeHintAgent",
    "NamingNormalizationAgent",
    "UnusedCleanupAgent",
    "DeadCodeDetectorAgent",
    "IntegrityGateExecutorAgent",
    "InputValidatorAgent",
    "ConvergenceDetectorAgent",
]


def get_agent_info(agent_name: str) -> dict[str, Any]:
    """Get agent info from discovery data."""
    with open(DISCOVERY_FILE, encoding="utf-8") as f:
        agents = json.load(f)
    for agent in agents:
        if agent["class_name"] == agent_name:
            return agent
    return None


def main():
    """Display target agents for refactoring."""
    print("=" * 70)
    print("BATCH REFACTORING TARGET: 10 AGENTS")
    print("=" * 70)
    for i, agent_name in enumerate(TARGET_AGENTS, 1):
        info = get_agent_info(agent_name)
        if info:
            print(f"\n{i}. {agent_name}")
            print(f"   Path: {info['path']}")
            print(
                f"   Typed: {info['typed_pct']:.0f}% | Doc: {info['documented_pct']:.0f}% | schema: {info['schema_strictness']:.0f}%",
            )
        else:
            print(f"\n{i}. {agent_name} - NOT FOUND")
    print("\n" + "=" * 70)
    print("Ready to refactor these 10 agents")
    print("=" * 70)


if __name__ == "__main__":
    main()
