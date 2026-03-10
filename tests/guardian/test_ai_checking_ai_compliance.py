#!/usr/bin/env python3
"""
Meta-Test: AI-Checking-AI Constitutional Compliance
Ensures no AI agents are validating other AI agents through heuristic analysis.
"""

from pathlib import Path

# Patterns that indicate AI-checking-AI violations
VIOLATION_PATTERNS = [
    # Runtime instantiation for validation
    "importlib.util.spec_from_file_location",
    "importlib.util.module_from_spec",
    "spec.loader.exec_module",
    # Dynamic class loading for validation
    "getattr(module,",
    "hasattr(instance,",
    # External AI service calls for validation
    "deepwiki_client",
    "ask_question",
    "verify_file_exists",
]

# Allowed exceptions (Guardian tests themselves + legitimate validator introspection)
ALLOWED_FILES = [
    "tests/guardian/",
    "test_ai_checking_ai_compliance.py",
    # Legitimate validator introspection for SSOT reconciliation
    "FilesystemSSOTReconcilerAgent.py",
    # Legitimate validator introspection for phase validation
    "Phase5Validator.py",
    "phase5_validator.py",
    # Legitimate external documentation lookup (not AI validation)
    "SovereignCanonAuditorAgent.py",
    # Legitimate test generation introspection
    "TestGeneratorAgent.py",
]


def check_file_for_violations(file_path: Path) -> list[str]:
    """
    Check a Python file for AI-checking-AI violation patterns.

    Returns:
        List of violation descriptions
    """
    violations = []

    # Skip allowed files
    if any(allowed in str(file_path) for allowed in ALLOWED_FILES):
        return []

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")

        # Check for violation patterns
        for pattern in VIOLATION_PATTERNS:
            if pattern in content:
                # Get line number
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    if pattern in line:
                        violations.append(f"Line {i}: Potential AI-checking-AI pattern: {pattern}")
                        break

    except (OSError, UnicodeDecodeError, SyntaxError) as e:
        violations.append(f"Error reading file: {e}")

    return violations


def scan_validators() -> tuple[int, int, list[tuple[Path, list[str]]]]:
    """
    Scan all L5 safety validators for AI-checking-AI violations.

    Returns:
        Tuple of (files_scanned, violations_found, violation_details)
    """
    validators_dir = Path("agentic_core/L5_safety/validators")

    if not validators_dir.exists():
        print(f"ERROR: Validators directory not found: {validators_dir}")
        return 0, 0, []

    files_scanned = 0
    violations_found = 0
    violation_details = []

    for file_path in validators_dir.glob("*.py"):
        if file_path.name.startswith("__"):
            continue

        files_scanned += 1
        violations = check_file_for_violations(file_path)

        if violations:
            violations_found += len(violations)
            violation_details.append((file_path, violations))

    return files_scanned, violations_found, violation_details


def test_ai_checking_ai_compliance() -> None:
    """
    Meta-test to ensure no AI-checking-AI patterns remain in the codebase.

    Raises:
        SystemExit: 1 if violations found, 0 if compliant
    """
    print("=" * 70)
    print("AI-CHECKING-AI CONSTITUTIONAL COMPLIANCE META-TEST")
    print("=" * 70)
    print()

    files_scanned, violations_found, violation_details = scan_validators()

    print(f"Files scanned: {files_scanned}")
    print(f"Violations found: {violations_found}")
    print()

    if violations_found > 0:
        print("VIOLATION: AI-checking-AI patterns detected:")
        print()
        for file_path, violations in violation_details:
            print(f"📄 {file_path}:")
            for violation in violations:
                print(f"  ❌ {violation}")
            print()

        print("=" * 70)
        print("❌ CONSTITUTIONAL COMPLIANCE: FAILED")
        print("=" * 70)
        raise AssertionError(f"Found {violations_found} AI-checking-AI violations")
    else:
        print("✅ No AI-checking-AI patterns detected")
        print()
        print("=" * 70)
        print("✅ CONSTITUTIONAL COMPLIANCE: PASSED")
        print("=" * 70)
        assert True  # no-exception contract


if __name__ == "__main__":
    test_ai_checking_ai_compliance()
