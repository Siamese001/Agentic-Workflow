#!/usr/bin/env python3
"""Remove vacuous ``assert True`` statements from test functions.

The script uses AST rewriting so it only removes explicit top-level
``assert True`` statements inside test functions. If that leaves a function
empty, a ``pass`` statement is inserted to keep the file valid.
"""

from __future__ import annotations

import argparse
import ast
import logging
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class FixResult:
    path: str
    changed: bool
    removed_asserts: int
    reason: str | None = None


class VacuousAssertCleaner(ast.NodeTransformer):
    def __init__(self) -> None:
        self.removed_asserts = 0

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        node = self.generic_visit(node)
        if not node.name.startswith("test_"):
            return node
        node.body = self._clean_body(node.body)
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
        node = self.generic_visit(node)
        if not node.name.startswith("test_"):
            return node
        node.body = self._clean_body(node.body)
        return node

    def _clean_body(self, body: list[ast.stmt]) -> list[ast.stmt]:
        preserved: list[ast.stmt] = []
        docstring_stmt: ast.stmt | None = None

        if (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            docstring_stmt = body[0]
            body = body[1:]

        for stmt in body:
            if self._is_vacuous_assert_true(stmt):
                self.removed_asserts += 1
                continue
            preserved.append(stmt)

        result: list[ast.stmt] = []
        if docstring_stmt is not None:
            result.append(docstring_stmt)
        result.extend(preserved)
        if len(result) == 0 or (len(result) == 1 and docstring_stmt is not None):
            result.append(ast.Pass())
        return result

    @staticmethod
    def _is_vacuous_assert_true(stmt: ast.stmt) -> bool:
        if not isinstance(stmt, ast.Assert):
            return False
        test = stmt.test
        return isinstance(test, ast.Constant) and test.value is True


def _resolve_project_root() -> Path:
    env_root = os.getenv("AGENTIC_WORKFLOW_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    for candidate in Path(__file__).resolve().parents:
        if (candidate / ".git").exists() or (candidate / "tests").exists():
            return candidate
    return Path.cwd().resolve()


def _collect_test_files(paths: list[str]) -> list[Path]:
    if not paths:
        default_root = _resolve_project_root() / "tests"
        return sorted(default_root.rglob("test_*.py")) if default_root.exists() else []

    collected: list[Path] = []
    for item in paths:
        path = Path(item).expanduser().resolve()
        if path.is_dir():
            collected.extend(sorted(path.rglob("test_*.py")))
        elif path.is_file() and path.suffix == ".py":
            collected.append(path)
    return collected


def _rewrite_file(path: Path, execute: bool) -> FixResult:
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source)
    except (OSError, SyntaxError, ValueError) as exc:
        return FixResult(str(path), False, 0, f"parse_failed: {exc}")

    cleaner = VacuousAssertCleaner()
    updated_tree = cleaner.visit(tree)
    ast.fix_missing_locations(updated_tree)
    if cleaner.removed_asserts == 0:
        return FixResult(str(path), False, 0, None)

    updated_source = ast.unparse(updated_tree) + "\n"
    if execute:
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        tmp_path.write_text(updated_source, encoding="utf-8")
        tmp_path.replace(path)
    return FixResult(str(path), True, cleaner.removed_asserts, None)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="Optional test files or directories.")
    parser.add_argument("--execute", action="store_true", help="Write transformed files.")
    parser.add_argument("--report", help="Optional JSON report path.")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging.")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO, format="%(levelname)s %(message)s"
    )

    results = [_rewrite_file(path, execute=args.execute) for path in _collect_test_files(args.paths)]
    changed = sum(1 for item in results if item.changed)
    removed_asserts = sum(item.removed_asserts for item in results)
    failures = [item for item in results if item.reason]

    LOGGER.info("files_changed=%s removed_asserts=%s failures=%s", changed, removed_asserts, len(failures))

    if args.report:
        import json

        report_path = Path(args.report).expanduser().resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(
                {
                    "execute": args.execute,
                    "files_scanned": len(results),
                    "files_changed": changed,
                    "removed_asserts": removed_asserts,
                    "failures": len(failures),
                    "results": [asdict(item) for item in results],
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
