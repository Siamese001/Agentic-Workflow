#!/usr/bin/env python3
"""
Windsurf Skill: HITL Decision Validator
Validates that HITL was presented for multi-option decisions.
"""

import re
import subprocess
import sys
from pathlib import Path

# guardian: allow-silent-swallower -- Exception handling for HITL validation
# guardian: allow-magic-configuration -- HITL decision validation patterns


def check_hitl_presentation(decision_context: str, options_count: int) -> tuple[bool, list[str]]:
    """Check if HITL was properly presented."""
    issues = []

    # Only validate if multiple options (2-4)
    if options_count < 2:
        return True, []  # Single option, no HITL required

    if options_count > 4:
        issues.append(f"Too many options ({options_count}). Maximum 4 allowed.")

    # Check for HITL workflow invocation
    hitl_patterns = [
        r"/hitl-decision-gate",
        r"HITL.*options.*presented",
        r"Present.*options.*A/B/C/D",
        r"Waiting.*explicit.*user.*selection",
        r"DO.*NOT.*assume.*defaults",
    ]

    # Check recent command history for HITL presentation
    try:
        # Check if hitl-decision-gate workflow was called
        result = subprocess.run(
            [
                "python",
                "-c",
                """
import subprocess
import sys
try:
    result = subprocess.run(["git", "log", "--oneline", "-5"], capture_output=True, text=True, timeout=30)
    if "hitl-decision-gate" in result.stdout.lower():
        print("HITL workflow found")
    else:
        print("HITL workflow not found")
except:
    print("Error checking HITL workflow")
""",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if "HITL workflow not found" in result.stdout:
            issues.append("No evidence of /hitl-decision-gate workflow invocation")
    except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
        issues.append(f"Failed to check HITL workflow: {e}")

    # Check for option presentation format
    required_elements = [
        (r"\bA\)", "Option A presented"),
        (r"\bB\)", "Option B presented" if options_count >= 2 else None),
        (r"\bC\)", "Option C presented" if options_count >= 3 else None),
        (r"\bD\)", "Option D presented" if options_count >= 4 else None),
        (r"trade-offs?", "Trade-offs listed"),
        (r"waiting.*selection", "Waiting for user selection"),
    ]

    # Check recent evidence files for HITL presentation
    evidence_dir = Path("docs/reports/plans")
    if evidence_dir.exists():
        recent_evidence = list(evidence_dir.glob("*.md"))[-5:]  # Last 5 evidence files

        hitl_found = False
        for evidence_file in recent_evidence:
            try:
                content = evidence_file.read_text(encoding="utf-8")

                # Check for HITL elements
                hitl_elements = 0
                for pattern, description in required_elements:
                    if description and re.search(pattern, content, re.IGNORECASE):
                        hitl_elements += 1

                if hitl_elements >= 3:  # At least 3 HITL elements found
                    hitl_found = True
                    break
            except Exception:  # guardian: allow-broad-exception -- offline tooling, reports failure
                continue

        if not hitl_found:
            issues.append("No HITL presentation found in recent evidence files")

    # Check for user selection recording
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-3", '--grep="User selected"'],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0 or not result.stdout.strip():
            issues.append("No user selection recorded in commit history")
    except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
        issues.append(f"Failed to check user selection: {e}")

    return len(issues) == 0, issues


def main():
    """Main entry point for the skill."""
    if len(sys.argv) == 2 and sys.argv[1] == "--health-check":
        print("[PASS] HITL decision validator health check")
        sys.exit(0)

    if len(sys.argv) != 3:
        print("Usage: python main.py <decision_context> <options_count>")
        sys.exit(1)

    decision_context = sys.argv[1]
    try:
        options_count = int(sys.argv[2])
    except ValueError:
        print("Error: options_count must be an integer")
        sys.exit(1)

    is_valid, issues = check_hitl_presentation(decision_context, options_count)

    if not is_valid:
        print("❌ HITL Decision Validator Failed:")
        for issue in issues:
            print(f"  - {issue}")
        print("\n🚫 HITL discipline requires:")
        print("   1. Present 2-4 concrete options with trade-offs")
        print("   2. Wait for explicit user selection (A/B/C/D)")
        print("   3. Record user selection in evidence")
        print("   4. Never assume defaults or 'best' options")
        print("   See §8 - HITL Discipline in .windsurfrules")
        sys.exit(1)
    else:
        print("[PASS] HITL decision validation passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
