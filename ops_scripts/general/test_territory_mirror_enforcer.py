#!/usr/bin/env python3
"""Audit whether source files have mirrored tests in the expected territory.

The script can also move misplaced tests into their expected territory when
``--execute`` is supplied. It defaults to audit-only mode.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import shutil
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

try:
    from agentic_core.L0_routing.config.path_constants import (
        AGENTIC_CORE_DIR as _AGENTIC_CORE_DIR,
        APPS_LIC_DIR as _APPS_LIC_DIR,
        APPS_RG_DIR as _APPS_RG_DIR,
        APPS_SHARED_DIR as _APPS_SHARED_DIR,
        TESTS_DIR as _TESTS_DIR,
    )
except Exception:
    _AGENTIC_CORE_DIR = "agentic_core"
    _APPS_LIC_DIR = "apps_lic"
    _APPS_RG_DIR = "apps_rg"
    _APPS_SHARED_DIR = "apps_shared"
    _TESTS_DIR = "tests"


@dataclass(slots=True)
class SourceFile:
    path: str
    territory: str
    kind: str
    expected_test: str
    has_test: bool = False


@dataclass(slots=True)
class TestFile:
    path: str
    expected_source: str | None
    expected_test: str | None
    is_misplaced: bool = False
    is_orphan: bool = False


@dataclass(slots=True)
class MirrorAuditReport:
    project_root: str
    dry_run: bool
    execute: bool
    sources: int
    tests: int
    missing_tests: list[dict[str, Any]] = field(default_factory=list)
    misplaced_tests: list[dict[str, Any]] = field(default_factory=list)
    orphan_tests: list[dict[str, Any]] = field(default_factory=list)
    moved_tests: list[dict[str, Any]] = field(default_factory=list)


def _resolve_project_root() -> Path:
    env_root = os.getenv("AGENTIC_WORKFLOW_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()

    for candidate in Path(__file__).resolve().parents:
        if (candidate / ".git").exists() or (candidate / _AGENTIC_CORE_DIR).exists():
            return candidate

    return Path.cwd().resolve()


def _classify_file_simple(path: Path) -> str:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, SyntaxError, ValueError):
        return "unknown"

    has_class = any(isinstance(node, ast.ClassDef) for node in ast.walk(tree))
    has_function = any(isinstance(node, ast.FunctionDef) for node in ast.walk(tree))
    if has_class and has_function:
        return "mixed"
    if has_class:
        return "class"
    if has_function:
        return "function"
    return "module"


def _source_roots(project_root: Path) -> list[Path]:
    return [
        project_root / _AGENTIC_CORE_DIR,
        project_root / _APPS_RG_DIR,
        project_root / _APPS_LIC_DIR,
        project_root / _APPS_SHARED_DIR,
    ]


def _test_root(project_root: Path) -> Path:
    return project_root / _TESTS_DIR / "unit"


def _territory_of(path: Path, project_root: Path) -> str:
    return path.relative_to(project_root).parts[0]


def _expected_test_for_source(source_path: Path, project_root: Path) -> Path:
    relative = source_path.relative_to(project_root)
    territory = relative.parts[0]
    subpath = Path(*relative.parts[1:])
    return _test_root(project_root) / territory / subpath.with_name(f"test_{subpath.stem}.py")


def _expected_source_for_test(test_path: Path, project_root: Path) -> tuple[Path | None, Path | None]:
    unit_root = _test_root(project_root)
    try:
        relative = test_path.relative_to(unit_root)
    except ValueError:
        return None, None

    if len(relative.parts) < 2:
        return None, None

    territory = relative.parts[0]
    file_name = relative.name
    if not file_name.startswith("test_"):
        return None, None

    source_name = file_name[len("test_") :]
    source_relative = Path(territory, *relative.parts[1:-1], source_name)
    expected_source = project_root / source_relative
    expected_test = _expected_test_for_source(expected_source, project_root)
    return expected_source, expected_test


def scan_source_files(project_root: Path) -> list[SourceFile]:
    source_files: list[SourceFile] = []
    for root in _source_roots(project_root):
        if not root.exists():
            continue
        for py_file in sorted(root.rglob("*.py")):
            if "__pycache__" in py_file.parts or py_file.name == "__init__.py":
                continue
            source_files.append(
                SourceFile(
                    path=str(py_file),
                    territory=_territory_of(py_file, project_root),
                    kind=_classify_file_simple(py_file),
                    expected_test=str(_expected_test_for_source(py_file, project_root)),
                )
            )
    return source_files


def scan_test_files(project_root: Path) -> list[TestFile]:
    test_files: list[TestFile] = []
    root = _test_root(project_root)
    if not root.exists():
        return test_files

    for py_file in sorted(root.rglob("test_*.py")):
        if "__pycache__" in py_file.parts:
            continue
        expected_source, expected_test = _expected_source_for_test(py_file, project_root)
        is_orphan = expected_source is None or not expected_source.exists()
        is_misplaced = expected_test is not None and py_file.resolve() != expected_test.resolve()
        test_files.append(
            TestFile(
                path=str(py_file),
                expected_source=str(expected_source) if expected_source else None,
                expected_test=str(expected_test) if expected_test else None,
                is_misplaced=is_misplaced,
                is_orphan=is_orphan,
            )
        )
    return test_files


def move_test_file(test_file: TestFile, *, dry_run: bool, execute: bool) -> bool:
    if not test_file.expected_test:
        return False
    source = Path(test_file.path)
    target = Path(test_file.expected_test)
    if source == target:
        return False
    if target.exists():
        return False
    if dry_run or not execute:
        return True

    target.parent.mkdir(parents=True, exist_ok=True)
    tmp_target = target.with_suffix(target.suffix + ".tmp")
    shutil.copy2(source, tmp_target)
    tmp_target.replace(target)
    source.unlink()
    return True


def run_mirror_audit(project_root: Path, *, dry_run: bool, execute: bool) -> MirrorAuditReport:
    source_files = scan_source_files(project_root)
    test_files = scan_test_files(project_root)
    by_expected_test = {item.expected_test: item for item in test_files if item.expected_test}

    report = MirrorAuditReport(
        project_root=str(project_root),
        dry_run=dry_run,
        execute=execute,
        sources=len(source_files),
        tests=len(test_files),
    )

    for source_file in source_files:
        has_test = source_file.expected_test in by_expected_test
        source_file.has_test = has_test
        if not has_test:
            report.missing_tests.append(asdict(source_file))

    for test_file in test_files:
        if test_file.is_orphan:
            report.orphan_tests.append(asdict(test_file))
        if test_file.is_misplaced:
            report.misplaced_tests.append(asdict(test_file))
            if move_test_file(test_file, dry_run=dry_run, execute=execute):
                report.moved_tests.append(asdict(test_file))

    return report


def generate_violation_report(report: MirrorAuditReport) -> dict[str, Any]:
    return {
        "project_root": report.project_root,
        "dry_run": report.dry_run,
        "execute": report.execute,
        "sources": report.sources,
        "tests": report.tests,
        "missing_tests": len(report.missing_tests),
        "misplaced_tests": len(report.misplaced_tests),
        "orphan_tests": len(report.orphan_tests),
        "moved_tests": len(report.moved_tests),
        "details": asdict(report),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--execute", action="store_true", help="Move misplaced tests into the mirrored location."
    )
    parser.add_argument("--report", help="Optional JSON report path.")
    args = parser.parse_args(argv)

    project_root = _resolve_project_root()
    report = run_mirror_audit(project_root, dry_run=not args.execute, execute=args.execute)
    summary = generate_violation_report(report)

    if args.report:
        report_path = Path(args.report).expanduser().resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    return 1 if report.missing_tests or report.misplaced_tests or report.orphan_tests else 0


if __name__ == "__main__":
    raise SystemExit(main())
