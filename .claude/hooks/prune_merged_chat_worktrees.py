"""SessionStart — reap merged chat worktrees (complement to worktree-per-chat).

The worktree-per-chat guard (``session_start_branch_guard.py``) CREATES a git worktree per chat at
``<repo-parent>/.chat-worktrees/chat-<stamp>-<hex>`` on a ``chat/<...>`` branch. This hook is the
other half of the lifecycle: once such a chat worktree's branch is fully merged into
``origin/main`` and its tree is clean, the worktree has served its purpose and is removed
(``git worktree remove`` + ``git branch -d``). Merged + clean ⇒ zero data loss.

Hard safety envelope — a worktree is reaped ONLY when ALL hold:
  * it lives under the chat-worktree root (``.chat-worktrees/``) and its branch matches ``chat/*``
    — long-lived feature/codex/fix worktrees and the primary checkout are NEVER eligible;
  * it is NOT the worktree this session is running in (never reap your own CWD);
  * its branch is an ANCESTOR of ``origin/main`` (fully merged — unmerged work is never touched);
  * its working tree is CLEAN (``git status --porcelain`` empty — uncommitted work is never touched);
  * its HEAD commit is older than the grace window (protects a worktree another live chat just made).

Self-contained (no ``lib`` import). Best-effort, fail-soft, always exits 0 — never blocks a session.

Bypass: ``WORKTREE_MERGE_CLEANUP_BYPASS=1`` (also honors ``WORKTREE_PER_CHAT_BYPASS=1``).
Dry-run (report, don't delete): ``WORKTREE_MERGE_CLEANUP_DRY_RUN=1``.
Grace window: ``WORKTREE_CLEANUP_MIN_AGE_MINUTES`` (default ``0`` — reap as soon as merged+clean).
Worktree root override: ``CHAT_WORKTREE_ROOT`` (default ``<repo-parent>/.chat-worktrees``).
Trunk ref override: ``WORKTREE_CLEANUP_TRUNK_REF`` (default ``origin/main``).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PROTECTED = ("main", "master", "release")


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


def _bypass() -> bool:
    return (
        os.environ.get("WORKTREE_MERGE_CLEANUP_BYPASS") == "1"
        or os.environ.get("WORKTREE_PER_CHAT_BYPASS") == "1"
    )


def _chat_root(repo_root: Path) -> Path:
    override = os.environ.get("CHAT_WORKTREE_ROOT", "").strip()
    return Path(override) if override else repo_root.parent / ".chat-worktrees"


def _trunk_ref() -> str:
    return os.environ.get("WORKTREE_CLEANUP_TRUNK_REF", "").strip() or "origin/main"


def _min_age_seconds() -> int:
    raw = os.environ.get("WORKTREE_CLEANUP_MIN_AGE_MINUTES", "").strip()
    try:
        return max(0, int(float(raw))) * 60 if raw else 0
    except ValueError:
        return 0


def _parse_worktrees(porcelain: str) -> list[dict[str, str]]:
    """Parse ``git worktree list --porcelain`` into [{path, head, branch}]."""
    out: list[dict[str, str]] = []
    cur: dict[str, str] = {}
    for line in porcelain.splitlines():
        if not line.strip():
            if cur:
                out.append(cur)
                cur = {}
            continue
        if line.startswith("worktree "):
            cur = {"path": line[len("worktree ") :].strip()}
        elif line.startswith("HEAD "):
            cur["head"] = line[len("HEAD ") :].strip()
        elif line.startswith("branch "):
            ref = line[len("branch ") :].strip()
            cur["branch"] = ref[len("refs/heads/") :] if ref.startswith("refs/heads/") else ref
    if cur:
        out.append(cur)
    return out


def reap_merged_chat_worktrees(
    *,
    repo_root: Path,
    trunk_ref: str = "origin/main",
    current_worktree: Path | None = None,
    chat_root: Path | None = None,
    dry_run: bool = False,
    min_age_seconds: int = 0,
    do_fetch: bool = True,
) -> dict:
    """Reap fully-merged, clean chat worktrees. Returns a structured report (never raises)."""
    report: dict = {"scanned": 0, "reaped": [], "skipped": [], "dry_run": dry_run, "status": "ok"}
    repo_root = repo_root.resolve()
    cur = (current_worktree or repo_root).resolve()
    root = (chat_root or _chat_root(repo_root)).resolve()

    if do_fetch:
        _git("fetch", "origin", "main", "--quiet", cwd=repo_root)  # best-effort; ignore failure

    rc, porcelain = _git("worktree", "list", "--porcelain", cwd=repo_root)
    if rc != 0:
        report["status"] = "no_worktrees"
        return report

    now = time.time()
    for wt in _parse_worktrees(porcelain):
        path = Path(wt.get("path", "")).resolve()
        branch = wt.get("branch", "")
        report["scanned"] += 1

        def skip(reason: str) -> None:
            report["skipped"].append({"path": str(path), "branch": branch, "reason": reason})

        # Eligibility: only ephemeral chat worktrees under the chat root, on a chat/* branch.
        try:
            under_chat_root = root == path or root in path.parents
        except (OSError, ValueError):
            under_chat_root = False
        if not under_chat_root:
            continue  # not a chat worktree — silently ignore (primary, feature, codex, ...)
        if not branch or branch in PROTECTED or not branch.startswith("chat/"):
            skip("not_chat_branch")
            continue
        if path == cur:
            skip("current_worktree")
            continue

        # Merged into trunk?
        rc_anc, _ = _git("merge-base", "--is-ancestor", branch, trunk_ref, cwd=repo_root)
        if rc_anc != 0:
            skip("not_merged_into_trunk")
            continue

        # Clean working tree?
        rc_st, st = _git("status", "--porcelain", cwd=path)
        if rc_st != 0 or st.strip():
            skip("uncommitted_changes")
            continue

        # Grace window — protect a worktree another live chat just created+merged.
        if min_age_seconds > 0:
            rc_ts, ts = _git("show", "-s", "--format=%ct", "HEAD", cwd=path)
            try:
                age = now - float(ts)
            except (ValueError, TypeError):
                age = min_age_seconds + 1  # unknown age → don't let it block reaping
            if rc_ts == 0 and age < min_age_seconds:
                skip("within_grace_window")
                continue

        if dry_run:
            report["reaped"].append({"path": str(path), "branch": branch, "dry_run": True})
            continue

        rc_rm, _ = _git("worktree", "remove", str(path), cwd=repo_root)
        if rc_rm != 0:
            rc_rm, _ = _git("worktree", "remove", "--force", str(path), cwd=repo_root)
        if rc_rm != 0:
            skip("worktree_remove_failed")
            continue
        # Branch is now free; -d first (safe), -D fallback (we already proved ancestor-of-trunk).
        rc_br, _ = _git("branch", "-d", branch, cwd=repo_root)
        if rc_br != 0:
            _git("branch", "-D", branch, cwd=repo_root)
        report["reaped"].append({"path": str(path), "branch": branch})

    return report


def _emit_context(message: str) -> None:
    sys.stdout.write(
        json.dumps(
            {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": message}}
        )
    )


def main() -> int:
    # Drain stdin (SessionStart payload) so the pipe never blocks; we don't need its contents.
    try:
        sys.stdin.read()
    except OSError:
        pass

    if _bypass():
        return 0

    report = reap_merged_chat_worktrees(
        repo_root=REPO_ROOT,
        trunk_ref=_trunk_ref(),
        current_worktree=REPO_ROOT,
        dry_run=os.environ.get("WORKTREE_MERGE_CLEANUP_DRY_RUN") == "1",
        min_age_seconds=_min_age_seconds(),
    )
    reaped = report.get("reaped") or []
    if reaped:
        verb = "would reap" if report.get("dry_run") else "reaped"
        lines = "\n".join(f"  - {r['branch']}  ({r['path']})" for r in reaped)
        msg = (
            f"worktree-merge-cleanup: {verb} {len(reaped)} merged+clean chat worktree(s):\n{lines}\n"
            f"(branches fully merged into {_trunk_ref()}; no committed work lost)."
        )
        sys.stderr.write("[HOOK] " + msg + "\n")
        _emit_context(msg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
