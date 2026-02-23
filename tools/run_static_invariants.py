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


def load_baseline(baseline_file: Path) -> set:
    """Load baseline violations into a set for comparison."""
    baseline = set()
    if baseline_file.exists():
        with open(baseline_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    # Format: path:code:excerpt
                    baseline.add(line)
    return baseline


def print_violations(title: str, violations: list, baseline: set) -> int:
    """Print violations and return count of NEW violations."""
    if not violations:
        print(f"OK: {title}: No violations found")
        return 0

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
    baseline = load_baseline(baseline_file)
    print(f"Loaded baseline with {len(baseline)} existing violations")
    print()

    # 1. PowerShell prohibition scanner
    print("1. Scanning for PowerShell usage...")
    ps_violations = scan_repository_for_powershell(repo_root)
    new_ps = print_violations("PowerShell Ban", ps_violations, baseline)
    total_violations += len(ps_violations)
    total_new_violations += new_ps
    print()

    # 2. Direct write scanner
    print("2. Scanning for direct writes...")
    write_violations = scan_repository_for_writes(repo_root)
    new_write = print_violations("Direct Writes", write_violations, baseline)
    total_violations += len(write_violations)
    total_new_violations += new_write
    print()

    # 3. Determinism serialization scanner
    print("3. Scanning for non-deterministic serialization...")
    det_violations = scan_repository_for_determinism(repo_root)
    new_det = print_violations("Determinism Serialization", det_violations, baseline)
    total_violations += len(det_violations)
    total_new_violations += new_det
    print()

    # 4. PTC invariants scanner
    print("4. Scanning for PTC invariants...")
    ptc_violations = scan_repository_for_ptc_invariants(repo_root)
    new_ptc = print_violations("PTC Invariants", ptc_violations, baseline)
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
