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
import dis
import pathlib
import sys
import trace
import types
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
    """Return executable line numbers for *path* based on bytecode analysis."""

    source = path.read_text(encoding="utf-8")
    try:
        module_code = compile(source, str(path), "exec")
    except SyntaxError:
        return set()

    code_lines: Set[int] = set()

    def _visit(code_obj: types.CodeType) -> None:
        for _, lineno in dis.findlinestarts(code_obj):
            if lineno:
                code_lines.add(lineno)
        for const in code_obj.co_consts:
            if isinstance(const, types.CodeType):
                _visit(const)

    _visit(module_code)
    return code_lines


def _collect_coverage(
    counts: dict[Tuple[str, int], int]
) -> Tuple[int, int, list[tuple[pathlib.Path, int, int]]]:
    total_lines = 0
    executed_lines = 0
    per_file: list[tuple[pathlib.Path, int, int]] = []
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
        executed_count = len(lines & executed)
        executed_lines += executed_count
        per_file.append((file_path, executed_count, len(lines)))

    return executed_lines, total_lines, per_file


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
    parser.add_argument(
        "--report-missing",
        action="store_true",
        help="Print per-file coverage breakdown to stderr",
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

    executed, total, per_file = _collect_coverage(tracer.results().counts)
    coverage_pct = (executed / total * 100.0) if total else 100.0

    print(f"Coverage for src/lic_agentic: {coverage_pct:.2f}% ({executed}/{total} lines)")
    if args.report_missing:
        for file_path, executed_lines, total_lines in sorted(
            per_file,
            key=lambda entry: (entry[1] / entry[2] if entry[2] else 1.0),
        ):
            percentage = (executed_lines / total_lines * 100.0) if total_lines else 100.0
            print(
                f"  {file_path.relative_to(ROOT)}: {percentage:5.1f}% ({executed_lines}/{total_lines})",
                file=sys.stderr,
            )
    if coverage_pct < args.threshold:
        print(
            f"ERROR: coverage {coverage_pct:.2f}% is below the required {args.threshold:.2f}%",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
