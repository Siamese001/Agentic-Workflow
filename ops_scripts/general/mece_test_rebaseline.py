#!/usr/bin/env python3
"""Generate or rebaseline minimal MECE-style test skeletons for source files.

The script scans core source territories, identifies files missing mirrored unit
tests, and can generate small structured test skeletons. It also reports orphan
unit tests that no longer map to a source file.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
from dataclasses import asdict, dataclass
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
class FileClassification:
    source_path: str
    file_type: str
    primary_symbol: str
    expected_test_path: str
    existing_test: bool


SOURCE_ROOTS = (_AGENTIC_CORE_DIR, _APPS_RG_DIR, _APPS_LIC_DIR, _APPS_SHARED_DIR)


def _resolve_project_root() -> Path:
    env_root = os.getenv("AGENTIC_WORKFLOW_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    for candidate in Path(__file__).resolve().parents:
        if (candidate / ".git").exists() or (candidate / _AGENTIC_CORE_DIR).exists():
            return candidate
    return Path.cwd().resolve()


def _classify_file(path: Path) -> tuple[str, str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, SyntaxError, ValueError):
        return "unknown", path.stem

    class_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    function_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    if class_names:
        return "class", class_names[0]
    if function_names:
        return "function", function_names[0]
    return "module", path.stem


def _expected_test_path(project_root: Path, source_path: Path) -> Path:
    relative = source_path.relative_to(project_root)
    territory = relative.parts[0]
    remainder = Path(*relative.parts[1:])
    return project_root / _TESTS_DIR / "unit" / territory / remainder.with_name(f"test_{remainder.stem}.py")


def classify_all_files(project_root: Path) -> list[FileClassification]:
    items: list[FileClassification] = []
    for root_name in SOURCE_ROOTS:
        root = project_root / root_name
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.py")):
            if "__pycache__" in path.parts or path.name == "__init__.py":
                continue
            file_type, primary_symbol = _classify_file(path)
            expected = _expected_test_path(project_root, path)
            items.append(
                FileClassification(
                    source_path=str(path),
                    file_type=file_type,
                    primary_symbol=primary_symbol,
                    expected_test_path=str(expected),
                    existing_test=expected.exists(),
                )
            )
    return items


def find_orphan_tests(project_root: Path) -> list[str]:
    unit_root = project_root / _TESTS_DIR / "unit"
    if not unit_root.exists():
        return []

    orphans: list[str] = []
    for test_path in sorted(unit_root.rglob("test_*.py")):
        relative = test_path.relative_to(unit_root)
        if len(relative.parts) < 2:
            continue
        territory = relative.parts[0]
        source_name = relative.name[len("test_") :]
        expected_source = project_root / territory / Path(*relative.parts[1:-1], source_name)
        if not expected_source.exists():
            orphans.append(str(test_path))
    return orphans


def generate_mece_test(source_path: Path, file_type: str, primary_symbol: str) -> str:
    module_name = source_path.stem
    import_path = ".".join(source_path.with_suffix("").parts)
    return f'''"""Generated MECE baseline tests for {module_name}."""

from __future__ import annotations

import importlib

MODULE_NAME = "{import_path}"
PRIMARY_SYMBOL = "{primary_symbol}"
FILE_TYPE = "{file_type}"


def test_module_imports() -> None:
    module = importlib.import_module(MODULE_NAME)
    assert module is not None


def test_primary_symbol_presence() -> None:
    module = importlib.import_module(MODULE_NAME)
    assert hasattr(module, PRIMARY_SYMBOL)


def test_public_api_surface_is_accessible() -> None:
    module = importlib.import_module(MODULE_NAME)
    exported = getattr(module, "__all__", None)
    assert exported is None or isinstance(exported, list | tuple)


def test_edge_case_placeholder() -> None:
    assert FILE_TYPE in {{"class", "function", "module", "unknown"}}
'''


def run_rebaseline(project_root: Path, *, execute: bool, overwrite: bool) -> dict[str, Any]:
    classifications = classify_all_files(project_root)
    created = 0
    planned = 0
    skipped = 0
    writes: list[dict[str, str]] = []

    for item in classifications:
        if item.existing_test and not overwrite:
            skipped += 1
            continue
        planned += 1
        source_path = Path(item.source_path)
        target_path = Path(item.expected_test_path)
        content = generate_mece_test(
            source_path.relative_to(project_root), item.file_type, item.primary_symbol
        )
        writes.append({"source": item.source_path, "target": item.expected_test_path})
        if execute:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            tmp_path = target_path.with_suffix(target_path.suffix + ".tmp")
            tmp_path.write_text(content, encoding="utf-8")
            tmp_path.replace(target_path)
            created += 1

    orphan_tests = find_orphan_tests(project_root)
    return {
        "project_root": str(project_root),
        "execute": execute,
        "overwrite": overwrite,
        "classified_files": len(classifications),
        "planned_writes": planned,
        "created": created,
        "skipped_existing": skipped,
        "orphan_tests": orphan_tests,
        "classifications": [asdict(item) for item in classifications],
        "writes": writes,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="Write generated tests.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing mirrored tests.")
    parser.add_argument("--report", help="Optional JSON report path.")
    args = parser.parse_args(argv)

    project_root = _resolve_project_root()
    report = run_rebaseline(project_root, execute=args.execute, overwrite=args.overwrite)

    if args.report:
        report_path = Path(args.report).expanduser().resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    return 1 if report["orphan_tests"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
