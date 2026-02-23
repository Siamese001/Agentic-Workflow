#!/usr/bin/env python3
"""
Static Invariants Checker

Runs all static analysis scanners to enforce repository invariants.
Exits non-zero on violations.
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


def print_violations(title: str, violations: list) -> int:
    """Print violations and return count."""
    if not violations:
        print(f"✓ {title}: No violations found")
        return 0

    print(f"✗ {title}: {len(violations)} violations found:")
    for file_path, lineno, rule_id, snippet in violations:
        print(f"  {file_path}:{lineno} - {rule_id} - {snippet}")

    return len(violations)


def main():
    """Run all static invariant scanners."""
    print("=== Static Invariants Checker ===")
    print()

    repo_root = Path.cwd()
    total_violations = 0

    # 1. PowerShell prohibition scanner
    print("1. Scanning for PowerShell usage...")
    ps_violations = scan_repository_for_powershell(repo_root)
    total_violations += print_violations("PowerShell Ban", ps_violations)
    print()

    # 2. Write gateway enforcement scanner
    print("2. Scanning for direct file writes...")
    write_violations = scan_repository_for_writes(repo_root)
    total_violations += print_violations("Write Gateway Enforcement", write_violations)
    print()

    # 3. Determinism serialization scanner
    print("3. Scanning for non-deterministic serialization...")
    det_violations = scan_repository_for_determinism(repo_root)
    total_violations += print_violations("Determinism Serialization", det_violations)
    print()

    # Summary
    print("=== Summary ===")
    if total_violations == 0:
        print("✓ All static invariants passed")
        print("✓ Repository is compliant with formal verification requirements")
        return 0
    else:
        print(f"✗ {total_violations} total violations found")
        print("✗ Please fix violations before proceeding")
        return 1


if __name__ == "__main__":
    sys.exit(main())
