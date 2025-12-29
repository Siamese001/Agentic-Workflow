import os
import sys
from typing import Any, List, Dict, Optional

def analyze_and_extract() -> None:
    """Analyze legacy files and extract unique content (Python, JSON, and Markdown)."""
    source_dir = Path("archives/legacy_lic")
    staging_dir = Path("archive_code")

    # Clean staging directory
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir()

    existing_hashes = get_existing_file_hashes()

    extracted_files = []
    duplicate_files = []
    unique_content_files = []

    # Scan all Python, JSON, and Markdown files in legacy_lic
    all_files = (
        list(source_dir.rglob("*.py")) +
        list(source_dir.rglob("*.json")) +
        list(source_dir.rglob("*.md"))
    )

    for file_path in all_files:
        if "__pycache__" in file_path.parts or ".git" in file_path.parts:
            continue

        FILENAME = file_path.name
        legacy_hash = get_file_hash(file_path)

        if FILENAME not in existing_hashes:
            # Truly new filename
            dest_path = staging_dir / FILENAME
            shutil.copy2(file_path, dest_path)
            extracted_files.append(FILENAME)
            FILENAME.split('.')[-1].upper()

        elif existing_hashes[FILENAME] != legacy_hash:
            # Same filename but different content - might be valuable
            # Rename with _LIC suffix to preserve
            name_parts = FILENAME.rsplit('.', 1)
            new_name = f"{name_parts[0]}_LIC.{name_parts[1]}"
            dest_path = staging_dir / new_name
            shutil.copy2(file_path, dest_path)
            unique_content_files.append((FILENAME, new_name))
            name_parts[1].upper()

        else:
            duplicate_files.append(FILENAME)

    return extracted_files, unique_content_files, duplicate_files
