"""
Run HierarchyHealerAgent in dry-run mode (healing_enabled=False)
This will scan for hierarchy violations without making any changes.
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
# guardian: allow-global-mutation
sys.path.insert(0, str(project_root))
from agentic_core.L0_routing.utils.subprocess_runner_util import invoke_hierarchy_agent


def main():
    print("=" * 80)
    print("HIERARCHY HEALER - DRY RUN MODE")
    print("=" * 80)
    print("Scanning for hierarchy violations (no changes will be made)...\n")
    project_root = Path.cwd()
    result = invoke_hierarchy_agent(action="heal_violations", project_root=project_root)
    print("\n" + "=" * 80)
    print("DRY RUN RESULTS")
    print("=" * 80)
    if result.get("success"):
        print(f"Files that would be relocated: {result.get('files_relocated', 0)}")
        print(f"Folders that would be removed: {result.get('folders_removed', 0)}")
        errors = result.get("errors", [])
        print(f"Errors encountered: {len(errors)}")
        if errors:
            print("\nErrors:")
            for error in errors:
                print(f"  - {error}")
    else:
        print(f"❌ Error: {result.get('error')}")
    print("\n" + "=" * 80)
    print("DRY RUN COMPLETE - No changes were made")
    print("=" * 80)


if __name__ == "__main__":
    main()
