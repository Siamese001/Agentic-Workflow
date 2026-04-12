#!/usr/bin/env python3
"""
Windsurf Skill: Repair Gate Validator
Validates all 5 repair gates pass before any file edit.
"""

import subprocess
import sys

# guardian: allow-silent-swallower -- Exception handling for gate validation
# guardian: allow-magic-configuration -- Gate configuration and validation logic


def check_repair_gates(file_path: str, edit_type: str) -> tuple[bool, list[str]]:
    """Check all 5 repair gates before allowing edit."""
    issues = []

    # Gate 1: Scope Gate
    try:
        result = subprocess.run(
            ["python", "-c", "from .windsurf.skills.scope_guard import main; main()"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            issues.append("Scope gate validation failed")
    except Exception as e:
        issues.append(f"Scope gate error: {e}")

    # Gate 2: Dependency Graph Gate
    try:
        result = subprocess.run(
            ["python", "tools/adg/adg_stale_guard.py"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            issues.append("ADG freshness gate failed")
    except Exception as e:
        issues.append(f"ADG freshness gate error: {e}")

    # Gate 3: Test Integrity Gate
    try:
        result = subprocess.run(
            ["python", "ops_scripts/ci/check_test_integrity.py"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            issues.append("Test integrity gate failed")
    except Exception as e:
        issues.append(f"Test integrity gate error: {e}")

    # Gate 4: Evidence Contract Gate
    try:
        result = subprocess.run(
            ["python", "ops_scripts/ci/check_evidence_contract_v2.py"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            issues.append("Evidence contract gate failed")
    except Exception as e:
        issues.append(f"Evidence contract gate error: {e}")

    # Gate 5: Rollback Checkpoint Gate
    try:
        result = subprocess.run(
            ["python", "ops_scripts/ci/check_rollback_checkpoints.py"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            issues.append("Rollback checkpoint gate failed")
    except Exception as e:
        issues.append(f"Rollback checkpoint gate error: {e}")

    return len(issues) == 0, issues


def main():
    """Main entry point for the skill."""
    if len(sys.argv) == 2 and sys.argv[1] == "--health-check":
        print("[PASS] Repair gate validator health check")
        sys.exit(0)

    if len(sys.argv) != 3:
        print("Usage: python main.py <file_path> <edit_type>")
        sys.exit(1)

    file_path = sys.argv[1]
    edit_type = sys.argv[2]

    is_valid, issues = check_repair_gates(file_path, edit_type)

    if not is_valid:
        print("❌ Repair Gate Validation Failed:")
        for issue in issues:
            print(f"  - {issue}")
        print("\n🚫 All 5 repair gates must pass before editing")
        print("   See §4 - No Editing While Exploring in .windsurfrules")
        sys.exit(1)
    else:
        print("✅ All 5 repair gates passed - edit allowed")
        sys.exit(0)


if __name__ == "__main__":
    main()
