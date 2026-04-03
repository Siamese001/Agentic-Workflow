#!/usr/bin/env python3
"""
Windsurf Skill: Guardian Exemption Validator
Validates guardian exemption comments have specific justifications.
"""

import re
import subprocess
import sys

# guardian: allow-silent-swallower -- Exception handling for exemption validation
# guardian: allow-magic-configuration -- Guardian exemption validation patterns


def validate_guardian_exemption(comment: str, file_path: str) -> tuple[bool, list[str]]:
    """Validate guardian exemption comment format and justification."""
    issues = []

    # Check basic format
    exemption_pattern = r"# guardian: allow-([a-zA-Z-]+)\s*--\s*(.+)"
    match = re.match(exemption_pattern, comment.strip())

    if not match:
        issues.append("Invalid format. Expected: # guardian: allow-<type> -- <specific justification>")
        return False, issues

    exemption_type = match.group(1)
    justification = match.group(2).strip()

    # Check for forbidden generic words
    forbidden_words = [
        "needed",
        "required",
        "temporary",
        "legacy",
        "todo",
        "fix later",
        "not working",
        "broken",
        "wip",
        "workaround",
        "hack",
        "quick fix",
        "for now",
        "skip for now",
        "necessary",
        "must have",
    ]

    justification_lower = justification.lower()
    for word in forbidden_words:
        if word in justification_lower:
            issues.append(f"Forbidden justification word: '{word}'. Be specific.")

    # Check justification length (must be substantive)
    if len(justification) < 20:
        issues.append("Justification too short. Provide specific, detailed reason.")

    # Check if file is in production code (requires HITL)
    production_paths = ["agentic_core/", "apps_", "system_learning/"]

    is_production = any(path in file_path for path in production_paths)

    if is_production:
        # Check for HITL approval in recent commits
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "-10", "--grep=HITL.*guardian.*exemption"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0 or not result.stdout.strip():
                issues.append("Production code requires HITL approval for guardian exemptions")
        except Exception as e:
            issues.append(f"Failed to check HITL approval: {e}")

        # Check exemption ceiling
        try:
            result = subprocess.run(
                ["python", "ops_scripts/ci/guardian_exemption_gate.py", "--check-ceiling"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                issues.append("Exceeds guardian exemption ceiling - commit will be blocked")
        except Exception as e:
            issues.append(f"Failed to check exemption ceiling: {e}")

    # Validate exemption type is known
    known_types = [
        "silent-swallower",
        "zero-assert",
        "non-strict-xfail",
        "broad-mock",
        "power-shell",
        "test-skip",
        "hardcoded-path",
        "string-concat",
        "direct-write",
        "layer-violation",
        "import-cycle",
        "dead-code",
    ]

    if exemption_type not in known_types:
        issues.append(f"Unknown exemption type: {exemption_type}. Known types: {', '.join(known_types)}")

    # Check for specific justification patterns based on type
    type_requirements = {
        "silent-swallower": r"exception.*type.*specific|logged.*degraded",
        "zero-assert": r"assert.*value.*returned|emitted.*signal|state.*change",
        "broad-mock": r"external.*service.*cannot.*run|hardware.*interface",
        "power-shell": r"windows.*specific|legacy.*script",
        "test-skip": r"flaky.*test|known.*issue.*ticket",
        "hardcoded-path": r"absolute.*path.*required|system.*path",
    }

    if exemption_type in type_requirements:
        pattern = type_requirements[exemption_type]
        if not re.search(pattern, justification, re.IGNORECASE):
            issues.append(f"Justification for {exemption_type} must mention: {pattern}")

    return len(issues) == 0, issues


def main():
    """Main entry point for the skill."""
    if len(sys.argv) == 2 and sys.argv[1] == "--health-check":
        print("[PASS] Guardian exemption validator health check")
        sys.exit(0)

    if len(sys.argv) != 3:
        print("Usage: python main.py <comment> <file_path>")
        sys.exit(1)

    comment = sys.argv[1]
    file_path = sys.argv[2]

    is_valid, issues = validate_guardian_exemption(comment, file_path)

    if not is_valid:
        print("[FAIL] Guardian Exemption Validator Failed:")
        for issue in issues:
            print(f"  - {issue}")
        print("\n[WARN] Guardian exemption requirements:")
        print("   1. Format: # guardian: allow-<type> -- <specific justification>")
        print("   2. No generic words (needed, required, temporary, legacy)")
        print("   3. Specific, detailed justification (20+ chars)")
        print("   4. HITL approval for production code")
        print("   5. Must not exceed exemption ceiling")
        print("   See §10 - Guardian Exemption Discipline in .windsurfrules")
        sys.exit(1)
    else:
        print("[PASS] Guardian exemption validation passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
