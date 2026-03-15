"""
ADG-backed test selector — Accelerator #5.

Given a list of changed production files, queries ADG ``covers`` edges to return
the exact test file paths that cover those files.

Fail-closed: raises if Redis is unavailable. NO filesystem fallback. NO grep.

Usage (CLI):
    python tools/adg/adg_test_selector.py <file> [<file> ...]
    python tools/adg/adg_test_selector.py --from-diff
    python tools/adg/adg_test_selector.py --staged
    python tools/adg/adg_test_selector.py --from-diff --pytest-args
    python tools/adg/adg_test_selector.py --from-diff --show-gaps
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.adg.adg_redis_query import ADGRedisClient


class ADGTestSelector:
    """Select test files that cover a given set of production files via ADG covers edges.

    Query flow per production file:
      1. adg:nodes:by_file:<path>      -> node IDs for that file
      2. adg:edge:in:<nid>:covers      -> test node IDs (fan-in on 'covers')
      3. adg:node:<tnid>.resolved_path -> test file path (must start with 'tests/')

    Fail-closed: all Redis errors propagate as-is (no silent swallowing).
    """

    def __init__(self, client: ADGRedisClient | None = None) -> None:
        self._adg = client or ADGRedisClient()

    def select_tests(self, changed_files: Iterable[str]) -> list[str]:
        """Return sorted unique test file paths covering any file in changed_files.

        Args:
            changed_files: Iterable of repo-relative production file paths.

        Returns:
            Sorted list of test file paths (all start with 'tests/').

        Raises:
            redis.ConnectionError / RuntimeError: if Redis unavailable or ADG not loaded.
        """
        test_paths: set[str] = set()
        for path in changed_files:
            path = path.replace("\\", "/")
            node_ids = self._adg.nodes_in_file(path)
            for nid in node_ids:
                cover_nids = self._adg.fan_in(nid, "covers")
                for tnid in cover_nids:
                    node = self._adg.get_node(tnid)
                    rp = node.get("resolved_path", "")
                    if rp and rp.startswith("tests/"):
                        test_paths.add(rp)
        return sorted(test_paths)

    def coverage_gaps(self, changed_files: Iterable[str]) -> list[str]:
        """Return production files that have NO covers edges in ADG.

        A gap means zero test coverage is recorded — these need new tests.

        Args:
            changed_files: Iterable of repo-relative production file paths.

        Returns:
            Sorted list of production file paths with no ADG coverage.
        """
        gaps: list[str] = []
        for path in changed_files:
            path = path.replace("\\", "/")
            node_ids = self._adg.nodes_in_file(path)
            has_cover = False
            for nid in node_ids:
                if self._adg.fan_in(nid, "covers"):
                    has_cover = True
                    break
            if not has_cover:
                gaps.append(path)
        return sorted(gaps)


def _git_changed_files(staged: bool = False, repo_root: Path | None = None) -> list[str]:
    """Return changed Python file paths from git diff.

    Args:
        staged: If True, use --cached (staged files). Otherwise, HEAD vs working tree.
        repo_root: Repository root; defaults to ROOT.

    Raises:
        RuntimeError: if git command fails or times out.
    """
    root = repo_root or ROOT
    cmd = ["git", "diff", "--name-only", "--diff-filter=ACMRT"]
    if staged:
        cmd.append("--cached")
    else:
        cmd.append("HEAD")
    try:
        result = subprocess.run(
            cmd,
            cwd=str(root),
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"git diff timed out: {exc}") from exc
    if result.returncode != 0:
        raise RuntimeError(f"git diff failed: {result.stderr.strip()}")
    return [f for f in result.stdout.splitlines() if f.endswith(".py")]


def _cli() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        prog="adg_test_selector",
        description="Select tests covering changed production files via ADG covers edges.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        metavar="FILE",
        help="Production file paths to find covering tests for",
    )
    parser.add_argument(
        "--from-diff",
        action="store_true",
        help="Use 'git diff HEAD' to determine changed files",
    )
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Use 'git diff --cached' (staged files only) — implies --from-diff",
    )
    parser.add_argument(
        "--pytest-args",
        action="store_true",
        help="Print space-separated test paths suitable for passing directly to pytest",
    )
    parser.add_argument(
        "--show-gaps",
        action="store_true",
        help="Also print production files with no ADG covers edges (coverage gaps)",
    )
    args = parser.parse_args()

    use_diff = args.from_diff or args.staged
    if not args.files and not use_diff:
        parser.error("Provide FILE arguments or --from-diff / --staged")

    try:
        adg = ADGRedisClient()
        adg.ping()
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    selector = ADGTestSelector(client=adg)

    changed: list[str] = list(args.files)
    if use_diff:
        try:
            changed.extend(_git_changed_files(staged=args.staged))
        except RuntimeError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            sys.exit(1)

    tests = selector.select_tests(changed)
    gaps = selector.coverage_gaps(changed) if args.show_gaps else []

    if args.pytest_args:
        print(" ".join(tests) if tests else "")
    else:
        if tests:
            print(f"{len(tests)} covering test(s):")
            for t in tests:
                print(f"  {t}")
        else:
            print("No covering tests found in ADG for the given files.")

    if args.show_gaps:
        if gaps:
            print(f"\n{len(gaps)} coverage gap(s) — no ADG covers edges:")
            for g in gaps:
                print(f"  GAP: {g}")
        else:
            print("\nNo coverage gaps — all changed files have ADG covers edges.")


if __name__ == "__main__":
    _cli()
