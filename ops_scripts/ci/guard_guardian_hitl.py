#!/usr/bin/env python3
"""
Guard: HITL Authorization for New Guardian Exemptions.

Runs at the commit-msg stage. If the staged diff introduces any new
`# guardian: allow-*` lines in production files, the commit message
MUST contain `HITL-APPROVED: <description>` to document the HITL
decision record.

This enforces §8.5.2: every new guardian exemption requires a human
decision point, not just a ratchet ceiling check.

Exit codes:
  0 — no new exemptions, or HITL-APPROVED present in commit message
  1 — new exemptions found without HITL-APPROVED in commit message

Usage (commit-msg stage):
  pre-commit passes the path to the commit message file as argv[1].
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]

PRODUCTION_DIRS = {
    "agentic_core",
    "apps_lic",
    "apps_rg",
    "apps_shared",
    "apps_exec",
    "apps_eval",
    "apps_rfp",
    "apps_research",
    "system_learning",
}

_GUARDIAN_ALLOW_RE = re.compile(r"^\+.*#\s*guardian:\s+allow-", re.MULTILINE)


def _get_staged_diff() -> str:
    """Return the unified diff of staged changes."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--unified=0"],
            capture_output=True,
            text=True,
            cwd=str(_REPO_ROOT),
        )
        return result.stdout if result.returncode == 0 else ""
    except (ValueError, TypeError, RuntimeError) as e:
        return ""


def _diff_adds_guardian_exemptions(diff: str) -> list[str]:
    """
    Return a list of added `# guardian: allow-*` lines from the staged diff,
    restricted to production directories only.
    """
    if not diff:
        return []

    added_lines: list[str] = []
    current_file: str | None = None

    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            current_file = line[6:]
        elif line.startswith("+") and not line.startswith("+++"):
            if current_file is None:
                continue
            first_part = current_file.split("/")[0]
            if first_part not in PRODUCTION_DIRS:
                continue
            if re.search(r"#\s*guardian:\s+allow-", line):
                added_lines.append(f"{current_file}: {line[1:].strip()}")

    return added_lines


def main() -> int:
    if len(sys.argv) < 2:
        print("[guard-guardian-hitl] No commit message file provided — skipping.")
        return 0

    commit_msg_file = Path(sys.argv[1])
    if not commit_msg_file.exists():
        print(f"[guard-guardian-hitl] Commit message file not found: {commit_msg_file}")
        return 0

    commit_msg = commit_msg_file.read_text(encoding="utf-8", errors="replace")

    diff = _get_staged_diff()
    new_exemptions = _diff_adds_guardian_exemptions(diff)

    if not new_exemptions:
        return 0

    if "HITL-APPROVED:" in commit_msg:
        print(
            f"[guard-guardian-hitl] PASS — {len(new_exemptions)} new guardian exemption(s) "
            f"with HITL-APPROVED in commit message.",
        )
        return 0

    print()
    print("=" * 70)
    print("HITL AUTHORIZATION REQUIRED — New Guardian Exemptions (§8.5.2)")
    print("=" * 70)
    print()
    print(f"This commit adds {len(new_exemptions)} new `# guardian: allow-*` exemption(s)")
    print("in production code. A Human-In-The-Loop decision record is required.")
    print()
    print("New exemptions detected:")
    for line in new_exemptions:
        print(f"  {line}")
    print()
    print("Add the following to your commit message:")
    print()
    print("  HITL-APPROVED: <description of the HITL decision and rationale>")
    print()
    print("Example:")
    print("  HITL-APPROVED: Reviewed with team — allow-global-mutation in bootstrap")
    print("  path is unavoidable; no alternative import ordering exists for this module.")
    print()
    print("To invoke HITL: use /antipattern-hitl-gate in Cascade, present the options,")
    print("and document the chosen option in HITL-APPROVED:.")
    print()
    return 1


if __name__ == "__main__":
    sys.exit(main())
