"""SessionStart — worktree-per-chat guard.

Intent (per user directive 2026-06-08): every chat/feature gets its own **git
worktree** cut from the default branch, rather than just a new branch in the
primary checkout. When HEAD is on a protected branch (``main``/``master``), this
hook creates a fresh ``chat/<stamp>-<hex>`` branch in a sibling worktree under
``<repo-parent>/.chat-worktrees/`` and instructs the assistant to perform all
work for the chat inside that worktree.

KNOWN CONSTRAINT (documented, accepted): a SessionStart hook is a subprocess and
**cannot relocate the already-running session's working directory** into the new
worktree. It therefore creates the worktree and emits ``additionalContext`` telling
the assistant to ``cd`` into the worktree path and target files there. The hard
teeth live in ``before_file_edit_branch_guard.py``, which is worktree-aware: it
allows edits whose owning working tree is on a non-protected branch (i.e. inside
the chat worktree) and blocks edits to the primary checkout while it is on a
protected branch — nudging all mutation into the worktree.

Behaviour:
* HEAD on a protected branch -> create worktree + chat branch; emit context.
* HEAD already on a non-protected branch -> no-op (already isolated).
* Worktree/branch already exists, git unavailable, not a repo -> fail-soft (allow).

Self-contained: does not depend on ``lib.claude_hook_common`` (absent in some
checkouts). Always exits 0 (proactive half; never blocks session start).

Bypass: ``BRANCH_PER_CHAT_BYPASS=1`` or ``WORKTREE_PER_CHAT_BYPASS=1``.
Protected set override: ``BRANCH_PER_CHAT_PROTECTED=main,master,release`` (csv).
Worktree root override: ``CHAT_WORKTREE_ROOT=/abs/path`` (default ``<repo-parent>/.chat-worktrees``).
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROTECTED = ("main", "master")


def _git(*args: str, cwd: Path | None = None) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(cwd or REPO_ROOT),
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


def _bypass() -> bool:
    return (
        os.environ.get("BRANCH_PER_CHAT_BYPASS") == "1"
        or os.environ.get("WORKTREE_PER_CHAT_BYPASS") == "1"
    )


def _worktree_root() -> Path:
    override = os.environ.get("CHAT_WORKTREE_ROOT", "").strip()
    if override:
        return Path(override)
    return REPO_ROOT.parent / ".chat-worktrees"


def _read_payload() -> dict:
    try:
        raw = sys.stdin.read()
    except OSError:
        return {}
    try:
        obj = json.loads(raw) if raw.strip() else {}
        return obj if isinstance(obj, dict) else {}
    except json.JSONDecodeError:
        return {}


def _emit_context(message: str) -> None:
    out = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": message,
        }
    }
    sys.stdout.write(json.dumps(out))


def main() -> int:
    payload = _read_payload()

    if _bypass():
        return 0

    rc, branch = _git("rev-parse", "--abbrev-ref", "HEAD")
    if rc != 0 or not branch:
        return 0  # not a git repo / git unavailable — fail-soft
    if branch not in _protected():
        return 0  # already on an isolated branch — nothing to do

    session_id = str(payload.get("session_id") or payload.get("sessionId") or "")
    hexpart = (session_id.replace("-", "")[:8]) or "00000000"
    stamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%d-%H%M%S")
    new_branch = f"chat/{stamp}-{hexpart}"
    wt_dirname = f"chat-{stamp}-{hexpart}"
    wt_path = _worktree_root() / wt_dirname

    try:
        _worktree_root().mkdir(parents=True, exist_ok=True)
    except OSError:
        pass

    # Create the worktree on a fresh chat branch cut from the current (protected) tip.
    rc_wt, out_wt = _git("worktree", "add", str(wt_path), "-b", new_branch)
    if rc_wt != 0:
        # Retry once with a PID-uniquified branch/dir (collision), else fail-soft.
        new_branch = f"{new_branch}-{os.getpid()}"
        wt_path = _worktree_root() / f"{wt_dirname}-{os.getpid()}"
        rc_wt, out_wt = _git("worktree", "add", str(wt_path), "-b", new_branch)
    if rc_wt != 0:
        msg = (
            f"worktree-per-chat: still on protected branch '{branch}'. Auto-worktree "
            f"failed ({out_wt or 'unknown error'}). Create one manually before editing:\n"
            f"    git worktree add {_worktree_root() / wt_dirname} -b {new_branch}\n"
            f"then `cd` into it. (Set WORKTREE_PER_CHAT_BYPASS=1 for an intentional "
            f"on-primary change.)"
        )
        sys.stderr.write("[HOOK WARN] " + msg + "\n")
        _emit_context(msg)
        return 0

    msg = (
        f"worktree-per-chat: this chat was on protected branch '{branch}'. Created a git "
        f"worktree for the feature at:\n    {wt_path}\n"
        f"on branch '{new_branch}' (cut from '{branch}').\n\n"
        f"⚠️ ALL work for this chat must happen inside that worktree — the primary checkout "
        f"({REPO_ROOT}) stays on '{branch}' and edits to it are blocked. First action: "
        f"`cd {wt_path}` for shell commands, and target file edits at paths under {wt_path}. "
        f"Commit and push from the worktree; open the PR from branch '{new_branch}'."
    )
    sys.stderr.write("[HOOK] " + msg + "\n")
    _emit_context(msg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
