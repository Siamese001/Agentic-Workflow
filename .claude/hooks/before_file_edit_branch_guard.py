"""PreToolUse (Edit|Write|MultiEdit) — protected-branch edit gate.

Hard enforcement for branch-per-chat. Blocks any file mutation while HEAD is on
a protected branch (``main``/``master``). This is the teeth behind
``session_start_branch_guard.py``: a resumed session, a manual
``git checkout main``, or a failed auto-branch cannot silently mutate the
default branch — the first Edit/Write/MultiEdit is refused with exit 2 and a
remediation instruction.

Allow conditions (fail-soft / non-blocking):
* Not a git repo or git unavailable.
* HEAD on any non-protected branch.
* ``BRANCH_PER_CHAT_BYPASS=1`` set.

Protected set override: ``BRANCH_PER_CHAT_PROTECTED=main,master,release`` (csv).
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from lib.claude_hook_common import allow, block, read_payload, write_receipt

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROTECTED = ("main", "master")


def _current_branch() -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    if proc.returncode != 0:
        return ""
    return (proc.stdout or "").strip()


def _protected() -> set[str]:
    raw = os.environ.get("BRANCH_PER_CHAT_PROTECTED", "")
    if raw.strip():
        return {b.strip() for b in raw.split(",") if b.strip()}
    return set(DEFAULT_PROTECTED)


def main() -> int:
    payload = read_payload()

    if os.environ.get("BRANCH_PER_CHAT_BYPASS") == "1":
        return allow("bypass env set")

    branch = _current_branch()
    if not branch:
        return allow("no git branch (fail-soft)")

    if branch not in _protected():
        return allow(f"on isolated branch '{branch}'")

    reason = (
        f"branch-per-chat: editing on protected branch '{branch}' is blocked. "
        f"Create a working branch first, e.g.:\n"
        f"    git switch -c chat/<topic>\n"
        f"then retry the edit. (Set BRANCH_PER_CHAT_BYPASS=1 only for an intentional "
        f"on-main change.)"
    )
    write_receipt("beforeFileEditBranchGuard", payload, "block", reason)
    return block(reason)


if __name__ == "__main__":
    raise SystemExit(main())
