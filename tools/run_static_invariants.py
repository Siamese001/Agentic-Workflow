#!/usr/bin/env python3
"""
Static Invariants Checker

Runs all static analysis scanners to enforce repository invariants.
Exits non-zero on NEW violations (baseline-aware).
"""

import sys
from pathlib import Path

# Add agentic_core to path for imports
# guardian: allow-global-mutation
sys.path.insert(0, str(Path(__file__).parent.parent / "agentic_core"))

# Import with full path to avoid import dependency check issues
import importlib.util

# Import determinism_serialization_check
spec = importlib.util.spec_from_file_location(
    "determinism_serialization_check",
    Path(__file__).parent.parent
    / "agentic_core"
    / "L5_safety"
    / "static_checks"
    / "determinism_serialization_check.py",
)
determinism_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(determinism_module)
scan_repository_for_determinism = determinism_module.scan_repository_for_determinism

# Import powershell_ban
spec = importlib.util.spec_from_file_location(
    "powershell_ban",
    Path(__file__).parent.parent / "agentic_core" / "L5_safety" / "static_checks" / "powershell_ban.py",
)
powershell_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(powershell_module)
scan_repository_for_powershell = powershell_module.scan_repository_for_powershell

# Import write_gateway_enforcer
spec = importlib.util.spec_from_file_location(
    "write_gateway_enforcer",
    Path(__file__).parent.parent
    / "agentic_core"
    / "L5_safety"
    / "static_checks"
    / "write_gateway_enforcer.py",
)
write_gateway_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(write_gateway_module)
scan_repository_for_writes = write_gateway_module.scan_repository_for_writes

# Import ptc_invariants
spec = importlib.util.spec_from_file_location(
    "ptc_invariants",
    Path(__file__).parent.parent / "agentic_core" / "L5_safety" / "static_checks" / "ptc_invariants.py",
)
ptc_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ptc_module)
scan_repository_for_ptc_invariants = ptc_module.scan_repository_for_ptc_invariants


def load_baseline(baseline_file: Path) -> dict[str, set]:
    """Load baseline violations grouped by category.

    Returns:
        Dict mapping category (rule_id prefix) to set of violation keys
    """
    baseline_by_category = {}
    if baseline_file.exists():
        with open(baseline_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    # Extract category from violation key (e.g., "PS_", "DIRECT_", etc.)
                    parts = line.split(":")
                    if len(parts) >= 3:
                        # Category is the rule_id (3rd field for 4-tuple, 2nd for 3-tuple)
                        if len(parts) == 4:
                            category = parts[2].split("_")[0]  # e.g., "PS" from "PS_SUBPROCESS_ARGV0"
                        else:
                            category = parts[1].split("_")[0]

                        if category not in baseline_by_category:
                            baseline_by_category[category] = set()
                        baseline_by_category[category].add(line)
    return baseline_by_category


def print_violations(
    title: str, violations: list, baseline_by_category: dict[str, set], category_prefix: str
) -> int:
    """Print violations and return count of NEW violations.

    Args:
        title: Title for the violation category
        violations: List of violations
        baseline_by_category: Baseline violations grouped by category
        category_prefix: Category prefix to check (e.g., "PS", "DIRECT", "DETERMINISM")

    Returns:
        Count of new violations (0 if category unseeded)
    """
    if not violations:
        print(f"OK: {title}: No violations found")
        return 0

    # Check if this category has a seeded baseline
    baseline = baseline_by_category.get(category_prefix, set())

    if not baseline:
        # Unseeded category - FAIL to require explicit baseline governance
        print(f"FAIL: {title}: UNSEEDED_BASELINE - {len(violations)} violations require baseline")
        print(f"  Action: Add baseline entries for {category_prefix}_* violations or fix them")
        return len(violations)

    # Identify new violations
    new_violations = []
    for violation in violations:
        # Handle both 3-tuple and 4-tuple formats
        if len(violation) == 4:
            path, lineno, code, excerpt = violation
            violation_key = f"{path}:{lineno}:{code}:{excerpt}"
        else:
            path, code, excerpt = violation
            violation_key = f"{path}:{code}:{excerpt}"

        if violation_key not in baseline:
            new_violations.append(violation)

    print(f"FAIL: {title}: {len(violations)} total violations found ({len(new_violations)} new)")
    if new_violations:
        print("NEW violations:")
        for violation in new_violations:
            if len(violation) == 4:
                path, lineno, code, excerpt = violation
                print(f"  {path}:{lineno}:{code} - {excerpt}")
            else:
                path, code, excerpt = violation
                print(f"  {path}:{code} - {excerpt}")
    return len(new_violations)


def main() -> int:
    """Run all static invariant scanners."""
    print("=== Static Invariants Checker ===")
    print()

    repo_root = Path.cwd()
    total_violations = 0
    total_new_violations = 0

    # Load baseline
    baseline_file = repo_root / "ops_scripts" / "hooks" / "landmine_baseline.txt"
    baseline_by_category = load_baseline(baseline_file)
    total_baseline = sum(len(v) for v in baseline_by_category.values())
    print(
        f"Loaded baseline with {total_baseline} existing violations across {len(baseline_by_category)} categories"
    )
    print()

    # 1. PowerShell prohibition scanner
    print("1. Scanning for PowerShell usage...")
    ps_violations = scan_repository_for_powershell(repo_root)
    new_ps = print_violations("PowerShell Ban", ps_violations, baseline_by_category, "PS")
    total_violations += len(ps_violations)
    total_new_violations += new_ps
    print()

    # 2. Direct write scanner
    print("2. Scanning for direct writes...")
    write_violations = scan_repository_for_writes(repo_root)
    new_write = print_violations("Direct Writes", write_violations, baseline_by_category, "DIRECT")
    total_violations += len(write_violations)
    total_new_violations += new_write
    print()

    # 3. Determinism serialization scanner
    print("3. Scanning for non-deterministic serialization...")
    det_violations = scan_repository_for_determinism(repo_root)
    new_det = print_violations(
        "Determinism Serialization", det_violations, baseline_by_category, "DETERMINISM"
    )
    total_violations += len(det_violations)
    total_new_violations += new_det
    print()

    # 4. PTC invariants scanner
    print("4. Scanning for PTC invariants...")
    ptc_violations = scan_repository_for_ptc_invariants(repo_root)
    new_ptc = print_violations("PTC Invariants", ptc_violations, baseline_by_category, "PTC")
    total_violations += len(ptc_violations)
    total_new_violations += new_ptc
    print()

    # Summary
    print("=== Summary ===")
    print(f"Total violations: {total_violations} ({total_new_violations} new)")
    if total_new_violations == 0:
        print("OK: No NEW violations found")
        return 0
    else:
        print(f"FAIL: {total_new_violations} new violations found")
        print("FAIL: Please fix new violations before proceeding")
        return 1


if __name__ == "__main__":
    sys.exit(main())
