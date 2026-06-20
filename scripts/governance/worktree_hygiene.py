"""Shared worktree hygiene helpers for Codex governance checks."""

from __future__ import annotations

import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

PROTECTED_BRANCHES: tuple[str, ...] = ("main", "master", "release")


@dataclass(frozen=True)
class WorktreeHygieneIssue:
    branch: str
    worktree: Path
    dirty_files: tuple[str, ...]


@dataclass(frozen=True)
class SingleMainWorktreeIssue:
    code: str
    detail: str


def run_git(*args: str, cwd: Path) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, "", str(exc)
    return proc.returncode, (proc.stdout or "").strip(), (proc.stderr or "").strip()


def parse_worktrees(porcelain: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    cur: dict[str, str] = {}
    for line in porcelain.splitlines() + [""]:
        if not line.strip():
            if cur:
                rows.append(cur)
                cur = {}
            continue
        if line.startswith("worktree "):
            cur = {"path": line[len("worktree ") :].strip()}
        elif line.startswith("HEAD "):
            cur["head"] = line[len("HEAD ") :].strip()
        elif line.startswith("branch "):
            ref = line[len("branch ") :].strip()
            cur["branch"] = ref[len("refs/heads/") :] if ref.startswith("refs/heads/") else ref
        elif line == "detached":
            cur["branch"] = "DETACHED"
    return rows


def find_dirty_protected_worktrees(
    repo_root: Path,
    *,
    protected_branches: Sequence[str] = PROTECTED_BRANCHES,
    skip_paths: Sequence[Path] = (),
) -> list[WorktreeHygieneIssue]:
    """Return protected worktrees whose tracked or untracked state is dirty."""

    rc, porcelain, _ = run_git("worktree", "list", "--porcelain", cwd=repo_root)
    if rc != 0:
        return []

    skip = {Path(path).resolve() for path in skip_paths}
    issues: list[WorktreeHygieneIssue] = []
    for row in parse_worktrees(porcelain):
        branch = row.get("branch", "")
        if branch not in protected_branches:
            continue
        path_text = row.get("path", "")
        if not path_text:
            continue
        worktree = Path(path_text).resolve()
        if worktree in skip or not worktree.exists():
            continue
        rc_status, status, _ = run_git("status", "--short", cwd=worktree)
        if rc_status != 0 or not status.strip():
            continue
        issues.append(
            WorktreeHygieneIssue(
                branch=branch,
                worktree=worktree,
                dirty_files=tuple(line for line in status.splitlines() if line.strip()),
            )
        )
    return issues


def summarize_dirty_worktrees(
    issues: Sequence[WorktreeHygieneIssue],
    *,
    max_files_per_worktree: int = 5,
) -> str:
    if not issues:
        return ""
    lines: list[str] = []
    for issue in issues:
        files = list(issue.dirty_files)
        preview = ", ".join(files[:max_files_per_worktree])
        if len(files) > max_files_per_worktree:
            preview += f" (+{len(files) - max_files_per_worktree} more)"
        lines.append(f"- {issue.branch} @ {issue.worktree}: {preview}")
    return "\n".join(lines)


def verify_single_main_worktree(
    repo_root: Path,
    *,
    expected_path: Path | None = None,
    base_ref: str = "origin/main",
    fetch: bool = False,
) -> list[SingleMainWorktreeIssue]:
    """Return blockers when local closeout is not exactly one clean main worktree."""

    root = repo_root.resolve()
    expected = (expected_path or repo_root).resolve()
    issues: list[SingleMainWorktreeIssue] = []

    if fetch:
        rc_fetch, _, stderr = run_git("fetch", "origin", "--prune", cwd=root)
        if rc_fetch != 0:
            issues.append(SingleMainWorktreeIssue("fetch_failed", stderr))

    rc, porcelain, stderr = run_git("worktree", "list", "--porcelain", cwd=root)
    if rc != 0:
        return [*issues, SingleMainWorktreeIssue("worktree_list_failed", stderr)]

    worktrees = parse_worktrees(porcelain)
    if len(worktrees) != 1:
        issues.append(SingleMainWorktreeIssue("worktree_count", f"expected=1 actual={len(worktrees)}"))

    current = worktrees[0] if worktrees else {}
    path_text = current.get("path", "")
    actual_path = Path(path_text).resolve() if path_text else None
    if actual_path != expected:
        issues.append(
            SingleMainWorktreeIssue(
                "worktree_path",
                f"expected={expected} actual={actual_path or '<missing>'}",
            )
        )

    branch = current.get("branch", "")
    if branch != "main":
        issues.append(SingleMainWorktreeIssue("worktree_branch", f"expected=main actual={branch or '<missing>'}"))

    rc_status, status, status_err = run_git("status", "--short", "--branch", cwd=root)
    if rc_status != 0:
        issues.append(SingleMainWorktreeIssue("status_failed", status_err))
    else:
        dirty_rows = [line for line in status.splitlines() if line and not line.startswith("##")]
        if dirty_rows:
            issues.append(SingleMainWorktreeIssue("dirty_status", "\n".join(dirty_rows)))

    rc_diff, _, diff_err = run_git("diff", "--quiet", cwd=root)
    if rc_diff != 0:
        issues.append(SingleMainWorktreeIssue("unstaged_diff", diff_err or "git diff --quiet reported changes"))

    rc_cached, _, cached_err = run_git("diff", "--cached", "--quiet", cwd=root)
    if rc_cached != 0:
        issues.append(
            SingleMainWorktreeIssue("staged_diff", cached_err or "git diff --cached --quiet reported changes")
        )

    rc_head, head, head_err = run_git("rev-parse", "--verify", "HEAD", cwd=root)
    rc_base, base, base_err = run_git("rev-parse", "--verify", base_ref, cwd=root)
    if rc_head != 0:
        issues.append(SingleMainWorktreeIssue("head_missing", head_err))
    if rc_base != 0:
        issues.append(SingleMainWorktreeIssue("base_ref_missing", f"{base_ref}: {base_err}"))
    if rc_head == 0 and rc_base == 0 and head != base:
        issues.append(SingleMainWorktreeIssue("head_not_base_ref", f"HEAD={head} {base_ref}={base}"))

    rc_unmerged, unmerged, unmerged_err = run_git(
        "branch",
        "--no-merged",
        base_ref,
        "--format=%(refname:short)",
        cwd=root,
    )
    if rc_unmerged != 0:
        issues.append(SingleMainWorktreeIssue("unmerged_branch_check_failed", unmerged_err))
    elif unmerged.strip():
        issues.append(SingleMainWorktreeIssue("unmerged_branches", unmerged))

    return issues


def summarize_single_main_worktree_issues(issues: Sequence[SingleMainWorktreeIssue]) -> str:
    if not issues:
        return ""
    return "\n".join(f"- {issue.code}: {issue.detail}" for issue in issues)
