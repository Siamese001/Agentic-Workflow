#!/usr/bin/env python3
"""
Plan Location Compliance Guardrail

Enforces Constitutional Rule #0: ALL plans, reports, and markdown artifacts 
MUST be saved to `docs/reports/plans/` inside the repository.

Usage:
    python ops_scripts/ci/check_plan_location_compliance.py [--fix]
"""

import argparse
import json
import sys
from pathlib import Path

# Force UTF-8 encoding for Windows compatibility
import io

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Ensure project root is in path
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from agentic_core.L0_routing.config.path_constants import get_validated_project_root

PROJECT_ROOT = get_validated_project_root()


class PlanLocationComplianceChecker:
    """Enforces plan location compliance with Constitutional Rule #0."""
    
    def check_compliance(self):
        """Check for plan location violations."""
        violations = []
        
        # Check for .windsurf/plans directory
        windsurf_plans = PROJECT_ROOT / ".windsurf" / "plans"
        if windsurf_plans.exists():
            violations.append({
                "type": "windsurf_plans_exists",
                "directory": str(windsurf_plans),
                "message": ".windsurf/plans directory exists (violates Constitutional Rule #0)",
                "severity": "error"
            })
        
        # Ensure SSOT plans directory exists
        ssot_plans = PROJECT_ROOT / "docs" / "reports" / "plans"
        if not ssot_plans.exists():
            violations.append({
                "type": "missing_ssot_directory", 
                "directory": str(ssot_plans),
                "message": "SSOT plans directory is missing",
                "severity": "error"
            })
        
        return violations
    
    def print_report(self):
        """Print compliance report."""
        violations = self.check_compliance()
        
        if not violations:
            print("✅ Plan location compliance: No violations found")
            print(f"📁 SSOT plans directory: {PROJECT_ROOT / 'docs' / 'reports' / 'plans'}")
            return 0
        
        print(f"❌ Plan location violations found: {len(violations)}")
        for v in violations:
            print(f"   {v['message']}")
        
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Check plan location compliance")
    args = parser.parse_args()
    
    checker = PlanLocationComplianceChecker()
    return checker.print_report()


if __name__ == "__main__":
    sys.exit(main())
