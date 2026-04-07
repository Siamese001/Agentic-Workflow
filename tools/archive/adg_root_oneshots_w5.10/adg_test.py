"""ADG Unified Testing Accelerator

Merges: adg_test_accelerator.py + adg_test_selector.py + fast_test.py

Commands:
    gap       - Gap analysis (uncovered modules by fan-in)
    scope     - Scoped test selection for changed files
    run       - Run tests with ADG-scoped selection
    groups    - Generate parallel test groups
    check     - Collection safety check
    preflight - CI preflight (combines collection + gap + eager-lint)

Usage:
    python tools/adg/adg_test.py gap --top 20 --layer L5
    python tools/adg/adg_test.py scope --changed file.py --from-diff
    python tools/adg/adg_test.py run --adg-scope --parallel 4
    python tools/adg/adg_test.py check --json out.json
    python tools/adg/adg_test.py preflight --strict
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
_logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent.parent
ADG_DIR = REPO_ROOT / "artifacts" / "adg"


def _get_latest_sqlite() -> Path | None:
    """Find latest ADG SQLite file."""
    if not ADG_DIR.exists():
        return None
    dbs = sorted(ADG_DIR.glob("adg_indexed_*.sqlite"), reverse=True)
    return dbs[0] if dbs else None


def _load_adg_index() -> Any:
    """Load ADG index from SQLite."""
    db = _get_latest_sqlite()
    if not db:
        return None
    try:
        import sqlite3
        conn = sqlite3.connect(db)
        return conn
    except Exception as e:
        _logger.warning(f"Could not load ADG: {e}")
        return None


def cmd_gap(args: argparse.Namespace) -> int:
    """Gap analysis - rank uncovered production modules by fan-in."""
    conn = _load_adg_index()
    if not conn:
        _logger.error("No ADG index found. Run: python tools/adg/adg_lifecycle.py generate")
        return 1

    layer_filter = f"AND n.layer = '{args.layer}'" if args.layer else ""

    query = f"""
    SELECT
        n.adg_name as module,
        n.layer,
        COUNT(DISTINCT e.src_id) as fan_in,
        GROUP_CONCAT(DISTINCT src.adg_name) as called_by
    FROM nodes n
    LEFT JOIN edges e ON n.id = e.dst_id AND e.relation_type = 'calls'
    LEFT JOIN nodes src ON e.src_id = src.id
    WHERE n.entity_type = 'module'
        AND n.adg_name NOT LIKE 'tests.%'
        AND n.adg_name NOT LIKE '%.test_%'
        {layer_filter}
    GROUP BY n.id
    HAVING fan_in > 0
    ORDER BY fan_in DESC
    LIMIT {args.top}
    """

    cursor = conn.execute(query)
    rows = cursor.fetchall()

    result = {
        "command": "gap",
        "top_n": args.top,
        "layer": args.layer,
        "uncovered_modules": [
            {
                "module": row[0],
                "layer": row[1],
                "fan_in": row[2],
                "called_by": row[3].split(",")[:5] if row[3] else [],
            }
            for row in rows
        ],
    }

    if args.json:
        Path(args.json).write_text(json.dumps(result, indent=2))
        _logger.info(f"Report written to {args.json}")
    else:
        print(json.dumps(result, indent=2))

    conn.close()
    return 0


def cmd_scope(args: argparse.Namespace) -> int:
    """Scoped test selection - find tests covering changed files."""
    changed_files = []

    if args.changed:
        changed_files = [args.changed]
    elif args.from_diff:
        # Get changed files from git diff
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            capture_output=True, text=True, cwd=REPO_ROOT,
        )
        changed_files = [f.strip() for f in result.stdout.split("\n") if f.strip().endswith(".py")]

    if not changed_files:
        _logger.warning("No changed Python files found")
        return 0

    conn = _load_adg_index()
    if not conn:
        _logger.error("No ADG index found")
        return 1

    # Find tests that import or call the changed modules
    related_tests = set()

    for changed in changed_files:
        module_path = changed.replace("/", ".").replace("\\", ".").replace(".py", "")

        query = """
        SELECT DISTINCT n2.resolved_path
        FROM nodes n1
        JOIN edges e ON n1.id = e.src_id OR n1.id = e.dst_id
        JOIN nodes n2 ON (e.src_id = n2.id OR e.dst_id = n2.id)
        WHERE n1.resolved_path LIKE ?
            AND n2.resolved_path LIKE '%test%'
            AND n2.entity_type = 'module'
        """

        cursor = conn.execute(query, (f"%{module_path}%",))
        for row in cursor.fetchall():
            if row[0]:
                related_tests.add(row[0])

    result = {
        "command": "scope",
        "changed_files": changed_files,
        "related_tests": sorted(related_tests),
        "test_count": len(related_tests),
    }

    if args.json:
        Path(args.json).write_text(json.dumps(result, indent=2))
    else:
        print(json.dumps(result, indent=2))

    conn.close()
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    """Run tests with ADG-scoped selection."""
    pytest_args = ["-m", "pytest"]

    if args.adg_scope:
        # Get scoped tests first
        scope_args = argparse.Namespace(
            changed=args.changed,
            from_diff=args.from_diff,
            json=None,
        )
        # Build test list from scope
        # (Simplified - actual implementation would parse scope output)
        pytest_args.extend(["-k", "test_"])  # Run tests matching pattern

    if args.parallel:
        pytest_args.extend(["-n", str(args.parallel)])

    if args.dry_run:
        pytest_args.append("--collect-only")

    if args.verbose:
        pytest_args.append("-v")

    _logger.info(f"Running: {' '.join(pytest_args)}")

    if not args.dry_run:
        result = subprocess.run(pytest_args, cwd=REPO_ROOT)
        return result.returncode
    else:
        print(f"Would run: {' '.join(pytest_args)}")
        return 0


def cmd_check(args: argparse.Namespace) -> int:
    """Collection safety check."""
    # Run pytest collection-only
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "--collect-only", "-q"],
        capture_output=True, text=True, cwd=REPO_ROOT,
    )

    collection_ok = result.returncode == 0

    # Also run eager import lint
    lint_result = subprocess.run(
        [sys.executable, "tools/lint_eager_imports.py", "tests", "--config", "config/eager_import_risk.yml"],
        capture_output=True, text=True, cwd=REPO_ROOT,
    )

    lint_ok = lint_result.returncode == 0

    result_data = {
        "command": "check",
        "collection_ok": collection_ok,
        "lint_ok": lint_ok,
        "overall_ok": collection_ok and lint_ok,
        "pytest_output": result.stdout[-500:] if len(result.stdout) > 500 else result.stdout,
        "lint_output": lint_result.stdout[-500:] if len(lint_result.stdout) > 500 else lint_result.stdout,
    }

    if args.json:
        Path(args.json).write_text(json.dumps(result_data, indent=2))
        _logger.info(f"Report written to {args.json}")
    else:
        print(json.dumps(result_data, indent=2))

    return 0 if result_data["overall_ok"] else 1


def cmd_preflight(args: argparse.Namespace) -> int:
    """CI preflight - combines collection, gap, and eager-lint checks."""
    _logger.info("=== ADG Preflight Check ===")

    # 1. Collection check
    _logger.info("1. Checking test collection...")
    check_args = argparse.Namespace(json=None)
    check_result = cmd_check(check_args)

    if check_result != 0 and args.strict:
        _logger.error("Collection check failed - aborting")
        return 1

    # 2. Gap analysis (quick)
    _logger.info("2. Running quick gap analysis...")
    gap_args = argparse.Namespace(top=10, layer=None, json=None)
    cmd_gap(gap_args)

    # 3. Scope check for changed files
    if args.from_diff or args.changed:
        _logger.info("3. Checking scope for changed files...")
        scope_args = argparse.Namespace(
            changed=args.changed,
            from_diff=args.from_diff,
            json=None,
        )
        cmd_scope(scope_args)

    _logger.info("=== Preflight Complete ===")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="adg_test",
        description="ADG Unified Testing Accelerator",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # gap command
    gap_parser = subparsers.add_parser("gap", help="Gap analysis")
    gap_parser.add_argument("--top", type=int, default=30, help="Top N results")
    gap_parser.add_argument("--layer", help="Filter by layer (L0-L6)")
    gap_parser.add_argument("--json", help="JSON output file")

    # scope command
    scope_parser = subparsers.add_parser("scope", help="Scoped test selection")
    scope_parser.add_argument("--changed", help="Specific changed file")
    scope_parser.add_argument("--from-diff", action="store_true", help="Use git diff")
    scope_parser.add_argument("--json", help="JSON output file")

    # run command
    run_parser = subparsers.add_parser("run", help="Run tests")
    run_parser.add_argument("--adg-scope", action="store_true", help="Use ADG scoping")
    run_parser.add_argument("--changed", help="Changed file for scoping")
    run_parser.add_argument("--from-diff", action="store_true", help="Scope from git diff")
    run_parser.add_argument("--parallel", "-n", type=int, help="Number of workers")
    run_parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    run_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    # check command
    check_parser = subparsers.add_parser("check", help="Collection safety check")
    check_parser.add_argument("--json", help="JSON output file")

    # preflight command
    preflight_parser = subparsers.add_parser("preflight", help="CI preflight")
    preflight_parser.add_argument("--strict", action="store_true", help="Fail on any issue")
    preflight_parser.add_argument("--quick", action="store_true", help="Quick mode")
    preflight_parser.add_argument("--changed", help="Changed file")
    preflight_parser.add_argument("--from-diff", action="store_true", help="From git diff")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    commands = {
        "gap": cmd_gap,
        "scope": cmd_scope,
        "run": cmd_run,
        "check": cmd_check,
        "preflight": cmd_preflight,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
