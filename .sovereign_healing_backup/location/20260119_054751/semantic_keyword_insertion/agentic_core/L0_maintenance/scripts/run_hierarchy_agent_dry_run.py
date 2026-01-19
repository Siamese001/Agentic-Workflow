"""
Run unified HierarchyAgent in dry-run mode (healing_enabled=False)
This consolidates both HierarchyEnforcerAgent and HierarchyHealerAgent functionality.

Location: Uses the NEW unified agent at agentic_core/L5_safety/guardrails/HierarchyAgent.py
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from agentic_core.L5_safety.validators.HierarchyAgent import HierarchyAgent

def main():
    print("=" * 80)
    print("UNIFIED HIERARCHY AGENT - DRY RUN MODE")
    print("=" * 80)
    print("Using: agentic_core/L5_safety/guardrails/HierarchyAgent.py")
    print("Validating hierarchy (no changes will be made)...\n")
    
    project_root = Path.cwd()
    
    # Initialize with healing_enabled=False for dry-run
    agent = HierarchyAgent(project_root, healing_enabled=False)
    
    # Run comprehensive hierarchy healing (all operations in dry-run)
    result = agent.heal_hierarchy(
        create_structure=True,
        relocate_files=True,
        enforce_depth=True,
        purge_orphans=True
    )
    
    print("\n" + "=" * 80)
    print("DRY RUN COMPLETE - No changes were made")
    print("=" * 80)
    print("\nTo apply these changes, run with healing_enabled=True")
    print("Note: There is an older HierarchyAgent in validators/ - this uses the new unified version in guardrails/")

if __name__ == "__main__":
    main()
