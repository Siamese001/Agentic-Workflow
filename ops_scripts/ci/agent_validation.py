"""
CI/CD Agent Validation Script

Replaces removed pre-commit hooks with agent-based validation:
- CodeDeduplicationAgent for duplicate filename detection
- ArchitectureGovernorAgent for SSOT folder structure validation

Exit codes:
- 0: All validations passed
- 1: Validation failures detected
"""

import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def run_code_deduplication_check() -> tuple[bool, str]:
    """
    Run CodeDeduplicationAgent to detect duplicate filenames.

    Returns:
        Tuple of (success, message)
    """
    try:
        from agentic_core.L5_safety.validators import (
            CodeDeduplicationAgent,
        )

        print("\n" + "=" * 70)
        print("AGENT VALIDATION: Code Deduplication")
        print("=" * 70)

        agent = CodeDeduplicationAgent()

        # Scan for duplicates
        python_files = list(project_root.rglob("*.py"))
        python_files = [f for f in python_files if "__pycache__" not in str(f)]

        agent.scan_filename_duplicates(python_files, project_root)

        if agent.filename_duplicates:
            print(f"\n❌ Found {len(agent.filename_duplicates)} duplicate filename groups:")
            for basename, entries in agent.filename_duplicates.items():
                print(f"\n  Duplicate: {basename}")
                for path, hash_val in entries:
                    rel = path.relative_to(project_root)
                    print(f"    - {rel} (hash: {hash_val[:8]}...)")
            return False, f"Found {len(agent.filename_duplicates)} duplicate filename groups"

        print("\n✅ No duplicate filenames detected")
        return True, "Code deduplication check passed"

    except Exception as e:
        return False, f"Code deduplication check failed: {e}"


def run_architecture_governance_check() -> tuple[bool, str]:
    """
    Run ArchitectureGovernorAgent to validate SSOT folder structure.

    Returns:
        Tuple of (success, message)
    """
    try:
        from agentic_core.L5_safety.validators import (
            ArchitectureGovernorAgent,
        )

        print("\n" + "=" * 70)
        print("AGENT VALIDATION: Architecture Governance")
        print("=" * 70)

        agent = ArchitectureGovernorAgent(
            project_root=project_root,
            auto_approve=True,  # Headless CI mode
        )

        # Run validation (dry-run mode)
        is_compliant, results = agent.run_ci_verification_sync()

        violations_found = results.get("violations_found", 0)

        if not is_compliant:
            print(f"\n❌ Found {violations_found} architecture violations")
            print(f"   Roots scanned: {', '.join(results.get('roots_scanned', []))}")
            return False, f"Found {violations_found} architecture violations"

        print("\n✅ Architecture validation passed")
        print(f"   Roots scanned: {', '.join(results.get('roots_scanned', []))}")
        return True, "Architecture governance check passed"

    except Exception as e:
        return False, f"Architecture governance check failed: {e}"


def main() -> int:
    """
    Run all agent validations.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    print("\n" + "=" * 70)
    print("CI/CD AGENT VALIDATION SUITE")
    print("=" * 70)
    print("Replacing removed pre-commit hooks with agent-based validation")
    print("=" * 70)

    results = []

    # Run code deduplication check
    success, message = run_code_deduplication_check()
    results.append((success, "Code Deduplication", message))

    # Run architecture governance check
    success, message = run_architecture_governance_check()
    results.append((success, "Architecture Governance", message))

    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)

    all_passed = True
    for success, check_name, message in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {check_name}")
        if not success:
            print(f"       {message}")
            all_passed = False

    print("=" * 70)

    if all_passed:
        print("\n✅ All agent validations passed")
        return 0
    else:
        print("\n❌ Some agent validations failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
