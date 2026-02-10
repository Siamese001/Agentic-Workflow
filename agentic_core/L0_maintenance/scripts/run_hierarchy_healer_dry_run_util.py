"""
Run HierarchyHealerAgent in dry-run mode (healing_enabled=False)
This will scan for hierarchy violations without making any changes.
"""

# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, guardrail, memory, orchestrator, prompt, state, workflow
# This boosts alignment detection — review and integrate appropriately

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parents[1]
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))

from agentic_core.L5_safety.reasoning.HierarchyAgent import HierarchyAgent as HierarchyHealerAgent


def main():
    print("=" * 80)
    print("HIERARCHY HEALER - DRY RUN MODE")
    print("=" * 80)
    print("Scanning for hierarchy violations (no changes will be made)...\n")

    # Initialize with healing_enabled=False for dry-run
    project_root = Path.cwd()
    agent = HierarchyHealerAgent(project_root, healing_enabled=False)

    # Run hierarchy violation detection
    result = agent.heal_hierarchy_violations()

    print("\n" + "=" * 80)
    print("DRY RUN RESULTS")
    print("=" * 80)
    print(f"Files that would be relocated: {result['files_relocated']}")
    print(f"Folders that would be removed: {result['folders_removed']}")
    print(f"Errors encountered: {len(result['errors'])}")

    if result["errors"]:
        print("\nErrors:")
        for error in result["errors"]:
            print(f"  - {error}")

    print("\n" + "=" * 80)
    print("DRY RUN COMPLETE - No changes were made")
    print("=" * 80)


if __name__ == "__main__":
    main()
