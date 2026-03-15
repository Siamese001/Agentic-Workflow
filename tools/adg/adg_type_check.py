"""
ADG-scoped incremental type checker — Accelerator #4.

Given a set of changed files, queries ADG for their import blast radius
(files that directly or transitively import them) and runs mypy only on that
surface. This keeps type-checking fast even in large codebases.

Fail-closed: raises RuntimeError if Redis unavailable. NO filesystem fallback.

Usage (CLI):
    python tools/adg/adg_type_check.py <file> [<file> ...]
    python tools/adg/adg_type_check.py --from-diff
    python tools/adg/adg_type_check.py --from-diff --depth 2
    python tools/adg/adg_type_check.py --from-diff --strict
    python tools/adg/adg_type_check.py --from-diff --dry-run   # show scope only
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import redis

from tools.adg.adg_redis_query import ADGRedisClient


@dataclass
class MypyResult:
    exit_code: int
    stdout: str
    stderr: str
    scoped_files: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.exit_code == 0

    @property
    def error_lines(self) -> list[str]:
        return [ln for ln in self.stdout.splitlines() if ": error:" in ln]

    @property
    def error_count(self) -> int:
        return len(self.error_lines)


class ADGTypeChecker:
    """ADG-scoped incremental type checker.

    1. Resolves the import blast radius from ADG (fan-in on 'imports' edges).
    2. Runs mypy on exactly those files — not the whole repo.

    Fail-closed: all Redis errors propagate (no silent swallowing).
    """

    def __init__(
        self,
        client: ADGRedisClient | None = None,
        repo_root: Path | None = None,
    ) -> None:
        self._adg = client or ADGRedisClient()
        self._root = repo_root or ROOT

    def get_blast_radius(
        self,
        changed_files: Iterable[str],
        depth: int = 1,
    ) -> list[str]:
        """Return all files in the import fan-in blast radius of changed_files.

        For each changed file at each depth level:
          1. adg:nodes:by_file:<path>      -> node IDs
          2. adg:edge:in:<nid>:imports     -> importer node IDs
          3. adg:node:<importer>.resolved_path -> importer file path

        Args:
            changed_files: Repo-relative production file paths.
            depth: Blast radius depth (0 = changed files only, 1 = direct importers,
                   2 = importers of importers, etc.).

        Returns:
            Sorted unique file paths including the original changed files.

        Raises:
            ValueError: if depth < 0.
            RuntimeError / redis.ConnectionError: if Redis unavailable.
        """
        if depth < 0:
            raise ValueError(f"depth must be >= 0, got {depth}")

        frontier: set[str] = set()
        for p in changed_files:
            frontier.add(p.replace("\\", "/"))

        all_files: set[str] = set(frontier)

        for _ in range(depth):
            next_frontier: set[str] = set()
            for path in frontier:
                node_ids = self._adg.nodes_in_file(path)
                for nid in node_ids:
                    importer_nids = self._adg.fan_in(nid, "imports")
                    for inid in importer_nids:
                        node = self._adg.get_node(inid)
                        rp = node.get("resolved_path", "")
                        if rp and rp.endswith(".py") and rp not in all_files:
                            next_frontier.add(rp)
            all_files |= next_frontier
            frontier = next_frontier
            if not frontier:
                break

        return sorted(all_files)

    def run_mypy(
        self,
        files: list[str],
        strict: bool = False,
    ) -> MypyResult:
        """Run mypy on the given list of files.

        Args:
            files: Repo-relative file paths to type-check.
            strict: If True, pass --strict to mypy.

        Returns:
            MypyResult with exit_code, stdout, stderr, scoped_files.

        Raises:
            RuntimeError: if mypy is not installed or execution times out.
        """
        if not files:
            return MypyResult(exit_code=0, stdout="", stderr="", scoped_files=[])

        cmd = [sys.executable, "-m", "mypy"]
        if strict:
            cmd.append("--strict")
        cmd.extend(files)

        try:
            result = subprocess.run(
                cmd,
                cwd=str(self._root),
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=120,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(f"mypy timed out after 120s: {exc}") from exc
        except FileNotFoundError as exc:
            raise RuntimeError(f"mypy not found — install with: pip install mypy. Error: {exc}") from exc

        return MypyResult(
            exit_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            scoped_files=list(files),
        )

    def check(
        self,
        changed_files: Iterable[str],
        depth: int = 1,
        strict: bool = False,
    ) -> MypyResult:
        """Full incremental type check: compute blast radius, then run mypy.

        Args:
            changed_files: Production files that changed.
            depth: Blast radius depth (1 = direct importers only).
            strict: If True, pass --strict to mypy.

        Returns:
            MypyResult — passed=True means no type errors found.
        """
        blast = self.get_blast_radius(changed_files, depth=depth)
        return self.run_mypy(blast, strict=strict)


def _git_changed_files(staged: bool = False, repo_root: Path | None = None) -> list[str]:
    """Return changed Python files from git diff.

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
        prog="adg_type_check",
        description="ADG-scoped incremental type checker: blast radius + mypy.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        metavar="FILE",
        help="Production file paths to type-check (with their import blast radius)",
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
        "--depth",
        type=int,
        default=1,
        metavar="N",
        help="Blast radius depth (default: 1 = direct importers only)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Pass --strict to mypy",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the scoped file list without running mypy",
    )
    args = parser.parse_args()

    use_diff = args.from_diff or args.staged
    if not args.files and not use_diff:
        parser.error("Provide FILE arguments or --from-diff / --staged")

    try:
        adg = ADGRedisClient()
        adg.ping()
    except (RuntimeError, redis.ConnectionError) as exc:
        print(f"ERROR: ADG Redis unavailable — {exc}", file=sys.stderr)
        sys.exit(1)

    checker = ADGTypeChecker(client=adg)

    changed: list[str] = list(args.files)
    if use_diff:
        try:
            changed.extend(_git_changed_files(staged=args.staged))
        except RuntimeError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            sys.exit(1)

    try:
        scope = checker.get_blast_radius(changed, depth=args.depth)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Blast radius (depth={args.depth}): {len(scope)} file(s)")
    for f in scope:
        print(f"  {f}")

    if args.dry_run:
        sys.exit(0)

    try:
        result = checker.run_mypy(scope, strict=args.strict)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)

    if result.passed:
        print(f"\nmypy: OK — {len(scope)} file(s) checked")
    else:
        print(f"\nmypy: FAIL — {result.error_count} error(s) in {len(scope)} file(s)")
    sys.exit(result.exit_code)


if __name__ == "__main__":
    _cli()
