"""Fail-fast Python syntax checker for CI.

By default this checks Python files changed since the base branch. Passing
explicit file paths checks only those paths. Use ``--all`` for a full repo scan.
"""

from __future__ import annotations

import argparse
import py_compile
import subprocess  # noqa: S404 -- bounded git subprocess calls for CI file selection
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]

_SCAN_DIRS = (
    "agentic_core",
    "apps_shared",
    "apps_lic",
    "apps_rg",
    "apps_exec",
    "apps_eval",
    "apps_research",
    "apps_underwriting_ai",
    "ops_scripts",
    "tools",
    "system_learning",
    "tests",
)

_SKIP_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    "__pycache__",
    "_archived_obsolete",
    "archive",
    "archives",
    "build",
    "dist",
    "lib",
    "lib64",
    "node_modules",
}


def _is_scannable(path: Path) -> bool:
    return path.suffix == ".py" and not any(part in _SKIP_PARTS for part in path.parts)


def _git_lines(args: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=_ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _changed_files(base_ref: str) -> list[Path]:
    candidates = [
        [f"{base_ref}...HEAD"],
        [f"origin/{base_ref}...HEAD"],
        ["HEAD~1...HEAD"],
    ]
    names: list[str] = []
    for revspec in candidates:
        names = _git_lines(["diff", "--name-only", "--diff-filter=ACMR", *revspec])
        if names:
            break
    return [(_ROOT / name).resolve() for name in names if _is_scannable(Path(name))]


def _all_files() -> list[Path]:
    files: list[Path] = []
    for rel in _SCAN_DIRS:
        root = _ROOT / rel
        if root.is_dir():
            files.extend(path.resolve() for path in root.rglob("*.py") if _is_scannable(path))
    return files


def _explicit_files(values: list[str]) -> list[Path]:
    files: list[Path] = []
    for value in values:
        path = (_ROOT / value).resolve()
        if path.is_file() and _is_scannable(path):
            files.append(path)
    return files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check Python files with py_compile before heavier CI gates.")
    parser.add_argument("files", nargs="*", help="Optional explicit Python files to compile")
    parser.add_argument("--all", action="store_true", help="Compile all repo Python files in configured scan dirs")
    parser.add_argument("--base-ref", default="main", help="Base branch/ref for changed-file mode")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    if args.files:
        paths = _explicit_files(args.files)
    elif args.all:
        paths = _all_files()
    else:
        paths = _changed_files(args.base_ref)

    if not paths:
        if args.verbose:
            print("[check_python_syntax] no Python files to compile")
        return 0

    failures: list[tuple[Path, str]] = []
    for path in sorted(set(paths)):
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            failures.append((path, exc.msg))

    if failures:
        print(f"[check_python_syntax] {len(failures)} syntax failure(s):")
        for path, message in failures:
            print(f"  {path.relative_to(_ROOT)}")
            print(message.rstrip())
        return 1

    if args.verbose:
        print(f"[check_python_syntax] OK: compiled {len(set(paths))} Python file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
