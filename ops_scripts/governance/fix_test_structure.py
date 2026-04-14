#!/usr/bin/env python3
"""Safely relocate shallow test files into the correct domain folders."""

from __future__ import annotations

import argparse
import ast
import shutil
import sys
from pathlib import Path

from tqdm import tqdm


DOMAIN_ROOTS = ("agentic_core", "apps_rg", "apps_lic", "apps_shared")
TEST_CATEGORIES = ("unit", "integration")


def analyze_test_imports(file_path: Path) -> str | None:
    """Infer the owning domain for a test file from its imports."""
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(file_path))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return None

    for node in tqdm(list(ast.walk(tree)), desc="Analyzing imports", unit="node", leave=False):
        if isinstance(node, ast.Import):
            for alias in node.names:
                for domain in DOMAIN_ROOTS:
                    if alias.name == domain or alias.name.startswith(f"{domain}."):
                        return domain
        elif isinstance(node, ast.ImportFrom) and node.module:
            for domain in DOMAIN_ROOTS:
                if node.module == domain or node.module.startswith(f"{domain}."):
                    return domain

    return None


def move_file(source: Path, target: Path, apply: bool) -> str:
    if source.resolve() == target.resolve():
        return "SKIPPED_SAME_PATH"

    if target.exists():
        return "SKIPPED_COLLISION"

    if apply:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(target))
    return "MOVED"


def fix_test_structure(tests_root: Path, apply: bool = False) -> tuple[int, int, int]:
    print("[AUTO-FIX] Relocating misplaced shallow test files...")
    moved_count = 0
    collision_count = 0
    skipped_count = 0

    for test_type in tqdm(TEST_CATEGORIES, desc="Processing test categories", unit="category"):
        test_dir = tests_root / test_type
        if not test_dir.exists():
            continue

        print(f"\n--- Processing {test_type} tests ---")
        for item in tqdm(sorted(test_dir.iterdir()), desc=f"Scanning {test_type}", unit="file", leave=False):
            if not item.is_file():
                continue
            if not (item.name.startswith("test_") and item.name.endswith(".py")):
                continue
            if item.name in {"__init__.py", "conftest.py"}:
                continue

            domain = analyze_test_imports(item) or "agentic_core"
            target_path = test_dir / domain / item.name
            result = move_file(item, target_path, apply=apply)

            if result == "MOVED":
                action = "MOVE" if apply else "PLAN"
                print(f"  [{action}] {item.name} -> {test_type}/{domain}/")
                moved_count += 1
            elif result == "SKIPPED_COLLISION":
                print(f"  [SKIP] target already exists: {target_path}")
                collision_count += 1
            else:
                print(f"  [SKIP] same path: {item}")
                skipped_count += 1

    mode = "applied" if apply else "dry-run"
    print(
        f"\n[AUTO-FIX] Complete ({mode}): {moved_count} planned/moved, "
        f"{collision_count} collisions, {skipped_count} skipped"
    )
    return moved_count, collision_count, skipped_count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--tests-root",
        type=Path,
        default=Path.cwd() / "tests",
        help="Root tests directory.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Perform file moves. Without this flag the script runs in dry-run mode.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    tests_root = args.tests_root.resolve()

    if not tests_root.exists():
        print(f"CRITICAL: tests root not found: {tests_root}", file=sys.stderr)
        return 1

    fix_test_structure(tests_root=tests_root, apply=args.apply)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
