"""
Safely mirror misplaced test files into tests/unit using the source tree as the address map.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

from tqdm import tqdm


SOURCE_ROOTS = ("agentic_core", "apps_rg", "apps_lic")
EXCLUDED_SEGMENTS = {"tests", "archives", "ops_scripts"}
IMPORT_REWRITES = (
    (re.compile(r"\bfrom\s+src\.agentic_core\b"), "from agentic_core"),
    (re.compile(r"\bfrom\s+core\."), "from agentic_core."),
)


def find_project_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "tests").exists():
            return candidate
    return start


def build_source_map(project_root: Path) -> dict[str, Path]:
    print("Indexing source tree...")
    source_index: dict[str, Path] = {}
    for root_name in SOURCE_ROOTS:
        root = project_root / root_name
        if not root.exists():
            continue
        for file in root.rglob("*.py"):
            if file.name == "__init__.py":
                continue
            source_index.setdefault(file.stem, file.parent.relative_to(project_root))
    return source_index


def rewrite_imports(file_path: Path, apply: bool) -> bool:
    try:
        content = file_path.read_text(encoding="utf-8")
    except OSError:
        return False

    updated = content
    for pattern, replacement in IMPORT_REWRITES:
        updated = pattern.sub(replacement, updated)

    if updated == content:
        return False

    if apply:
        file_path.write_text(updated, encoding="utf-8")
    return True


def iter_candidate_tests(project_root: Path) -> list[Path]:
    candidates: list[Path] = []
    for file in project_root.rglob("test_*.py"):
        rel_parts = set(file.relative_to(project_root).parts)
        if EXCLUDED_SEGMENTS & rel_parts:
            continue
        candidates.append(file)
    return sorted(candidates)


def execute_sentry(project_root: Path, apply: bool = False) -> tuple[int, int, int]:
    source_map = build_source_map(project_root)
    tests_unit_root = project_root / "tests" / "unit"
    candidates = iter_candidate_tests(project_root)

    print("Scanning for misplaced test files...")
    moved = 0
    collisions = 0
    rewritten = 0

    for test_file in tqdm(candidates, desc="Relocating test files", unit="file"):
        target_stem = test_file.stem.removeprefix("test_")
        relative_parent = test_file.parent.relative_to(project_root)
        dest_dir = tests_unit_root / source_map.get(target_stem, relative_parent)
        dest_path = dest_dir / test_file.name

        if dest_path.exists():
            print(f"  [SKIP] collision: {dest_path}")
            collisions += 1
            continue

        action = "MOVE" if apply else "PLAN"
        print(f"  [{action}] {test_file.relative_to(project_root)} -> {dest_path.relative_to(project_root)}")

        if apply:
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(test_file), str(dest_path))

        rewritten += int(rewrite_imports(dest_path if apply else test_file, apply=apply))
        moved += 1

    mode = "applied" if apply else "dry-run"
    print(f"Complete ({mode}): {moved} planned/moved, {collisions} collisions, {rewritten} import rewrites")
    return moved, collisions, rewritten


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root to scan.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Perform moves and in-place import rewrites. Without this flag the script is read-only.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = find_project_root(args.project_root.resolve())

    if not project_root.exists():
        print(f"CRITICAL: project root not found: {project_root}", file=sys.stderr)
        return 1

    execute_sentry(project_root=project_root, apply=args.apply)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
