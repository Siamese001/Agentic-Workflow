"""ADG-driven test selection for runtime use.

Given a set of changed files, compute the transitive set of test files
whose imports (directly or transitively) reach one of the changed modules.

Mechanism:
    - Resolve each changed file to its ADG node ids.
    - For each changed node, compute the upstream closure along the
      ``imports`` relation (fan-in closure).
    - From the closure, filter to test files (``tests/`` prefix or
      filename matching ``test_*.py`` / ``*_test.py``).

This is intentionally conservative: a false-positive (extra test run)
is acceptable; a false-negative (missed regression) is not.

Usage (library)::

    from tools.adg.select_tests import select_tests_for
    tests = select_tests_for(["apps_shared/utils/foo.py", "tools/adg/runtime_query.py"])
    # Returns a sorted list of test file paths.

CLI::

    python tools/adg/select_tests.py path/a.py path/b.py
    python tools/adg/select_tests.py --stdin-null < changed_files.txt

Integrates cleanly with pytest::

    python -m pytest $(python tools/adg/select_tests.py apps_shared/utils/foo.py)
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .codex/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import argparse
import json
import logging
import sqlite3
import sys
from pathlib import Path
from typing import Iterable

_REPO_ROOT_FOR_IMPORT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT_FOR_IMPORT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT_FOR_IMPORT))

from tools.adg.runtime_query import (  # noqa: E402
    RuntimeADGQuery,
    _open_readonly,
    get_default_query,
)

logger = logging.getLogger(__name__)

TEST_FILE_PREFIXES: tuple[str, ...] = ("tests/", "tests\\")
TEST_FILE_SUFFIXES: tuple[str, ...] = (".py",)
TEST_FILE_NAME_PATTERNS: tuple[str, ...] = ("test_", "_test")
MAX_CLOSURE_DEPTH: int = 6


def _is_test_file(path: str | None) -> bool:
    if not path:
        return False
    p = path.replace("\\", "/").lower()
    if p.startswith("tests/"):
        return True
    name = Path(p).name
    return any(name.startswith(pat) for pat in TEST_FILE_NAME_PATTERNS) or any(
        name.endswith("_test.py") for _ in (0,)
    )


def _nodes_for_file(conn: sqlite3.Connection, file_path: str) -> list[str]:
    """Return all node ids whose resolved_path matches the given file."""
    # Normalize leading-slash and backslash variants.
    norm = file_path.replace("\\", "/").lstrip("./")
    rows = conn.execute(
        "SELECT id FROM nodes WHERE resolved_path = ? OR resolved_path = ? LIMIT 200",
        (norm, "./" + norm),
    ).fetchall()
    return [str(r["id"]) for r in rows]


def _upstream_closure(conn: sqlite3.Connection, seed_ids: Iterable[str], depth: int) -> set[str]:
    """Compute the transitive upstream closure along ``imports`` edges."""
    depth = max(1, min(int(depth), MAX_CLOSURE_DEPTH))
    frontier = {str(s) for s in seed_ids if s}
    visited: set[str] = set(frontier)
    for _ in range(depth):
        if not frontier:
            break
        placeholders = ",".join("?" * len(frontier))
        rows = conn.execute(
            f"SELECT DISTINCT src_id FROM edges "
            f"WHERE relation_type = 'imports' AND tgt_id IN ({placeholders})",
            tuple(frontier),
        ).fetchall()
        new_frontier = {str(r["src_id"]) for r in rows if r["src_id"] is not None}
        new_frontier -= visited
        if not new_frontier:
            break
        visited |= new_frontier
        frontier = new_frontier
    return visited


def select_tests_for(
    changed_files: Iterable[str],
    *,
    depth: int = MAX_CLOSURE_DEPTH,
    query: RuntimeADGQuery | None = None,
) -> list[str]:
    """Return a sorted list of test file paths that transitively import any
    of the ``changed_files``.

    Fail-soft: returns ``[]`` if no ADG snapshot is available (callers
    should fall back to running the full suite in that case).
    """
    q = query if query is not None else get_default_query()
    if q is None:
        logger.warning("select_tests_for: no ADG snapshot; returning empty set")
        return []
    sqlite_path = Path(q.snapshot_path)
    tests: set[str] = set()
    try:
        with _open_readonly(sqlite_path) as conn:
            seeds: list[str] = []
            for f in changed_files:
                seeds.extend(_nodes_for_file(conn, f))
            if not seeds:
                return []
            closure_ids = _upstream_closure(conn, seeds, depth)
            if not closure_ids:
                return []
            # Chunk to avoid SQLite SQLITE_MAX_VARIABLE_NUMBER.
            id_list = list(closure_ids)
            chunk_size = 500
            for i in range(0, len(id_list), chunk_size):
                chunk = id_list[i : i + chunk_size]
                placeholders = ",".join("?" * len(chunk))
                rows = conn.execute(
                    f"SELECT DISTINCT resolved_path FROM nodes WHERE id IN ({placeholders})",
                    tuple(chunk),
                ).fetchall()
                for r in rows:
                    path = r["resolved_path"]
                    if _is_test_file(path):
                        tests.add(path)
    except sqlite3.Error as exc:
        logger.warning("select_tests_for SQLite error: %s", exc)
        return []
    return sorted(tests)


# ---------- CLI ----------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", help="Changed files (repo-relative paths)")
    parser.add_argument(
        "--stdin-null",
        action="store_true",
        help="Read NUL-delimited file list from stdin (for git diff -z piping)",
    )
    parser.add_argument(
        "--format",
        choices=["list", "json", "pytest"],
        default="list",
        help="Output format",
    )
    parser.add_argument("--depth", type=int, default=MAX_CLOSURE_DEPTH)
    args = parser.parse_args(argv)

    files: list[str] = list(args.files)
    if args.stdin_null:
        files.extend(f for f in sys.stdin.read().split("\0") if f)
    if not files:
        parser.error("no files provided (use positional args or --stdin-null)")
        return 2

    tests = select_tests_for(files, depth=args.depth)
    if args.format == "json":
        print(json.dumps({"tests": tests, "count": len(tests)}, indent=2))
    elif args.format == "pytest":
        print(" ".join(tests))
    else:
        for t in tests:
            print(t)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
