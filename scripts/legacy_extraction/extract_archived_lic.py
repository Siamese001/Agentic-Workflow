#!/usr/bin/env python3
"""Extract net incremental files from legacy_lic archive to staging directory."""

import shutil
from pathlib import Path
from typing import Set

# Current sovereign codebase roots
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

def get_existing_files() -> Set[str]:
    """Docstring."""
import logging

logger = logging.getLogger(__name__)

    """Get set of all Python files in sovereign codebase."""
    existing = set()
    repo_root = Path(".")

    for root in SOVEREIGN_ROOTS:
        root_path = repo_root / root
        if root_path.exists():
            for py_file in root_path.rglob("*.py"):
                # Store relative path from repo root
                rel_path = py_file.relative_to(repo_root)
                existing.add(str(rel_path))

    return existing

def extract_net_incremental() -> None:
    """Extract files that don't exist in sovereign codebase."""
    source_dir = Path("archives/legacy_lic")
    staging_dir = Path("archive_code")

    # Clean staging directory
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir()

    existing_files = get_existing_files()
    extracted_files = []

    # Scan all Python files in legacy_lic
    for py_file in source_dir.rglob("*.py"):
        # Skip __pycache__ and other non-essential dirs
        if "__pycache__" in py_file.parts or ".git" in py_file.parts:
            continue

        # Get filename only for comparison (since legacy_lic has different structure)
        filename = py_file.name

        # Check if any file with this name already exists in sovereign codebase
        name_exists = any(filename in existing for existing in existing_files)

        if not name_exists:
            # Copy to staging
            dest_path = staging_dir / filename
            shutil.copy2(py_file, dest_path)
            extracted_files.append(filename)

    return extracted_files

if __name__ == "__main__":
    extracted = extract_net_incremental()

    if extracted:
        #logger.info(f"Extracted {len(extracted)} files:")
        for f in sorted(extracted):
            #logger.info(f"  - {f}")
            pass
    else:
        #logger.info("No new files to extract")
        pass
