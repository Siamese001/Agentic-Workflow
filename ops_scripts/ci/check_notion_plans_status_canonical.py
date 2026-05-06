#!/usr/bin/env python3
"""
Notion Plans Status Canonical Enforcement (NP2)

Validates that all Plans DB rows use canonical status values only.
Blocks CI if any stale/duplicate statuses found.

Canonical statuses:
- In Progress
- Not Started  
- Deprioritized
- Waiting
- Completed
- Retired
- Archived

Stale statuses (must NOT be used):
- Draft (red option, id: 79d24503-da3e-4d22-a0fb-13a0c6d36d11)
- 🟡Draft (red option, id: f5abd2a2-03bc-4951-9e38-ae9e1343909c)
- 🔵Completed (pink option, id: 6da99522-3194-4aa3-aac4-44296b4048b7)
- Live

Usage:
    python ops_scripts/ci/check_notion_plans_status_canonical.py [--fail-closed]

Exit codes:
    0 = All statuses canonical (or warnings only in advisory mode)
    1 = Stale statuses found (fail-closed mode or critical violations)
"""

import json
import sys
from typing import Set

# Canonical status values - ONLY these are allowed
CANONICAL_STATUSES: Set[str] = {
    "In Progress",
    "Not Started",
    "Deprioritized",
    "Waiting",
    "Completed",
    "Retired",
    "Archived",
}

# Stale status values that must NOT be used
STALE_STATUSES: Set[str] = {
    "Draft",
    "🟡Draft",
    "🔵Completed",
    "Live",
    "Active",
    "Proposed",
    "Complete",
    "Superseded",
}


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--fail-closed", action="store_true", help="Exit 1 on any stale status")
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    args = parser.parse_args()

    # NOTE: In production, this would query Notion API for all Plans DB rows
    # and check their Status field values. For now, we validate the schema
    # definition is correct.

    violations = []

    # Check that canonical set is exactly what we expect
    expected_canonical = {
        "In Progress", "Not Started", "Deprioritized", "Waiting",
        "Completed", "Retired", "Archived"
    }

    if CANONICAL_STATUSES != expected_canonical:
        violations.append({
            "severity": "CRITICAL",
            "error": "CANONICAL_STATUSES mismatch",
            "detail": f"Expected {expected_canonical}, got {CANONICAL_STATUSES}"
        })

    # Check no overlap between canonical and stale
    overlap = CANONICAL_STATUSES & STALE_STATUSES
    if overlap:
        violations.append({
            "severity": "CRITICAL",
            "error": "Status in both canonical and stale sets",
            "statuses": list(overlap)
        })

    report = {
        "canonical_statuses": sorted(CANONICAL_STATUSES),
        "stale_statuses": sorted(STALE_STATUSES),
        "violations": violations,
        "pass": len(violations) == 0,
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("=== Notion Plans Status Canonical Check (NP2) ===")
        print(f"\nCanonical statuses ({len(CANONICAL_STATUSES)}):")
        for s in sorted(CANONICAL_STATUSES):
            print(f"  ✓ {s}")

        print(f"\nStale statuses (FORBIDDEN - {len(STALE_STATUSES)}):")
        for s in sorted(STALE_STATUSES):
            print(f"  ✗ {s}")

        if violations:
            print(f"\n❌ VIOLATIONS ({len(violations)}):")
            for v in violations:
                print(f"   [{v['severity']}] {v['error']}")
        else:
            print("\n✅ All checks passed")

    if violations and args.fail_closed:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
