#!/usr/bin/env python3
"""
Repository Cache Purge Utility

Hardened cache purge specifically for Windows environments and deep agentic architectures.
Traverses the root directory to find and destroy all __pycache__ instances with SSOT compliance.
"""

import argparse
import logging
import pathlib
import shutil
import sys

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR, get_validated_project_root
from agentic_core.L0_routing.config.path_constants import GLOBAL_EXCLUDED_DIRS, SOVEREIGN_EXCLUDED_FOLDERS

# Configure logging for Windows environments
logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def get_project_root():
    """
    SSOT-approved method to get project root directory.
    Uses the agentic_core structure as the canonical reference point.
    """
    current_file = pathlib.Path(__file__).resolve()

    # Navigate from ops_scripts/maintenance/ to root (2 levels up)
    root_dir = current_file.parents[2]

    # Verify we're at the correct root by checking for agentic_core
    if not (root_dir / AGENTIC_CORE_DIR).exists():
        raise RuntimeError(f"Project root validation failed. Expected agentic_core at {root_dir}")

    return root_dir


def purge_all_pycache(quiet=False, extended=False):
    """
    Hardened cache purge specifically for Windows environments and deep agentic architectures.
    Traverses the root directory to find and destroy all __pycache__ instances.
    """
    # SSOT-approved method of anchoring to the project root directory.
    current_file = pathlib.Path(__file__).resolve()
    root_dir = current_file.parents[2]

    # Define targets based on extended flag
    targets = ["__pycache__"]
    if extended:
        targets.extend([".pytest_cache", ".mypy_cache", ".ruff_cache"])

    count = 0
    # Logic: Search for any directory in targets, excluding envs and git
    for target in targets:
        for p in root_dir.rglob(target):
            if any(part in p.parts for part in [".venv", "env", ".git"]):
                continue

            try:
                if p.is_dir():
                    shutil.rmtree(p, ignore_errors=True)
                    count += 1
                    if not quiet:
                        print(f"Removed: {p.relative_to(root_dir)}")
            except PermissionError:  # guardian: Permission errors should validate access before operation
                if not quiet:
                    logging.warning(f"Permission denied: {p}. File likely locked. Skipping...")
            except FileNotFoundError:  # guardian: File operations should check existence before access
                pass
            except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                raise
                if not quiet:
                    logging.error(f"Failed to delete {p}: {e}")

    if not quiet:
        print(f"Purged {count} cache directories across {root_dir.name}.")

    return count


def purge_all_cache():
    """
    Extended cache purge that handles multiple cache types beyond just __pycache__.
    Includes .pytest_cache, .mypy_cache, .ruff_cache, and temporary files.
    """
    try:
        root_dir = get_project_root()
    except RuntimeError as e:  # guardian: Runtime errors should be prevented with proper validation
        logger.error(f"Failed to determine project root: {e}")
        return 0

    cache_patterns = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS

    temp_patterns = {"temp_", "tmp_"}

    count = 0
    error_count = 0

    # Purge cache directories
    for pattern in cache_patterns:
        for p in root_dir.rglob(pattern):
            if ".venv" in p.parts or "env" in p.parts or ".git" in p.parts:
                continue

            try:
                if p.is_dir():
                    shutil.rmtree(p, ignore_errors=True)
                    count += 1
                    print(f"Removed cache: {p.relative_to(root_dir)}")
            except PermissionError:  # guardian: Permission errors should validate access before operation
                logger.warning(f"Permission denied: {p}. Skipping...")
                error_count += 1
            except FileNotFoundError:  # guardian: File operations should check existence before access
                pass
            except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                raise
                logger.error(f"Failed to delete {p}: {e}")
                error_count += 1

    # Purge temporary directories
    for p in root_dir.rglob("*"):
        if not p.is_dir():
            continue

        if ".venv" in p.parts or "env" in p.parts or ".git" in p.parts:
            continue

        if any(p.name.startswith(temp_pattern) for temp_pattern in temp_patterns):
            try:
                shutil.rmtree(p, ignore_errors=True)
                count += 1
                print(f"Removed temp: {p.relative_to(root_dir)}")
            except PermissionError:  # guardian: Permission errors should validate access before operation
                logger.warning(f"Permission denied: {p}. Skipping...")
                error_count += 1
            except FileNotFoundError:  # guardian: File operations should check existence before access
                pass
            except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                raise
                logger.error(f"Failed to delete {p}: {e}")
                error_count += 1

    # Purge .pyc and .pyo files
    for p in root_dir.rglob("*.pyc"):
        if ".venv" in p.parts or "env" in p.parts or ".git" in p.parts:
            continue

        try:
            p.unlink()
            count += 1
            print(f"Removed file: {p.relative_to(root_dir)}")
        except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
            raise
            logger.error(f"Failed to delete {p}: {e}")
            error_count += 1

    print(f"Purged {count} cache items across {root_dir.name}.")
    if error_count > 0:
        print(f"Encountered {error_count} errors during cleanup.")

    return count


if __name__ == "__main__":
    # CRITICAL ANALYSIS: Adding argparse allows the pre-commit hook to run silently
    # while manual maintenance remains verbose and supports 'extended' cleaning.
    parser = argparse.ArgumentParser(description="Hardened Cache Purge Utility")
    parser.add_argument("--quiet", action="store_true", help="Suppress output (ideal for hooks)")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Purge pytest, mypy, and ruff caches as well",
    )
    args = parser.parse_args()

    # Use the new purge_all_pycache function with argparse support
    purge_all_pycache(quiet=args.quiet, extended=args.all)
