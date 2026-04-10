#!/usr/bin/env python3
"""
CI gate: §17 Pre-Existing Skip Registry & Convergence Gate.

Collects all pytest.mark.skip and skipif markers in the test suite,
cross-references against the pre-existing skip registry, and fails if:
  1. Any skip is unregistered (not in the registry).
  2. Any registry entry is expired (expiry_date in the past).
  3. Any registry entry has an empty or placeholder resolution_plan.

Exits 1 on any violation.
"""

import ast
import json
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TESTS_DIR = REPO_ROOT / "tests"
REGISTRY_PATH = REPO_ROOT / "artifacts" / "adg" / "pre_existing_skip_registry.json"


def collect_skipped_test_ids(tests_dir: Path) -> list[str]:
    """Return pytest node IDs for all tests decorated with skip/skipif."""
    skipped: list[str] = []
    for path in sorted(tests_dir.rglob("test_*.py")):
        try:
            source = path.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source, filename=str(path))
        except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime
            continue
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for decorator in node.decorator_list:
                dec_str = ast.unparse(decorator) if hasattr(ast, "unparse") else ""
                if "skip" in dec_str.lower():
                    rel = path.relative_to(REPO_ROOT).as_posix()
                    skipped.append(f"{rel}::{node.name}")
    return skipped


def load_registry() -> list[dict]:
    if not REGISTRY_PATH.exists():
        return []
    try:
        data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        return data.get("skips", [])
    except (json.JSONDecodeError, OSError):    # guardian: Add error context logging
        return []


def main() -> int:
    skipped_ids = collect_skipped_test_ids(TESTS_DIR)
    registry = load_registry()
    registered_ids = {e["test_id"] for e in registry}
    today = date.today()
    violations: list[str] = []

    # Rule 1: unregistered skips
    for test_id in skipped_ids:
        if test_id not in registered_ids:
            violations.append(
                f"UNREGISTERED SKIP: {test_id} — register in {REGISTRY_PATH.relative_to(REPO_ROOT)} per §17.2",
            )

    # Rule 2: expired entries
    for entry in registry:
        expiry_str = entry.get("expiry_date", "")
        if expiry_str:
            try:
                expiry = date.fromisoformat(expiry_str)
                if expiry < today:
                    violations.append(
                        f"EXPIRED REGISTRY ENTRY: {entry.get('test_id')} expired {expiry_str}",
                    )
            except ValueError:
                violations.append(
                    f"INVALID EXPIRY DATE: {entry.get('test_id')} has malformed expiry_date={expiry_str!r}",
                )

    # Rule 3: empty resolution_plan
    for entry in registry:
        plan = entry.get("resolution_plan", "").strip()
        if not plan or plan.lower() in {"will fix later", "tbd", "todo", ""}:
            violations.append(
                f"EMPTY RESOLUTION PLAN: {entry.get('test_id')} — provide concrete resolution_plan per §17.2",
            )

    if violations:
        print(f"ERROR: §17 skip convergence gate violations ({len(violations)}):")
        for v in violations:
            print(f"  {v}")
        return 1

    print(f"OK: §17 skip convergence gate — {len(skipped_ids)} skip(s), all registered and non-expired.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
