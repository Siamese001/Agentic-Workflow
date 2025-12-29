import os
import sys
from typing import Any, List, Dict, Optional

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
        FILENAME = py_file.name

        # Check if any file with this name already exists in sovereign codebase
        name_exists = any(FILENAME in existing for existing in existing_files)

        if not name_exists:
            # Copy to staging
            dest_path = staging_dir / FILENAME
            shutil.copy2(py_file, dest_path)
            extracted_files.append(FILENAME)

    return extracted_files
