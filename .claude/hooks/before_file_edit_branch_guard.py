"""PreToolUse (Edit|Write|MultiEdit) — worktree-per-chat edit gate.

Hard enforcement for worktree-per-chat. The branch is resolved from the
**working tree that owns the file being edited** (git is run with ``cwd`` set to
the target file's directory), so:

* Edits inside a chat worktree (on a ``chat/*`` / any non-protected branch) -> ALLOW.
* Edits to the primary checkout while it is on a protected branch
  (``main``/``master``) -> BLOCK (exit 2) with a remediation pointing at the
  worktree. This nudges all mutation into the per-chat worktree created by
  ``session_start_branch_guard.py``.

Resolving the branch per-file (rather than from a fixed repo root) is what makes
the gate worktree-aware: a sibling worktree has its own HEAD/branch, which git
reports correctly when invoked from inside it.

Allow conditions (fail-soft / non-blocking):
* Not a git repo / git unavailable / no resolvable path.
* Owning working tree on any non-protected branch.
* ``BRANCH_PER_CHAT_BYPASS=1`` or ``WORKTREE_PER_CHAT_BYPASS=1``.

Self-contained: no dependency on ``lib.claude_hook_common`` (absent in some
checkouts). Protected set override: ``BRANCH_PER_CHAT_PROTECTED=main,master`` (csv).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROTECTED = ("main", "master")


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


def _target_path(payload: dict) -> str:
    ti = payload.get("tool_input")
    if isinstance(ti, dict):
        for key in ("file_path", "path", "notebook_path"):
            val = ti.get(key)
            if isinstance(val, str) and val:
                return val
    return ""


def _is_plan_file(file_path: str) -> bool:
    """True for a plan SSOT markdown file (parent dir == ``plans``, not under an ``_archive/`` tree).

    Plans are a shared, always-on SSOT — not per-chat feature work — so they are EXEMPT from
    worktree-per-chat isolation and must land in the primary checkout's ``plans/`` folder
    (``C:\\Git\\Agentic-Workflow-FRESH\\plans``). Without this exemption a plan written during a chat
    is trapped in an ephemeral worktree and never reaches the canonical SSOT
    (plan ``plan-ssot-notion-pipeline-d2f7a1`` W1). Matches repo-root ``plans/`` and legacy
    ``.claude/plans/`` (both have parent dir ``plans``).
    """
    if not file_path:
        return False
    norm = file_path.replace("\\", "/")
    if not norm.endswith(".md"):
        return False
    if "/plans/_archive/" in norm:
        return False
    if Path(norm).parent.name != "plans":
        return False
    # Exclude docs/reports/plans/ — that is a reports tree, not the plan SSOT (the rule forbids it
    # as a plan location). Canonical plan dirs (repo-root plans/, .claude/plans/) have no docs/reports
    # ancestor, so this denylist is safe.
    lowered = {p.lower() for p in Path(norm).parts}
    if "reports" in lowered or "docs" in lowered:
        return False
    return True


def _owning_dir(file_path: str) -> Path:
    """Directory to run git in: the file's parent if resolvable, else REPO_ROOT."""
    if file_path:
        p = Path(file_path)
        if not p.is_absolute():
            p = REPO_ROOT / p
        parent = p.parent
        # Walk up to the nearest existing ancestor (file may not exist yet on Write).
        while not parent.exists() and parent != parent.parent:
            parent = parent.parent
        if parent.exists():
            return parent
    return REPO_ROOT


def _branch_of(cwd: Path) -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=str(cwd),
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


def _bypass() -> bool:
    return (
        os.environ.get("BRANCH_PER_CHAT_BYPASS") == "1"
        or os.environ.get("WORKTREE_PER_CHAT_BYPASS") == "1"
    )


def main() -> int:
    if _bypass():
        return 0

    payload = _read_payload()
    target = _target_path(payload)

    # Plans are a shared SSOT, exempt from worktree isolation — they always write to the primary
    # checkout's plans/ folder (plan-ssot-notion-pipeline-d2f7a1 W1). Without this, plans get trapped
    # in ephemeral chat worktrees and never reach C:\Git\Agentic-Workflow-FRESH\plans.
    if _is_plan_file(target):
        return 0

    cwd = _owning_dir(target)
    branch = _branch_of(cwd)
    if not branch:
        return 0  # fail-soft
    if branch not in _protected():
        return 0  # owning worktree is isolated — allow

    reason = (
        f"worktree-per-chat: editing the primary checkout on protected branch '{branch}' "
        f"is blocked. Work in this chat's worktree instead (see the SessionStart message for "
        f"its path under .chat-worktrees/), e.g. create one with:\n"
        f"    git worktree add ../.chat-worktrees/chat-<topic> -b chat/<topic>\n"
        f"`cd` into it and edit there. (Set WORKTREE_PER_CHAT_BYPASS=1 only for an intentional "
        f"on-primary change.)"
    )
    sys.stderr.write(reason + "\n")
    return 2  # block


if __name__ == "__main__":
    raise SystemExit(main())
