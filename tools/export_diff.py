"""Utility for exporting consolidated git diffs.

This script captures a deterministic diff between a configurable base
reference and the current HEAD (or another ref) and saves it to disk so it
can be uploaded to review systems such as ChatGPT.
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import Optional


def _run_git_command(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        check=False,
        capture_output=True,
        text=True,
    )


def _ref_exists(ref: str) -> bool:
    result = _run_git_command("rev-parse", "--verify", ref)
    return result.returncode == 0


def _auto_base_ref() -> str:
    for candidate in ("main", "origin/main", "master", "origin/master"):
        if _ref_exists(candidate):
            return candidate
    # Fallback to the immediate parent commit; `HEAD^` will fail with a clear
    # error message later if this is the repository's first commit.
    return "HEAD^"


def _build_diff_range(base: str, head: str, mode: str) -> list[str]:
    if mode == "triple-dot":
        return [f"{base}...{head}"]
    if mode == "two-dot":
        return [f"{base}", head]
    raise ValueError(f"Unsupported diff mode: {mode}")


def export_diff(
    *,
    output_path: Path,
    base_ref: Optional[str],
    head_ref: str,
    mode: str,
    include_uncommitted: bool,
) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    if not output_path.is_absolute():
        output_path = repo_root / output_path
    resolved_base = base_ref or _auto_base_ref()
    if not _ref_exists(resolved_base):
        raise SystemExit(
            f"Unable to resolve base ref '{resolved_base}'. Please provide a valid --base."
        )

    if not _ref_exists(head_ref):
        raise SystemExit(f"Unable to resolve head ref '{head_ref}'.")

    diff_args = ["diff", *_build_diff_range(resolved_base, head_ref, mode)]
    diff_proc = _run_git_command(*diff_args)
    if diff_proc.returncode != 0:
        raise SystemExit(diff_proc.stderr.strip() or "git diff failed")

    diff_segments = [diff_proc.stdout]

    if include_uncommitted:
        worktree_proc = _run_git_command("diff", head_ref)
        if worktree_proc.returncode != 0:
            raise SystemExit(worktree_proc.stderr.strip() or "git diff failed")
        if worktree_proc.stdout.strip():
            diff_segments.append("\n# ---- Worktree vs HEAD ----\n")
            diff_segments.append(worktree_proc.stdout)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("".join(diff_segments))

    try:
        rel_output = output_path.relative_to(repo_root)
    except ValueError:
        rel_output = output_path
    print(
        f"Wrote consolidated diff between '{resolved_base}' and '{head_ref}' to {rel_output}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("exports/lic_refactor.diff"),
        help="Path where the diff should be written (default: exports/lic_refactor.diff)",
    )
    parser.add_argument(
        "--base",
        type=str,
        default=None,
        help="Base git ref to diff against. Defaults to auto-detect (main/origin/main/HEAD^).",
    )
    parser.add_argument(
        "--head",
        type=str,
        default="HEAD",
        help="Head git ref to diff from (default: HEAD)",
    )
    parser.add_argument(
        "--mode",
        choices=("triple-dot", "two-dot"),
        default="triple-dot",
        help="Diff range mode: triple-dot (merge-base) or two-dot (range).",
    )
    parser.add_argument(
        "--include-uncommitted",
        action="store_true",
        help="Append unstaged worktree changes vs HEAD to the diff output.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    export_diff(
        output_path=args.output,
        base_ref=args.base,
        head_ref=args.head,
        mode=args.mode,
        include_uncommitted=args.include_uncommitted,
    )
