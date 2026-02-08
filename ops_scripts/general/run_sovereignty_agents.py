#!/usr/bin/env python3
"""
Script to execute the integrated Sovereignty Guardians.
Runs RootHygieneAgent and PascalSovereigntyAgent to clean and enforce standards.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agentic_core.L5_safety.validators.PascalSovereigntyAgent import PascalSovereigntyAgent

from agentic_core.L5_safety.reasoning.RootHygieneAgent import RootHygieneAgent


def main():
    print("=" * 80)
    print("SOVEREIGNTY GUARDIANS EXECUTION")
    print("=" * 80)

    # Step 1: Root Hygiene
    print("\n[PHASE 1] Executing RootHygieneAgent...")
    hygiene_agent = RootHygieneAgent(project_root=project_root, dry_run=False)
    hygiene_result = hygiene_agent.run()

    print("\n=== ROOT HYGIENE RESULTS ===")
    print(f"Success: {hygiene_result['success']}")
    print(f"Stats: {hygiene_result['stats']}")
    print(f"Summary: {hygiene_result['summary']}")

    # Step 2: Pascal Sovereignty
    print("\n[PHASE 2] Executing PascalSovereigntyAgent...")
    pascal_agent = PascalSovereigntyAgent(project_root=project_root, dry_run=False)
    pascal_result = pascal_agent.run()

    print("\n=== PASCAL SOVEREIGNTY RESULTS ===")
    print(f"Success: {pascal_result['success']}")
    print(f"Stats: {pascal_result['stats']}")
    print(f"Summary: {pascal_result['summary']}")

    # Step 3: Validation Pass
    print("\n[PHASE 3] Running validation audit...")
    validator = PascalSovereigntyAgent(project_root=project_root, dry_run=True, validate_only=True)
    validator.run()

    total_violations = sum(validator.stats["violations"].values())
    print("\n=== VALIDATION AUDIT ===")
    print(f"Total Violations Remaining: {total_violations}")
    print(f"Compliant Files: {validator.stats['compliant']}")
    print(f"Analyzed Files: {validator.stats['analyzed']}")

    if total_violations == 0:
        print("\n✅ 100% COMPLIANT - All sovereignty standards enforced!")
        return 0
    else:
        print(f"\n⚠️  {total_violations} violations remain - manual review required")
        return 1


if __name__ == "__main__":
    sys.exit(main())
