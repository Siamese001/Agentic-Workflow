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
