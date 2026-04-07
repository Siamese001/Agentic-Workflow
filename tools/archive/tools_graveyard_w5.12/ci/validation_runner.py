#!/usr/bin/env python3
"""
Standalone validation runner for test suite enforcement.
"""

import sys
from pathlib import Path

# Add the tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

try:
    from wave6a_validation_enforcer import ValidationEnforcer

    def main():
        """Run validation enforcement."""
        enforcer = ValidationEnforcer()
        report = enforcer.generate_enforcement_report()

        # Exit with error code if critical issues found
        if report['summary']['issues_by_severity'].get('critical', 0) > 0:
            print("CRITICAL: Critical validation issues found!")
            sys.exit(1)
        elif report['summary']['compliance_score'] < 80:
            print("WARNING: Low compliance score!")
            sys.exit(2)
        else:
            print("SUCCESS: Validation passed!")
            sys.exit(0)

    if __name__ == '__main__':
        main()

except ImportError as e:
    print(f"ERROR: Import error: {e}")
    sys.exit(1)
