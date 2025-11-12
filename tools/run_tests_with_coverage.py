#!/usr/bin/env python3
"""Run pytest under the stdlib trace module and enforce a coverage threshold.

This script exists so we can enforce the repository's 90%% coverage gate even in
restricted environments where third-party coverage plugins (e.g. pytest-cov)
are not available.  It executes pytest with the builtin ``trace`` module to
collect line execution counts, computes the aggregate coverage for the
``src/lic_agentic`` package, and exits with a non-zero status code if coverage
falls below the requested threshold.
"""
from __future__ import annotations

import argparse
import pathlib
import sys
import trace
from typing import Iterable, Set, Tuple

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TARGET_DIR = ROOT / "src" / "lic_agentic"
DEFAULT_TEST_TARGETS = [
    "tests/unit",
    "tests/integration",
    "tests/e2e",
    "tests/regression",
]


def _iter_code_lines(path: pathlib.Path) -> Set[int]:
    """Return the line numbers that should count toward coverage for *path*."""
    code_lines: Set[int] = set()
    with path.open("r", encoding="utf-8") as handle:
        for lineno, raw_line in enumerate(handle, start=1):
            stripped = raw_line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            code_lines.add(lineno)
    return code_lines


def _collect_coverage(counts: dict[Tuple[str, int], int]) -> Tuple[int, int]:
    total_lines = 0
    executed_lines = 0
    normalized_counts: dict[pathlib.Path, Set[int]] = {}

    for (filename, lineno), hit_count in counts.items():
        if hit_count <= 0:
            continue
        file_path = pathlib.Path(filename).resolve()
        if TARGET_DIR not in file_path.parents and file_path != TARGET_DIR:
            continue
        normalized_counts.setdefault(file_path, set()).add(lineno)

    for file_path in TARGET_DIR.rglob("*.py"):
        lines = _iter_code_lines(file_path)
        if not lines:
            continue
        total_lines += len(lines)
        executed = normalized_counts.get(file_path.resolve(), set())
        executed_lines += len(lines & executed)

    return executed_lines, total_lines


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run pytest with stdlib coverage enforcement")
    parser.add_argument(
        "--threshold",
        type=float,
        default=90.0,
        help="Required coverage percentage for src/lic_agentic (default: 90.0)",
    )
    parser.add_argument(
        "pytest_args",
        nargs=argparse.REMAINDER,
        help="Arguments forwarded to pytest (prefix with '--' to separate)",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    tracer = trace.Trace(count=True, trace=False, ignoredirs=[sys.prefix, str(ROOT / "tests")])
    pytest_args = list(args.pytest_args or [])
    if pytest_args and pytest_args[0] == "--":
        pytest_args = pytest_args[1:]
    if not pytest_args:
        pytest_args = DEFAULT_TEST_TARGETS

    exit_code = tracer.runfunc(pytest.main, pytest_args)

    if exit_code != 0:
        return exit_code

    executed, total = _collect_coverage(tracer.results().counts)
    coverage_pct = (executed / total * 100.0) if total else 100.0

    print(f"Coverage for src/lic_agentic: {coverage_pct:.2f}% ({executed}/{total} lines)")
    if coverage_pct < args.threshold:
        print(
            f"ERROR: coverage {coverage_pct:.2f}% is below the required {args.threshold:.2f}%",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
