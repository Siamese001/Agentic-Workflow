#!/usr/bin/env python3
"""Detailed extraction analysis for legacy_lic archive."""

import logging
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Set, Tuple

SOVEREIGN_ROOTS = {
    "agentic_core",
    "apps_lic",
    "apps_rg",
    "apps_shared",
    "schemas",
    "prompt_governance",
    "observability",
    "config",
    "data",
    "archives"
}


def get_existing_filenames() -> Set[str]:
    """Get set of all Python filenames in sovereign codebase."""
    existing = set()
    repo_root = Path(".")

    for root in SOVEREIGN_ROOTS:
        root_path = repo_root / root
        if root_path.exists():
            for py_file in root_path.rglob("*.py"):
                # Store only the filename
                existing.add(py_file.name)

    return existing


LOGGER = logging.getLogger(__name__)


def analyze_legacy_files() -> Tuple[List[str], List[str], List[str]]:
    """Analyze legacy files and categorize them."""
    source_dir = Path("archives/legacy_lic")
    existing_filenames = get_existing_filenames()

    net_incremental = []
    duplicates = []
    all_files = []

    # Scan all Python files in legacy_lic
    for py_file in source_dir.rglob("*.py"):
        if "__pycache__" in py_file.parts or ".git" in py_file.parts:
            continue

        filename = py_file.name
        all_files.append(filename)

        if filename in existing_filenames:
            duplicates.append(filename)
        else:
            net_incremental.append(filename)

    return all_files, net_incremental, duplicates


def extract_net_incremental() -> None:
    """Extract files that don't exist in sovereign codebase."""
    source_dir = Path("archives/legacy_lic")
    staging_dir = Path("archive_code")

    # Clean staging directory
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir()

    existing_filenames = get_existing_filenames()
    extracted_files = []

    # Scan all Python files in legacy_lic
    for py_file in source_dir.rglob("*.py"):
        if "__pycache__" in py_file.parts or ".git" in py_file.parts:
            continue

        filename = py_file.name

        if filename not in existing_filenames:
            # Copy to staging
            dest_path = staging_dir / filename
            shutil.copy2(py_file, dest_path)
            extracted_files.append(filename)

    return extracted_files


if __name__ == "__main__":

    all_files, net_incremental, duplicates = analyze_legacy_files()

    if net_incremental:
        # logger.info(f"\nNet incremental files ({len(net_incremental)}):")
        for f in sorted(net_incremental):
            # logger.info(f"  - {f}")
            pass
        extracted = extract_net_incremental()

    else:
        # logger.info("\nNo net incremental files to extract")
        if duplicates:
            # logger.info(f"\nDuplicate files ({len(set(duplicates))}):")
            for f in sorted(set(duplicates)):
                # logger.info(f"  - {f}")
                pass