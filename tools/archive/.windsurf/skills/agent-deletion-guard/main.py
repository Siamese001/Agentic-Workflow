#!/usr/bin/env python3
"""
Windsurf Skill: Agent Deletion Guard
Prevents unauthorized deletion of *Agent.py files.
"""

import subprocess
import sys
from pathlib import Path

# guardian: allow-silent-swallower -- Exception handling for authorization checks
# guardian: allow-magic-configuration -- Agent deletion validation patterns


def check_agent_deletion_authorization(file_path: str) -> tuple[bool, list[str]]:
    """Check if agent deletion is authorized."""
    issues = []

    # Check if file is an Agent file
    if not file_path.endswith("Agent.py"):
        return True, []  # Not an agent file, no restriction

    # Get the filename without path
    agent_name = Path(file_path).name

    # Check for AGENT-DELETION-AUTHORIZED marker in recent commits
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-10", "--grep=AGENT-DELETION-AUTHORIZED"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0 or not result.stdout.strip():
            issues.append("No AGENT-DELETION-AUTHORIZED marker found in recent commits")
        else:
            print("Found AGENT-DELETION-AUTHORIZED in commit history")
    except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
        issues.append(f"Failed to check authorization marker: {e}")

    # Check for justification in the same commit
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-5", "--grep=deletion.*justification"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0 or not result.stdout.strip():
            issues.append("No deletion justification found in commit message")
    except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
        issues.append(f"Failed to check justification: {e}")

    # Check for replacement specified
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-5", "--grep=replacement.*specified"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0 or not result.stdout.strip():
            issues.append("No replacement specification found in commit message")
    except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
        issues.append(f"Failed to check replacement specification: {e}")

    # Check for zero references (basic check - no imports)
    try:
        result = subprocess.run(
            ["git", "grep", "-r", agent_name.replace(".py", ""), "--include=*.py", "."],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0 and result.stdout.strip():
            # Count references, excluding the file itself
            references = [line for line in result.stdout.strip().split("\n") if file_path not in line]
            if len(references) > 0:
                issues.append(f"Found {len(references)} active references to {agent_name}")
    except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
        issues.append(f"Failed to check references: {e}")

    return len(issues) == 0, issues


def main():
    """Main entry point for the skill."""
    if len(sys.argv) != 2:
        print("Usage: python main.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    is_valid, issues = check_agent_deletion_authorization(file_path)

    if not is_valid:
        print("❌ Agent Deletion Guard Validation Failed:")
        for issue in issues:
            print(f"  - {issue}")
        print("\n🚫 Agent deletion requires:")
        print("   1. AGENT-DELETION-AUTHORIZED commit marker")
        print("   2. Clear justification in commit message")
        print("   3. Replacement specified")
        print("   4. Zero active references")
        print("   5. 90-day deprecation period")
        print("   See §5 - No Agent Deletion in .windsurfrules")
        sys.exit(1)
    else:
        print("[PASS] Agent deletion authorization validated")
        sys.exit(0)


if __name__ == "__main__":
    main()
