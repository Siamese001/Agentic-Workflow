#!/usr/bin/env python3
"""
Repository Cache Purge Utility.

Hardened cache purge specifically for Windows environments and deep agentic architectures.
Traverses the root directory to find and destroy cache directories with SSOT compliance.
"""

import argparse
import logging
import pathlib
import shutil

from agentic_core.L0_routing.config.path_constants import (
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
    get_validated_project_root,
)
from tqdm import tqdm

PROJECT_ROOT = get_validated_project_root()
logger = logging.getLogger(__name__)


def _is_excluded_path(path: pathlib.Path) -> bool:
    excluded_parts = {".venv", "env", ".git"}
    return any(part in excluded_parts for part in path.parts)


def _remove_path(path: pathlib.Path, root_dir: pathlib.Path, quiet: bool, dry_run: bool) -> bool:
    if dry_run:
        if not quiet:
            print(f"[DRY-RUN] Would remove: {path.relative_to(root_dir)}")
        return False

    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()

    if not quiet:
        print(f"Removed: {path.relative_to(root_dir)}")
    return True


def purge_all_pycache(quiet: bool = False, extended: bool = False, dry_run: bool = True) -> int:
    """Purge common Python cache directories."""
    root_dir = PROJECT_ROOT
    targets = ["__pycache__"]
    if extended:
        targets.extend([".pytest_cache", ".mypy_cache", ".ruff_cache"])

    removed_count = 0
    for target in tqdm(targets, desc="Targets", unit="target"):
        for path in tqdm(sorted(root_dir.rglob(target)), desc=f"Scanning {target}", unit="path"):
            if _is_excluded_path(path):
                continue

            try:
                if _remove_path(path, root_dir, quiet=quiet, dry_run=dry_run):
                    removed_count += 1
            except (PermissionError, FileNotFoundError, OSError) as exc:
                logger.warning("Failed to remove %s: %s", path, exc)

    if not quiet:
        verb = "Would purge" if dry_run else "Purged"
        print(f"{verb} {removed_count} cache directories across {root_dir.name}.")

    return removed_count


def purge_all_cache(dry_run: bool = True) -> int:
    """Extended cache purge that handles multiple cache types and temporary directories."""
    root_dir = PROJECT_ROOT
    cache_patterns = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS
    temp_prefixes = ("temp_", "tmp_")
    removed_count = 0
    error_count = 0

    for pattern in tqdm(sorted(cache_patterns), desc="Cache patterns", unit="pattern"):
        for path in tqdm(sorted(root_dir.rglob(pattern)), desc=f"Scanning {pattern}", unit="path"):
            if _is_excluded_path(path):
                continue
            try:
                if _remove_path(path, root_dir, quiet=False, dry_run=dry_run):
                    removed_count += 1
            except (PermissionError, FileNotFoundError, OSError) as exc:
                logger.warning("Failed to remove %s: %s", path, exc)
                error_count += 1

    for path in tqdm(sorted(root_dir.rglob("*")), desc="Temp directories", unit="path"):
        if not path.is_dir() or _is_excluded_path(path):
            continue
        if not path.name.startswith(temp_prefixes):
            continue
        try:
            if _remove_path(path, root_dir, quiet=False, dry_run=dry_run):
                removed_count += 1
        except (PermissionError, FileNotFoundError, OSError) as exc:
            logger.warning("Failed to remove %s: %s", path, exc)
            error_count += 1

    for path in tqdm(sorted(root_dir.rglob("*.pyc")), desc="Compiled files", unit="file"):
        if _is_excluded_path(path):
            continue
        try:
            if _remove_path(path, root_dir, quiet=False, dry_run=dry_run):
                removed_count += 1
        except (PermissionError, FileNotFoundError, OSError) as exc:
            logger.warning("Failed to remove %s: %s", path, exc)
            error_count += 1

    verb = "Would purge" if dry_run else "Purged"
    print(f"{verb} {removed_count} cache items across {root_dir.name}.")
    if error_count > 0:
        print(f"Encountered {error_count} errors during cleanup.")

    return removed_count


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
    parser = argparse.ArgumentParser(description="Hardened Cache Purge Utility")
    parser.add_argument("--quiet", action="store_true", help="Suppress output")
    parser.add_argument("--all", action="store_true", help="Purge pytest, mypy, and ruff caches as well")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually delete files. Default is dry-run.",
    )
    args = parser.parse_args()

    purge_all_pycache(quiet=args.quiet, extended=args.all, dry_run=not args.execute)
