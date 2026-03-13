"""
Run unified HierarchyAgent in dry-run mode (healing_enabled=False)
This consolidates both HierarchyEnforcerAgent and HierarchyHealerAgent functionality.

Location: Uses the NEW unified agent at agentic_core/L5_safety/enforcement/HierarchyAgent.py
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))
from agentic_core.L0_routing.utils.subprocess_runner_util import invoke_hierarchy_agent


def main():
    print("=" * 80)
    print("UNIFIED HIERARCHY AGENT - DRY RUN MODE")
    print("=" * 80)
    print("Using: agentic_core/L5_safety/enforcement/HierarchyAgent.py")
    print("Validating hierarchy (no changes will be made)...\n")
    project_root = Path.cwd()
    result = invoke_hierarchy_agent(action="dry_run", project_root=project_root)
    if result.get("success"):
        print(f"\n{result.get('message', 'Dry run complete')}")
    else:
        print(f"\n❌ Error: {result.get('error')}")
    print("\n" + "=" * 80)
    print("DRY RUN COMPLETE - No changes were made")
    print("=" * 80)
    print("\nTo apply these changes, run with healing_enabled=True")
    print(
        "Note: There is an older HierarchyAgent in validators/ - this uses the new unified version in guardrails/"
    )


if __name__ == "__main__":
    main()
