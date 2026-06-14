"""deliver-worktree — the standard, safe "deliver this worktree" path.

Item #5 of the worktree-lifecycle streamline. Codifies the delivery flow proven in
project memory ``safe-merge-under-concurrent-primary``: in a multi-worktree repo the
**primary checkout often has live concurrent work and ``main`` moves mid-task**, so a
feature is delivered *from its own worktree* by rebasing on the trunk, retesting, then
pushing/PR — **never** by merging in the primary checkout.

Steps (in order; any failure stops before push):
  1. Refuse to run in the primary checkout / on a protected branch.
  2. Require a clean tree (commit your work first — uncommitted work is never pushed).
  3. ``git fetch origin <trunk>``.
  4. ``git rebase origin/<trunk>`` (abort + guidance on conflict).
  5. Optional ``--test "<cmd>"`` retest — push is skipped if it fails.
  6. Deliver: ``--mode pr`` (default; ``gh pr create``) or ``--mode push``
     (``git push origin HEAD:<trunk>`` — direct-to-trunk, opt-in).

``--dry-run`` prints the plan and the trunk-divergence count without mutating anything.
Never force-pushes. Stdlib only; explicit subprocess timeouts.

Examples:
    python tools/git/deliver_worktree.py --dry-run
    python tools/git/deliver_worktree.py --test "python -m pytest tests/unit/tools/git -q"
    python tools/git/deliver_worktree.py --mode push --test "python -m pytest -q tests/unit/tools/git"
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

PROTECTED = ("main", "master", "release")


def _git(*args: str, cwd: Path) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, "", str(exc)
    return proc.returncode, (proc.stdout or "").strip(), (proc.stderr or "").strip()


def _toplevel(start: Path) -> Path | None:
    rc, out, _ = _git("rev-parse", "--show-toplevel", cwd=start)
    return Path(out) if rc == 0 and out else None


def _branch(cwd: Path) -> str:
    rc, out, _ = _git("rev-parse", "--abbrev-ref", "HEAD", cwd=cwd)
    return out if rc == 0 else ""


def _is_primary(worktree: Path) -> bool:
    """True if ``worktree`` is the main working tree (not a linked worktree)."""
    rc, common, _ = _git("rev-parse", "--git-common-dir", cwd=worktree)
    rc2, gitdir, _ = _git("rev-parse", "--git-dir", cwd=worktree)
    if rc != 0 or rc2 != 0:
        return False
    # In a linked worktree, --git-dir points inside <common>/worktrees/<name>; in the
    # primary, --git-dir == --git-common-dir (both ``.git``).
    return Path(common).resolve() == Path(gitdir).resolve()


def _fail(msg: str) -> int:
    sys.stderr.write(f"deliver-worktree: {msg}\n")
    return 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Safely deliver a feature worktree to the trunk.")
    ap.add_argument("--worktree", default=None, help="worktree path (default: cwd)")
    ap.add_argument("--trunk", default="main", help="trunk branch name (default: main)")
    ap.add_argument("--mode", choices=("pr", "push"), default="pr", help="delivery mode")
    ap.add_argument("--test", default=None, help="retest command run before delivery")
    ap.add_argument("--test-timeout", type=int, default=1800, help="retest timeout seconds")
    ap.add_argument("--dry-run", action="store_true", help="print plan + divergence; no mutation")
    args = ap.parse_args(argv)

    start = Path(args.worktree).resolve() if args.worktree else Path.cwd()
    top = _toplevel(start)
    if top is None:
        return _fail(f"{start} is not inside a git repository.")

    branch = _branch(top)
    if not branch or branch == "HEAD":
        return _fail("detached HEAD — check out a feature branch before delivering.")
    if branch in PROTECTED:
        return _fail(
            f"refusing to deliver from protected branch '{branch}'. Run this from the feature "
            "worktree, never the primary checkout on the trunk."
        )
    if _is_primary(top):
        return _fail(
            "refusing to run in the primary checkout. Deliver from the feature worktree "
            "(the primary often carries concurrent uncommitted work)."
        )

    trunk_branch = args.trunk
    trunk_ref = f"origin/{trunk_branch}"

    print(f"deliver-worktree: branch '{branch}' → {trunk_ref}  (mode={args.mode})")
    print(f"  worktree: {top}")

    # Divergence (best-effort, read-only).
    _git("fetch", "origin", trunk_branch, "--quiet", cwd=top)
    rc, behind, _ = _git("rev-list", "--count", f"HEAD..{trunk_ref}", cwd=top)
    if rc == 0 and behind.isdigit():
        print(f"  {trunk_ref} is {behind} commit(s) ahead of this branch.")

    if args.dry_run:
        print("  [dry-run] would: require-clean → rebase → "
              + (f"retest({args.test}) → " if args.test else "")
              + ("open PR" if args.mode == "pr" else f"push HEAD:{trunk_branch}"))
        return 0

    # 2. Clean tree.
    rc, st, _ = _git("status", "--porcelain", cwd=top)
    if rc != 0:
        return _fail("could not read git status.")
    if st.strip():
        return _fail("working tree is dirty — commit your work before delivering (nothing is auto-pushed).")

    # 3. Fetch (already fetched above; harmless to ensure).
    # 4. Rebase.
    print(f"  rebasing onto {trunk_ref} …")
    rc, out, err = _git("rebase", trunk_ref, cwd=top)
    if rc != 0:
        _git("rebase", "--abort", cwd=top)
        return _fail(
            "rebase onto trunk hit conflicts and was aborted. Resolve manually:\n"
            f"    cd {top} && git rebase {trunk_ref}\n"
            f"  ({err or out})"
        )

    # 5. Optional retest.
    if args.test:
        print(f"  retesting: {args.test}")
        try:
            tproc = subprocess.run(
                args.test,
                cwd=str(top),
                shell=True,  # user-provided test command
                timeout=args.test_timeout,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return _fail(f"retest timed out after {args.test_timeout}s — not delivering.")
        if tproc.returncode != 0:
            return _fail(f"retest failed (exit {tproc.returncode}) — not delivering.")
        print("  retest passed.")

    # 6. Deliver.
    if args.mode == "push":
        print(f"  pushing HEAD → {trunk_branch} …")
        rc, out, err = _git("push", "origin", f"HEAD:{trunk_branch}", cwd=top)
        if rc != 0:
            return _fail(f"push to {trunk_branch} rejected: {err or out}\n  (try --mode pr instead.)")
        print(f"deliver-worktree: pushed '{branch}' → {trunk_branch}. ✓")
        return 0

    # PR mode.
    print(f"  pushing branch '{branch}' and opening a PR …")
    rc, out, err = _git("push", "-u", "origin", branch, cwd=top)
    if rc != 0:
        return _fail(f"push of '{branch}' failed: {err or out}")
    if not _have_gh():
        print(
            "  branch pushed. `gh` not found — open the PR manually:\n"
            f"    https://github.com/  (compare {branch} → {trunk_branch})"
        )
        return 0
    try:
        pr = subprocess.run(
            ["gh", "pr", "create", "--fill", "--base", trunk_branch, "--head", branch],
            cwd=str(top),
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return _fail(f"gh pr create failed to launch: {exc}")
    sys.stdout.write(pr.stdout or "")
    sys.stderr.write(pr.stderr or "")
    if pr.returncode != 0:
        return _fail("gh pr create returned non-zero — open the PR manually.")
    print(f"deliver-worktree: PR opened for '{branch}' → {trunk_branch}. ✓")
    return 0


def _have_gh() -> bool:
    try:
        subprocess.run(["gh", "--version"], capture_output=True, timeout=15, check=False)
        return True
    except (OSError, subprocess.TimeoutExpired):
        return False


if __name__ == "__main__":
    raise SystemExit(main())
