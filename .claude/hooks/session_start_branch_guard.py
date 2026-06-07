"""SessionStart — branch-per-chat guard.

Constitutional intent: every chat works on its own fresh branch cut from the
default branch (``main``), never directly on ``main``/``master``. This hook runs
at session start and, when HEAD is on a protected branch, creates a new
``chat/<UTC-stamp>-<session-hex>`` branch off the *current* default-branch tip.
Any uncommitted work in the tree is carried onto the new branch by ``git switch
-c`` (nothing is lost).

Behavior:
* HEAD on a protected branch (``main``/``master``) -> create + switch to a new
  chat branch; emit additionalContext so the assistant knows the new branch.
* HEAD already on a non-protected branch -> no-op (chat is already isolated).
* Not a git repo / git unavailable / dirty edge cases -> fail-soft (allow).

This is the *proactive* half. The hard enforcement teeth live in
``before_file_edit_branch_guard.py`` (PreToolUse Edit|Write|MultiEdit), which
blocks edits whenever HEAD is on a protected branch — so even a resumed session
or a manual ``git checkout main`` cannot silently mutate the default branch.

Bypass: ``BRANCH_PER_CHAT_BYPASS=1``.
Protected set override: ``BRANCH_PER_CHAT_PROTECTED=main,master,release`` (csv).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from lib.claude_hook_common import read_payload, write_receipt

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROTECTED = ("main", "master")


def _git(*args: str) -> tuple[int, str]:
    """Run a git command (shell=False, bounded). Returns (returncode, stdout-stripped)."""
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return 1, ""
    return proc.returncode, (proc.stdout or "").strip()


def _protected() -> set[str]:
    raw = os.environ.get("BRANCH_PER_CHAT_PROTECTED", "")
    if raw.strip():
        return {b.strip() for b in raw.split(",") if b.strip()}
    return set(DEFAULT_PROTECTED)


def _emit_context(message: str) -> None:
    """SessionStart additionalContext is surfaced to the assistant at chat start."""
    out = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": message,
        }
    }
    sys.stdout.write(json.dumps(out))


def main() -> int:
    payload = read_payload()

    if os.environ.get("BRANCH_PER_CHAT_BYPASS") == "1":
        write_receipt("sessionStartBranchGuard", payload, "allow", "bypass env set")
        return 0

    rc, branch = _git("rev-parse", "--abbrev-ref", "HEAD")
    if rc != 0 or not branch:
        # Not a git repo or git unavailable — fail soft.
        write_receipt("sessionStartBranchGuard", payload, "allow", "no git branch")
        return 0

    protected = _protected()
    if branch not in protected:
        write_receipt(
            "sessionStartBranchGuard", payload, "allow", f"already on isolated branch '{branch}'"
        )
        return 0

    # On a protected branch — cut a fresh chat branch off the current tip.
    session_id = str(payload.get("session_id") or payload.get("sessionId") or "")
    hexpart = (session_id.replace("-", "")[:8]) or "00000000"
    # SessionStart payload carries no wall clock we trust; derive a stamp from git.
    rc_ts, stamp = _git("show", "-s", "--format=%cd", "--date=format:%Y%m%d-%H%M%S", "HEAD")
    if rc_ts != 0 or not stamp:
        stamp = "session"
    new_branch = f"chat/{stamp}-{hexpart}"

    rc_sw, _ = _git("switch", "-c", new_branch)
    if rc_sw != 0:
        # Name collision or other failure — try a uniquified name once.
        rc_sw, _ = _git("switch", "-c", f"{new_branch}-{os.getpid()}")
        if rc_sw != 0:
            msg = (
                f"branch-per-chat: still on protected branch '{branch}'. Auto-create failed; "
                f"create a working branch before editing (e.g. `git switch -c chat/<topic>`)."
            )
            write_receipt("sessionStartBranchGuard", payload, "warn", msg)
            sys.stderr.write("[HOOK WARN] " + msg + "\n")
            _emit_context(msg)
            return 0
        new_branch = f"{new_branch}-{os.getpid()}"

    msg = (
        f"branch-per-chat: this chat was on protected branch '{branch}'. Created and switched to "
        f"'{new_branch}' (cut from '{branch}'). All work for this chat lands here, not on '{branch}'."
    )
    write_receipt("sessionStartBranchGuard", payload, "allow", msg)
    _emit_context(msg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
