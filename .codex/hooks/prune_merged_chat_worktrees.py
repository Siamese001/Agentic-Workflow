"""Manual worktree cleanup — report or delete delivered local worktrees/branches.

SessionStart is intentionally non-mutating: if Claude invokes this file as a hook, it drains stdin
and exits without deleting anything. Cleanup is an explicit operator action:

    python .codex/hooks/prune_merged_chat_worktrees.py --dry-run
    python .codex/hooks/prune_merged_chat_worktrees.py --delete-merged

Hard safety envelope — a worktree is deleted ONLY when ALL hold:
  * its branch matches an ENABLED reap prefix. Default is ``chat/`` + ``feat/``. ``chat/*``
    worktrees must additionally live under the legacy chat-worktree root (``.chat-worktrees/``);
    ``feat/*`` worktrees may live as registered siblings. Long-lived ``codex-``/``claude-`` worktrees
    and the primary checkout are NEVER eligible by default. An operator can opt other prefixes in
    via ``WORKTREE_REAP_BRANCH_PREFIXES``; those may live anywhere (sibling worktrees);
  * it does NOT carry a ``.keep-worktree`` marker file (universal opt-out — kept regardless);
  * it is NOT the worktree this session is running in (never reap your own CWD);
  * its branch tip is an ANCESTOR of ``origin/main`` (fully merged by commit ancestry);
  * its working tree is CLEAN (``git status --porcelain`` empty — uncommitted work is never touched);
  * its HEAD commit is older than the grace window (protects a worktree another live chat just made).

Branch-prune half (the local branch cleanup): the worktree deletion path only deletes a branch
when it removes *that branch's worktree*. Merged branches whose worktree was already removed
(or which never had one) accumulate forever. ``prune_merged_branches`` is the
complement — after a merge+push, every local ``chat/``/``feat/`` branch that is (a) ancestor-contained
in ``origin/main`` and (b) has NO checked-out worktree is deleted. Same zero-loss guarantee: a branch
is only deleted when its exact tip is reachable from ``origin/main``.

Patch-equivalence, cherry-pick equivalence, or "no unique commits" evidence is NOT cleanup proof.
Those signals may justify a deliberate ``git merge -s ours --no-ff <branch>`` onto ``main`` to record
the branch tip, but deletion waits until ``git merge-base --is-ancestor <branch> origin/main`` passes.

Self-contained (no ``lib`` import). Best-effort, fail-soft, always exits 0 in hook mode — never
blocks a session.

Bypass: ``WORKTREE_MERGE_CLEANUP_BYPASS=1`` (also honors ``WORKTREE_PER_CHAT_BYPASS=1``).
Dry-run (report, don't delete): default for CLI unless ``--delete-merged`` is passed.
Grace window: ``WORKTREE_CLEANUP_MIN_AGE_MINUTES`` (default ``30`` — never reap a worktree whose
  HEAD is newer than N minutes; item #1, raised from ``0`` to end the mid-session reap-race).
Reap prefixes: ``WORKTREE_REAP_BRANCH_PREFIXES`` csv (default ``chat/``,``feat/``; opt other
  prefixes in only for explicit manual cleanup).
Branch-prune toggle: ``WORKTREE_PRUNE_MERGED_BRANCHES`` (default ``1`` — set ``0`` to disable the
  standalone merged-branch sweep and only reap worktrees).
Branch-prune prefixes: ``WORKTREE_PRUNE_BRANCH_PREFIXES`` csv (default ``chat/``,``feat/``).
Trunk acceptance ref: ``WORKTREE_CLEANUP_TRUNK_REF`` (default ``origin/main``). The branch tip must
  be an ancestor of that ref.
Opt-out marker: a ``.keep-worktree`` file in any worktree exempts it permanently.
Legacy chat root override: ``CHAT_WORKTREE_ROOT`` (default ``<repo-parent>/.chat-worktrees``).
Trunk ref override: ``WORKTREE_CLEANUP_TRUNK_REF`` (default ``origin/main``).

CLI (manual sweep): ``python .codex/hooks/prune_merged_chat_worktrees.py [--dry-run]
  [--delete-merged] [--no-branches] [--min-age-minutes N]``.
"""

from __future__ import annotations

import argparse
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


def _primary_worktree(start: Path) -> Path:
    """The primary working tree (anchor for the chat root), resolved from any worktree.

    ``REPO_ROOT`` is ``parents[2]`` of this file — correct when the SessionStart hook runs from the
    primary checkout, but WRONG when the script is invoked from inside a linked worktree (the chat
    root would resolve to ``<worktree>/.chat-worktrees``). ``git rev-parse --git-common-dir`` always
    points at ``<primary>/.git`` regardless of which worktree is current, so its parent is the
    primary. Fail-soft: returns ``start`` unchanged if git is unavailable."""
    rc, common = _git("rev-parse", "--git-common-dir", cwd=start)
    if rc != 0 or not common:
        return start
    p = Path(common)
    if not p.is_absolute():
        p = (start / p)
    return p.resolve().parent  # <primary>/.git -> <primary>


def _cwd_toplevel(start: Path) -> Path:
    """Top level of the worktree containing ``start`` (the session's own worktree — never reaped)."""
    rc, top = _git("rev-parse", "--show-toplevel", cwd=start)
    return Path(top).resolve() if rc == 0 and top else start


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


# Item #1: default grace window raised 0 -> 30 min to end the mid-session reap-race
# (a sibling chat's just-merged worktree being deleted before its session finishes
# writing into it). NOTE: this is the *env-reader* default used by main(); the
# ``reap_merged_chat_worktrees`` signature default stays ``0`` so unit tests that
# expect immediate reaping keep passing.
_DEFAULT_MIN_AGE_MINUTES = 30


def _min_age_seconds() -> int:
    raw = os.environ.get("WORKTREE_CLEANUP_MIN_AGE_MINUTES", "").strip()
    if not raw:
        return _DEFAULT_MIN_AGE_MINUTES * 60
    try:
        return max(0, int(float(raw))) * 60
    except ValueError:
        return _DEFAULT_MIN_AGE_MINUTES * 60


# Which branch prefixes are eligible for explicit cleanup. Default ``chat/`` + ``feat/``:
# a ``feat/*`` worktree is a legacy delivery vehicle, so once its branch is merged into the
# trunk and its tree is clean it is a *delivered leftover*. The
# merged-into-trunk + clean-tree + grace-window guards below protect any in-progress/unmerged work,
# so a ``feat/*`` you are still using is NEVER deleted. ``codex-``/``claude-`` can be opted in via
# ``WORKTREE_REAP_BRANCH_PREFIXES``; a ``.keep-worktree`` marker exempts any worktree regardless.
_DEFAULT_REAP_PREFIXES: tuple[str, ...] = ("chat/", "feat/")


def _reap_prefixes() -> tuple[str, ...]:
    raw = (os.environ.get("WORKTREE_REAP_BRANCH_PREFIXES") or "").strip()
    if not raw:
        return _DEFAULT_REAP_PREFIXES
    parsed = tuple(p.strip() for p in raw.split(",") if p.strip())
    return parsed or _DEFAULT_REAP_PREFIXES


def _csv_env(name: str, default: tuple[str, ...]) -> tuple[str, ...]:
    raw = (os.environ.get(name) or "").strip()
    if not raw:
        return default
    parsed = tuple(p.strip() for p in raw.split(",") if p.strip())
    return parsed or default


def _prune_branches_enabled() -> bool:
    return os.environ.get("WORKTREE_PRUNE_MERGED_BRANCHES", "1").strip() != "0"


def _reap_detached_enabled() -> bool:
    return os.environ.get("WORKTREE_REAP_DETACHED", "0").strip() != "0"


def _prune_branch_prefixes() -> tuple[str, ...]:
    return _csv_env("WORKTREE_PRUNE_BRANCH_PREFIXES", ("chat/", "feat/"))


def _matched_prefix(branch: str, prefixes: tuple[str, ...]) -> str | None:
    for p in prefixes:
        if p and branch.startswith(p):
            return p
    return None


def _branch_prefix_candidates(branch: str) -> tuple[str, ...]:
    candidates = [branch]
    if "/" in branch:
        normalized = branch.replace("/", "-")
        if normalized != branch:
            candidates.append(normalized)
    return tuple(dict.fromkeys(candidates))


def _worktree_prefix_candidates(branch: str, path: Path) -> tuple[str, ...]:
    candidates = list(_branch_prefix_candidates(branch)) if branch else []
    candidates.append(path.name)
    return tuple(dict.fromkeys(candidates))


def _is_ancestor(ref: str, trunk_ref: str, *, repo_root: Path) -> bool:
    """True only when ``ref`` is reachable from ``trunk_ref`` by commit ancestry."""

    if not ref or not trunk_ref:
        return False
    rc, _ = _git("merge-base", "--is-ancestor", ref, trunk_ref, cwd=repo_root)
    return rc == 0


def _worktree_branches(porcelain: str) -> set[str]:
    """Branches that currently have a checked-out worktree.

    Branch-only cleanup must skip these; the worktree cleanup path handles branch deletion after
    removing the checked-out worktree.
    """
    return {wt["branch"] for wt in _parse_worktrees(porcelain) if wt.get("branch")}


def _worktree_age_seconds(path: Path, now: float) -> float | None:
    """Age (seconds) of a worktree by its MOST RECENT signal, or ``None`` if unknown.

    Signals: (a) the HEAD commit time, and (b) the worktree's own creation mtime (the
    per-worktree ``.git`` gitdir-link file is written at ``git worktree add`` time and is
    not touched by content edits — a stable creation proxy). The smaller (more recent)
    age wins so a freshly-created worktree is protected even when its HEAD points at an old
    trunk tip (the empty-but-just-created reap-race; item #1).
    """
    ages: list[float] = []
    rc_ts, ts = _git("show", "-s", "--format=%ct", "HEAD", cwd=path)
    if rc_ts == 0:
        try:
            ages.append(now - float(ts))
        except (ValueError, TypeError):
            pass
    for probe in (path / ".git", path):
        try:
            ages.append(now - probe.stat().st_mtime)
            break
        except OSError:
            continue
    return min(ages) if ages else None


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
    reap_branch_prefixes: tuple[str, ...] = ("chat/",),
    allow_detached: bool = False,
) -> dict:
    """Report or delete fully delivered, clean worktrees. Returns a structured report.

    ``reap_branch_prefixes`` is the set of enabled branch prefixes. The default
    ``("chat/",)`` preserves the original behavior: only ``chat/*`` worktrees *under the
    chat root* are eligible. Adding non-chat prefixes (e.g. ``feat/``) lets the explicit cleanup
    command also remove merged sibling worktrees living anywhere. Detached worktrees are skipped
    unless ``allow_detached`` is true. A ``.keep-worktree`` marker file in any worktree exempts it
    permanently.
    """
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
        head = wt.get("head", "")
        report["scanned"] += 1

        def skip(reason: str) -> None:
            report["skipped"].append({"path": str(path), "branch": branch, "reason": reason})

        # Eligibility: branch must match an enabled reap prefix. Legacy ``chat/*`` worktrees
        # must live under the chat root; non-chat prefixes
        # (opt-in) may live anywhere (sibling worktrees).
        try:
            under_chat_root = root == path or root in path.parents
        except (OSError, ValueError):
            under_chat_root = False
        if not branch and not allow_detached:
            skip("detached_worktree_disabled")
            continue
        label_candidates = _worktree_prefix_candidates(branch, path)
        matched = None
        label = label_candidates[-1] if label_candidates else path.name
        for candidate in label_candidates:
            matched = _matched_prefix(candidate, reap_branch_prefixes)
            if matched is not None:
                label = candidate
                break
        # ``chat/*`` and non-matching branches are only *considered* under the chat root;
        # outside it they are silently ignored (preserves the "ignore manual worktrees" rule).
        if (matched == "chat/" or matched is None) and not under_chat_root:
            continue  # not an ephemeral chat worktree under the root — silently ignore
        if matched is None or not label:
            skip("not_chat_branch")
            continue
        if branch in PROTECTED:
            skip("not_chat_branch")
            continue
        if path == cur:
            skip("current_worktree")
            continue
        # Universal opt-out marker: a worktree carrying ``.keep-worktree`` is never reaped.
        if (path / ".keep-worktree").exists():
            skip("keep_marker")
            continue

        # Merged into trunk by exact commit ancestry. Patch-equivalent or no-unique-commit evidence
        # is insufficient; record superseded branches with an explicit ours merge before cleanup.
        ref = branch or head
        if not ref:
            skip("missing_head")
            continue
        if not _is_ancestor(ref, trunk_ref, repo_root=repo_root):
            skip("not_merged_into_trunk")
            continue

        # Clean working tree?
        rc_st, st = _git("status", "--porcelain", cwd=path)
        if rc_st != 0 or st.strip():
            skip("uncommitted_changes")
            continue

        # Grace window — protect a worktree another live chat just created+merged.
        # Recency is the MOST RECENT of (a) the HEAD commit time and (b) the worktree's
        # own creation time. (b) is essential (item #1): a freshly-created worktree cut
        # from an OLD trunk tip has an old HEAD commit, so keying only on HEAD would not
        # protect the empty-but-just-created window — the exact reap-race that orphans a
        # sibling session's first write.
        if min_age_seconds > 0:
            recent_age = _worktree_age_seconds(path, now)
            if recent_age is not None and recent_age < min_age_seconds:
                skip("within_grace_window")
                continue

        if dry_run:
            report["reaped"].append(
                {"path": str(path), "branch": branch, "label": label, "dry_run": True}
            )
            continue

        rc_rm, _ = _git("worktree", "remove", str(path), cwd=repo_root)
        if rc_rm != 0:
            rc_rm, _ = _git("worktree", "remove", "--force", str(path), cwd=repo_root)
        if rc_rm != 0:
            skip("worktree_remove_failed")
            continue
        if branch:
            # Branch is now free; -d first (safe), -D fallback (we already proved ancestor-of-trunk).
            rc_br, _ = _git("branch", "-d", branch, cwd=repo_root)
            if rc_br != 0:
                _git("branch", "-D", branch, cwd=repo_root)
        report["reaped"].append({"path": str(path), "branch": branch, "label": label})

    return report


def prune_merged_branches(
    *,
    repo_root: Path,
    trunk_ref: str = "origin/main",
    branch_prefixes: tuple[str, ...] = ("chat/", "feat/"),
    current_branch: str | None = None,
    dry_run: bool = False,
    do_fetch: bool = True,
) -> dict:
    """Delete local branches fully delivered into the trunk that have NO checked-out worktree.

    The worktree cleanup path deletes a branch only as a side effect of removing its worktree; merged
    branches whose worktree was already removed (the common case after a PR merge or
    ``deliver_worktree.py``) never get cleaned. This is that missing sweep.

    Hard safety envelope — a branch is deleted ONLY when ALL hold:
      * it matches an enabled prefix (default ``chat/``, ``feat/``);
      * it is NOT protected (``main``/``master``/``release``) and NOT the current branch;
      * it has NO checked-out worktree (checked-out branches are handled by worktree cleanup);
      * its exact tip is ancestor-contained in ``trunk_ref`` (delivered → zero committed work lost).
    Never deletes anything unmerged. Fail-soft, never raises; returns a structured report.
    """
    report: dict = {"scanned": 0, "deleted": [], "skipped": [], "dry_run": dry_run, "status": "ok"}
    repo_root = repo_root.resolve()

    if do_fetch:
        _git("fetch", "origin", "main", "--quiet", cwd=repo_root)  # best-effort

    rc_wt, porcelain = _git("worktree", "list", "--porcelain", cwd=repo_root)
    worktree_branches = _worktree_branches(porcelain) if rc_wt == 0 else set()

    if current_branch is None:
        rc_cur, cur = _git("rev-parse", "--abbrev-ref", "HEAD", cwd=repo_root)
        current_branch = cur if rc_cur == 0 else ""

    rc, listing = _git("for-each-ref", "--format=%(refname:short)", "refs/heads/", cwd=repo_root)
    if rc != 0:
        report["status"] = "no_branches"
        return report

    for branch in (b.strip() for b in listing.splitlines() if b.strip()):
        report["scanned"] += 1

        def skip(reason: str) -> None:
            report["skipped"].append({"branch": branch, "reason": reason})

        if _matched_prefix(branch, branch_prefixes) is None or branch in PROTECTED:
            skip("not_reap_prefix")
            continue
        if branch == current_branch:
            skip("current_branch")
            continue
        if branch in worktree_branches:
            skip("has_worktree")  # owned by worktree cleanup
            continue
        if not _is_ancestor(branch, trunk_ref, repo_root=repo_root):
            skip("not_merged_into_trunk")
            continue
        if dry_run:
            report["deleted"].append({"branch": branch, "dry_run": True})
            continue
        # -d is the safe form; we already proved exact ancestry containment.
        rc_d, _ = _git("branch", "-d", branch, cwd=repo_root)
        if rc_d == 0:
            report["deleted"].append({"branch": branch})
        else:
            skip("branch_delete_failed")

    return report


def _emit_context(message: str) -> None:
    sys.stdout.write(
        json.dumps(
            {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": message}}
        )
    )


def main(argv: list[str] | None = None) -> int:
    # A SessionStart invocation has no argv flags and pipes a JSON payload on stdin. Hook mode is
    # intentionally non-mutating: cleanup belongs to explicit CLI runs.
    cli = bool(argv) or len(sys.argv) > 1
    if not cli:
        try:
            sys.stdin.read()
        except OSError:
            pass
        return 0

    dry_run = True
    min_age_seconds = _min_age_seconds()
    prune_branches = _prune_branches_enabled()
    ap = argparse.ArgumentParser(
        description="Report or delete delivered local chat/feat worktrees + local branches."
    )
    ap.add_argument("--dry-run", action="store_true", help="report, delete nothing (default)")
    ap.add_argument(
        "--delete-merged",
        action="store_true",
        help="delete delivered+clean local worktrees/branches after safety checks",
    )
    ap.add_argument("--no-branches", action="store_true", help="skip the standalone branch sweep")
    ap.add_argument("--min-age-minutes", type=int, default=None, help="grace window override")
    args = ap.parse_args(argv)
    if args.delete_merged:
        dry_run = False
    if args.dry_run:
        dry_run = True
    if args.no_branches:
        prune_branches = False
    if args.min_age_minutes is not None:
        min_age_seconds = max(0, args.min_age_minutes) * 60

    if _bypass():
        return 0

    # Anchor to the primary working tree so the sweep is correct whether invoked from the primary
    # (SessionStart) or from inside a linked worktree (manual CLI). current_worktree = the session's
    # own worktree, which is never reaped.
    primary = _primary_worktree(REPO_ROOT)
    current = _cwd_toplevel(Path.cwd())

    messages: list[str] = []

    report = reap_merged_chat_worktrees(
        repo_root=primary,
        trunk_ref=_trunk_ref(),
        current_worktree=current,
        dry_run=dry_run,
        min_age_seconds=min_age_seconds,
        reap_branch_prefixes=_reap_prefixes(),
        allow_detached=_reap_detached_enabled(),
    )
    reaped = report.get("reaped") or []
    if reaped:
        verb = "would reap" if report.get("dry_run") else "reaped"
        lines = "\n".join(f"  - {r.get('branch') or r.get('label')}  ({r['path']})" for r in reaped)
        messages.append(
            f"worktree-merge-cleanup: {verb} {len(reaped)} merged+clean worktree(s):\n{lines}\n"
            f"(branches delivered into the trunk; no committed work lost)."
        )

    if prune_branches:
        breport = prune_merged_branches(
            repo_root=primary,
            trunk_ref=_trunk_ref(),
            branch_prefixes=_prune_branch_prefixes(),
            dry_run=dry_run,
        )
        deleted = breport.get("deleted") or []
        if deleted:
            verb = "would delete" if breport.get("dry_run") else "deleted"
            lines = "\n".join(f"  - {d['branch']}" for d in deleted)
            messages.append(
                f"merged-branch-prune: {verb} {len(deleted)} delivered local branch(es) "
                f"with no worktree:\n{lines}\n(fully delivered into the trunk; no committed work lost)."
            )

    if messages:
        msg = "\n\n".join(messages)
        sys.stderr.write("[HOOK] " + msg + "\n")
        if cli:
            sys.stdout.write(msg + "\n")
        else:
            _emit_context(msg)
    elif cli:
        mode = "dry-run" if dry_run else "delete"
        sys.stdout.write(f"worktree cleanup ({mode}): nothing to reap or prune.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
