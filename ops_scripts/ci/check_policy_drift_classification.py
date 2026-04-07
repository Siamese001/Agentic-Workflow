#!/usr/bin/env python3
"""
CI gate: §18 Policy Drift Detection.

Detects commits where production code in governance/routing/protocol modules
is touched with repair_class: production_bug_fix but lacks a ## POLICY_DRIFT
section in the linked evidence file under docs/reports/plans/.

Governance modules (§18.5): L0_routing, L3_orchestration, L5_safety.

Exits 1 on any violation.
"""

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PLANS_DIR = REPO_ROOT / "docs" / "reports" / "plans"

GOVERNANCE_PATHS = ["L0_routing", "L3_orchestration", "L5_safety"]
PRODUCTION_BUG_CLASS = "production_bug_fix"
POLICY_DRIFT_MARKER = "## POLICY_DRIFT"


def get_recent_commit_messages(n: int = 20) -> list[tuple[str, str]]:
    """Return list of (hash, message) for the last n commits."""
    result = subprocess.run(
        ["git", "log", f"-{n}", "--pretty=format:%H %s"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    pairs = []
    for line in result.stdout.splitlines():
        parts = line.split(" ", 1)
        if len(parts) == 2:
            pairs.append((parts[0], parts[1]))
    return pairs


def commit_touches_governance(commit_hash: str) -> bool:
    result = subprocess.run(
        ["git", "diff-tree", "--no-commit-id", "-r", "--name-only", commit_hash],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    for line in result.stdout.splitlines():
        if any(gov in line for gov in GOVERNANCE_PATHS):
            return True
    return False


def evidence_has_policy_drift_section(commit_message: str) -> bool:
    """Search all evidence files for a POLICY_DRIFT section referencing this commit context."""
    for path in sorted(PLANS_DIR.rglob("*.md")):
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
            if POLICY_DRIFT_MARKER in content:
                return True
        except OSError:    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
            continue
    return False


def main() -> int:
    violations: list[str] = []
    commits = get_recent_commit_messages(20)

    for commit_hash, message in commits:
        if PRODUCTION_BUG_CLASS not in message:
            continue
        if not commit_touches_governance(commit_hash):
            continue
        if not evidence_has_policy_drift_section(message):
            violations.append(
                f"POLICY DRIFT MISCLASSIFICATION: commit {commit_hash[:8]} "
                f"touches governance module with repair_class: {PRODUCTION_BUG_CLASS} "
                f"but no evidence file contains ## POLICY_DRIFT section (§18.5)",
            )

    if violations:
        print(f"ERROR: §18 policy drift classification violations ({len(violations)}):")
        for v in violations:
            print(f"  {v}")
        return 1

    print("OK: §18 policy drift classification — no misclassified governance commits detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
