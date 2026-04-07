#!/usr/bin/env python3
"""
Guard against unauthorized agent deletion.

Blocks deletion of any *Agent.py file unless:
1. Explicit AGENT-DELETION-AUTHORIZED marker in commit message
2. Justification provided (min 50 chars)
3. Replacement agent specified
4. Reference scan shows zero references (or REFERENCES-MIGRATED: yes)
5. Deprecation period met (90 days minimum) OR marked as unused

Constitutional Authority: Prevents catastrophic data loss from premature agent deletion
"""

from __future__ import annotations

import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

MIN_DEPRECATION_DAYS = 90
MIN_JUSTIFICATION_LENGTH = 50


def check_agent_deletions() -> bool:
    """Check if any agents are being deleted and validate authorization."""

    # Get deleted files in this commit
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-status"],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        return True  # Can't check, allow (fail-open for git issues)

    deleted_agents = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t", 1)
        if len(parts) != 2:
            continue
        status, filepath = parts
        if status == "D" and filepath.endswith("Agent.py"):
            deleted_agents.append(filepath)

    if not deleted_agents:
        return True  # No agents deleted, allow

    # HITL: Show user what agents are being deleted and get confirmation
    print()
    print("=" * 80)
    print("⚠️  AGENT DELETION DETECTED - HUMAN CONFIRMATION REQUIRED")
    print("=" * 80)
    print()
    print("The following agents are being deleted in this commit:")
    print()
    for agent in deleted_agents:
        agent_name = Path(agent).stem
        print(f"  🗑️  {agent}")

        # Show reference count
        ref_count = count_references(agent_name)
        if ref_count > 0:
            print(f"      ⚠️  WARNING: {ref_count} references found in codebase!")
        else:
            print("      ✅ No active references found")

    print()
    print("Agent deletion is a DESTRUCTIVE operation that can break production systems.")
    print()

    # Get user confirmation
    try:
        response = input("Do you want to proceed with this deletion? (yes/no): ").strip().lower()
        if response not in ["yes", "y"]:
            print()
            print("❌ Agent deletion cancelled by user")
            print()
            return False
    except (EOFError, KeyboardInterrupt):    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling    # guardian: Multiple exceptions (EOFError, KeyboardInterrupt) need specific handling
        print()
        print("❌ Agent deletion cancelled")
        print()
        return False

    print()
    print("✅ User confirmed deletion - checking authorization...")
    print()

    # Read commit message
    commit_msg_file = Path(".git/COMMIT_EDITMSG")
    if not commit_msg_file.exists():
        return True  # No commit message yet, allow (pre-commit will catch it)

    commit_msg = commit_msg_file.read_text(encoding="utf-8")

    # Check for authorization marker
    pattern = r"AGENT-DELETION-AUTHORIZED:\s*(.+)"
    match = re.search(pattern, commit_msg, re.MULTILINE)

    if not match:
        print("❌ CRITICAL: Agent deletion detected without authorization")
        print()
        print("   Deleted agents:")
        for agent in deleted_agents:
            print(f"   - {agent}")
        print()
        print("   You must include in your commit message:")
        print("   AGENT-DELETION-AUTHORIZED: <justification>")
        print("   REPLACEMENT: <replacement agent or 'none' or 'unused'>")
        print("   DEPRECATION-DATE: <YYYY-MM-DD or 'N/A'>")
        print("   REFERENCES-MIGRATED: <yes/no>")
        print()
        print("   Example:")
        print("   refactor: Remove deprecated LocationAgent shim")
        print()
        print("   AGENT-DELETION-AUTHORIZED: Shim fully migrated after 90-day deprecation period.")
        print("   All 80 references redirected to LocationHealerAgent and LocationValidatorAgent.")
        print("   REPLACEMENT: LocationHealerAgent + LocationValidatorAgent")
        print("   DEPRECATION-DATE: 2026-02-07")
        print("   REFERENCES-MIGRATED: yes")
        print()
        return False

    justification = match.group(1).strip()
    if len(justification) < MIN_JUSTIFICATION_LENGTH:
        print(f"❌ Justification too short (min {MIN_JUSTIFICATION_LENGTH} chars)")
        print(f"   Got ({len(justification)} chars): {justification}")
        return False

    # Check for required metadata
    if "REPLACEMENT:" not in commit_msg:
        print("❌ Missing REPLACEMENT: field")
        print("   Specify replacement agent or 'none' if truly unused")
        return False

    if "DEPRECATION-DATE:" not in commit_msg:
        print("❌ Missing DEPRECATION-DATE: field")
        print("   Specify date agent was deprecated or 'N/A' if never used")
        return False

    if "REFERENCES-MIGRATED:" not in commit_msg:
        print("❌ Missing REFERENCES-MIGRATED: field")
        print("   Specify 'yes' if all references migrated, 'no' if none existed")
        return False

    # Validate deprecation period (if applicable)
    dep_match = re.search(r"DEPRECATION-DATE:\s*(\d{4}-\d{2}-\d{2})", commit_msg)
    if dep_match:
        dep_date_str = dep_match.group(1)
        dep_date = datetime.strptime(dep_date_str, "%Y-%m-%d")
        days_deprecated = (datetime.now() - dep_date).days

        if days_deprecated < MIN_DEPRECATION_DAYS:
            print(f"❌ Deprecation period too short: {days_deprecated} days")
            print(f"   Minimum required: {MIN_DEPRECATION_DAYS} days")
            print(f"   Agent was deprecated on: {dep_date_str}")
            print(
                f"   Earliest deletion date: {(dep_date + timedelta(days=MIN_DEPRECATION_DAYS)).strftime('%Y-%m-%d')}",
            )
            return False

    # Check if references were migrated
    ref_match = re.search(r"REFERENCES-MIGRATED:\s*(yes|no)", commit_msg, re.IGNORECASE)
    if ref_match and ref_match.group(1).lower() == "no":
        # If no references existed, that's fine
        pass
    elif ref_match and ref_match.group(1).lower() == "yes":
        # References were migrated, validate with scan
        for agent_path in deleted_agents:
            agent_name = Path(agent_path).stem
            if has_references(agent_name):
                print(f"❌ Agent {agent_name} still has references in codebase")
                print(f"   Run: git grep '{agent_name}' -- '*.py'")
                print("   Migration may be incomplete!")
                return False

    print(f"✅ Agent deletion authorized: {justification[:60]}...")
    for agent in deleted_agents:
        print(f"   Deleting: {agent}")
    return True


def count_references(agent_name: str) -> int:
    """Count how many references to an agent exist in the codebase."""
    try:
        result = subprocess.run(
            ["git", "grep", "-l", agent_name, "--", "*.py"],
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        return 0  # No references found

    # Filter out the agent file itself and test files
    references = [
        line
        for line in result.stdout.splitlines()
        if not line.endswith(f"{agent_name}.py")
        and "test_" not in line
        and "/tests/" not in line
        and "DELETED_SHIM_NAMES" not in line  # Ignore deletion registry
    ]
    return len(references)


def has_references(agent_name: str) -> bool:
    """Check if agent is still referenced in codebase."""
    return count_references(agent_name) > 0


def main() -> int:
    """Main entry point."""
    if check_agent_deletions():
        return 0
    else:
        return 1


if __name__ == "__main__":
    from datetime import timedelta

    sys.exit(main())
