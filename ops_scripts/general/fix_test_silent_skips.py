#!/usr/bin/env python3
"""Narrow broad exception guards in tests when they only toggle availability flags.

The rewrite is conservative. It only changes ``except``, ``except Exception``,
and ``except BaseException`` blocks whose bodies only assign ``False`` to names
that look like availability gates.
"""

from __future__ import annotations

import argparse
import ast
import logging
import os
from dataclasses import asdict, dataclass
from pathlib import Path

LOGGER = logging.getLogger(__name__)
AVAILABILITY_TOKENS = ("available", "enabled", "installed", "imported", "has_", "present")


@dataclass(slots=True)
class FixResult:
    path: str
    changed: bool
    narrowed_handlers: int
    reason: str | None = None


class SilentSkipCleaner(ast.NodeTransformer):
    def __init__(self) -> None:
        self.narrowed_handlers = 0

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> ast.AST:
        node = self.generic_visit(node)
        if not self._is_broad_handler(node):
            return node
        if not self._is_availability_guard(node.body):
            return node
        node.type = ast.Name(id="ImportError", ctx=ast.Load())
        self.narrowed_handlers += 1
        return node

    @staticmethod
    def _is_broad_handler(node: ast.ExceptHandler) -> bool:
        if node.type is None:
            return True
        if isinstance(node.type, ast.Name):
            return node.type.id in {"Exception", "BaseException"}
        return False

    def _is_availability_guard(self, body: list[ast.stmt]) -> bool:
        if not body:
            return False
        for stmt in body:
            if not isinstance(stmt, ast.Assign):
                return False
            if not isinstance(stmt.value, ast.Constant) or stmt.value.value is not False:
                return False
            for target in stmt.targets:
                if not isinstance(target, ast.Name):
                    return False
                if not any(token in target.id.lower() for token in AVAILABILITY_TOKENS):
                    return False
        return True


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

    cleaner = SilentSkipCleaner()
    updated_tree = cleaner.visit(tree)
    ast.fix_missing_locations(updated_tree)
    if cleaner.narrowed_handlers == 0:
        return FixResult(str(path), False, 0, None)

    updated_source = ast.unparse(updated_tree) + "\n"
    if execute:
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        tmp_path.write_text(updated_source, encoding="utf-8")
        tmp_path.replace(path)
    return FixResult(str(path), True, cleaner.narrowed_handlers, None)


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
    narrowed = sum(item.narrowed_handlers for item in results)
    failures = [item for item in results if item.reason]

    LOGGER.info("files_changed=%s narrowed_handlers=%s failures=%s", changed, narrowed, len(failures))

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
                    "narrowed_handlers": narrowed,
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
