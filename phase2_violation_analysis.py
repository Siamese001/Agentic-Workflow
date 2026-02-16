#!/usr/bin/env python3
"""
Phase 2 violation analysis script
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileClassificationAgent


def analyze_violations():
    """Analyze violations across all app domains"""
    domains = ["apps_shared", "apps_lic", "apps_rg"]
    violations = {}

    print("=== PHASE 2 VIOLATION ANALYSIS ===\n")

    for domain in domains:
        print(f"=== {domain.upper()} ===")
        agent = FileClassificationAgent(
            project_root=Path(".").resolve() / domain, dry_run=True, validate_only=True
        )
        result = agent.run()
        violations[domain] = result["stats"]["violations"]

        print(f"Violations: {violations[domain]}")
        print(f"Analyzed: {result['stats']['analyzed']}")
        print(f"Compliant: {result['stats']['compliant']}")
        print()

    # Summary
    print("=== SUMMARY ===")
    total_violations = 0
    for domain, vols in violations.items():
        domain_total = sum(vols.values())
        total_violations += domain_total
        print(f"{domain}: {domain_total} violations")

    print(f"\nTotal violations across all domains: {total_violations}")

    return violations


if __name__ == "__main__":
    analyze_violations()
