"""C0 Policy Required Gate (Hard Cutoff Enforcement)

W1 c0-policy-rectification-phase2-deferred-a3f7e2:
    CI gate enforcing that RouteContract instances have c0_policy field
    after the hard cutoff date. Fails builds if contracts lack C0 policy.

Usage:
    python ops_scripts/ci/check_c0_policy_required.py \
        --contract-path contracts/ \
        --cutoff-date 2026-08-08

DS-5: Hard cutoff option for C0 policy rectification.
Environment:
    C0_POLICY_REQUIRED_CUTOFF: ISO date for hard cutoff (default: 2026-08-08)
    C0_POLICY_STRICT_MODE: If 0, warn only; if 1, fail (default: 1)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


# Hard cutoff date: 90 days after Phase 2 start (2026-05-08)
DEFAULT_CUTOFF = "2026-08-08"


def check_contract_has_c0_policy(contract: dict[str, Any]) -> tuple[bool, str]:
    """Check if a RouteContract has c0_policy field.

    Returns:
        (passed, reason) tuple
    """
    route_id = contract.get("route_id", "UNKNOWN")

    if "c0_policy" not in contract:
        return False, f"{route_id}: Missing c0_policy field entirely"

    c0_policy = contract.get("c0_policy")
    if c0_policy is None:
        return False, f"{route_id}: c0_policy is None (lazy migration fallback)"

    # Validate required sub-fields
    if isinstance(c0_policy, dict):
        if "c0_mode" not in c0_policy:
            return False, f"{route_id}: c0_policy missing c0_mode"
        if "evidence_contract_required" not in c0_policy:
            return False, f"{route_id}: c0_policy missing evidence_contract_required"

    return True, ""


def scan_contracts(contract_path: str) -> list[tuple[bool, str, Path]]:
    """Scan all contracts in path for C0 policy compliance.

    Returns:
        List of (passed, reason, file_path) tuples
    """
    results = []
    base_path = Path(contract_path)

    if not base_path.exists():
        return [(False, f"Path not found: {contract_path}", base_path)]

    # Find all JSON contract files
    contract_files = list(base_path.rglob("*.json"))

    for contract_file in contract_files:
        try:
            with open(contract_file, "r", encoding="utf-8") as f:
                contract = json.load(f)

            # Handle both single contracts and arrays
            contracts = contract if isinstance(contract, list) else [contract]

            for c in contracts:
                # Only check RouteContract-like objects
                if "route_id" not in c:
                    continue

                passed, reason = check_contract_has_c0_policy(c)
                results.append((passed, reason, contract_file))

        except json.JSONDecodeError as e:
            results.append((False, f"JSON parse error: {e}", contract_file))
        except Exception as e:
            results.append((False, f"Error reading file: {e}", contract_file))

    return results


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for C0 policy required gate."""
    parser = argparse.ArgumentParser(
        description="C0 Policy Required Gate (Hard Cutoff Enforcement)"
    )
    parser.add_argument(
        "--contract-path",
        default="contracts/",
        help="Path to contract files (JSON)",
    )
    parser.add_argument(
        "--cutoff-date",
        default=os.environ.get("C0_POLICY_REQUIRED_CUTOFF", DEFAULT_CUTOFF),
        help="ISO date for hard cutoff (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--strict",
        type=int,
        default=int(os.environ.get("C0_POLICY_STRICT_MODE", "1")),
        help="1=fail on violation, 0=warn only",
    )
    parser.add_argument(
        "--output-report",
        help="Path to write violation report JSON",
    )

    args = parser.parse_args(argv)

    # Check if cutoff date has passed
    today = datetime.utcnow().date()
    cutoff = datetime.fromisoformat(args.cutoff_date).date()

    if today < cutoff:
        print(f"C0 Policy Gate: CUTOFF NOT YET REACHED ({args.cutoff_date})")
        print(f"  Today: {today}")
        print(f"  Cutoff: {cutoff}")
        print(f"  Days remaining: {(cutoff - today).days}")
        print("  Skipping enforcement (grace period)")
        return 0

    print(f"C0 Policy Gate: ENFORCING (cutoff {args.cutoff_date} reached)")
    print(f"  Scanning: {args.contract_path}")
    print()

    results = scan_contracts(args.contract_path)

    failures = [(reason, path) for passed, reason, path in results if not passed]
    passed_count = len([r for r in results if r[0]])

    print(f"Results: {passed_count} passed, {len(failures)} failed")

    if failures:
        print("\nFailures:")
        for reason, path in failures:
            print(f"  - {path}: {reason}")

    if args.output_report:
        report = {
            "cutoff_date": args.cutoff_date,
            "enforced": True,
            "total_checked": len(results),
            "passed": passed_count,
            "failed": len(failures),
            "violations": [
                {"file": str(path), "reason": reason} for reason, path in failures
            ],
            "checked_at": datetime.utcnow().isoformat(),
        }
        with open(args.output_report, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\nReport written to: {args.output_report}")

    if failures and args.strict:
        print("\nFAILED: C0 policy required gate")
        return 1

    if failures and not args.strict:
        print("\nWARNED: C0 policy violations found (strict mode off)")
        return 0

    print("\nPASSED: All contracts have C0 policy")
    return 0


if __name__ == "__main__":
    sys.exit(main())
