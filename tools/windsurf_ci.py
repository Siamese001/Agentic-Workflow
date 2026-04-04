#!/usr/bin/env python3
"""
Windsurf Native CI for Plans
Runs CI validation directly in Windsurf using existing hooks and tools.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

from tools.ci_validate_plans import CIPlanValidator


def run_windsurf_ci():
    """Run CI validation directly in Windsurf."""

    print("=" * 80)
    print("WINDSURF NATIVE CI - PLAN VALIDATION")
    print("=" * 80)
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    print()

    # Initialize validator
    validator = CIPlanValidator()

    # Run validation
    results = validator.validate_all_plans()

    # Save report
    report_path = validator.save_report()

    # Load results for windsurf CI check
    ci_results = {
        "status": "passed" if results["invalid_plans"] == 0 else "failed",
        "summary": {
            "total": results["total_plans"],
            "valid": results["valid_plans"],
            "invalid": results["invalid_plans"],
            "warnings": results["plans_with_warnings"]
        },
        "report_path": str(report_path),
        "timestamp": results["timestamp"]
    }

    # Save CI results for other tools to consume
    ci_results_path = repo_root / "artifacts" / "ci" / "windsurf_ci_results.json"
    ci_results_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ci_results_path, 'w') as f:
        json.dump(ci_results, f, indent=2)

    # Display results
    print("\n" + "=" * 80)
    print("WINDSURF CI RESULTS:")
    print("=" * 80)
    print(f"Status: {'PASSED' if ci_results['status'] == 'passed' else 'FAILED'}")
    print(f"Plans: {ci_results['summary']['valid']}/{ci_results['summary']['total']} valid")

    if ci_results['summary']['invalid'] > 0:
        print(f"{ci_results['summary']['invalid']} plan(s) INVALID")
        print("\nTop Issues:")
        for failure in results["failures"][:5]:
            print(f"  - {failure['plan']}: {failure['issues'][0]}")

    if ci_results['summary']['warnings'] > 0:
        print(f"{ci_results['summary']['warnings']} plan(s) have warnings")

    print(f"\nReport: {report_path}")
    print("=" * 80)

    return ci_results['status'] == 'passed'

def check_windsurfrules_compliance():
    """Check compliance with windsurfrules."""

    print("\nCHECKING WINDSURFRULES COMPLIANCE")
    print("-" * 40)

    rules_dir = repo_root / ".windsurf" / "rules"
    if not rules_dir.exists():
        print("No .windsurf/rules directory found")
        return True

    # Check for plan-specific rules
    plan_rules = []
    for rule_file in rules_dir.rglob("*.md"):
        content = rule_file.read_text(errors='ignore')
        if 'plan' in content.lower():
            plan_rules.append(rule_file)

    if plan_rules:
        print(f"Found {len(plan_rules)} plan-related rules:")
        for rule in plan_rules[:3]:
            print(f"  - {rule.relative_to(repo_root)}")

    # Check if plan validation is enforced
    precommit_path = repo_root / ".pre-commit-config.yaml"
    if precommit_path.exists():
        content = precommit_path.read_text()
        if "validate-plan-format" in content:
            print("Plan validation enforced in pre-commit hooks")
        else:
            print("Plan validation not in pre-commit hooks")

    return True

if __name__ == "__main__":
    # Run Windsurf CI
    ci_passed = run_windsurf_ci()

    # Check windsurfrules compliance
    rules_compliant = check_windsurfrules_compliance()

    # Final status
    if ci_passed and rules_compliant:
        print("\nWINDSURF CI PASSED")
        sys.exit(0)
    else:
        print("\nWINDSURF CI FAILED")
        sys.exit(1)
