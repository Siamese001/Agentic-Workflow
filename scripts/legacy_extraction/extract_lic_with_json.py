#!/usr/bin/env python3
"""Extract net incremental files (Python and JSON) from legacy_lic archive to staging directory."""

import hashlib
import shutil
from pathlib import Path
from typing import Dict, Set, List, Tuple

def get_file_hash(filepath: Path) -> str:
import logging

logger = logging.getLogger(__name__)

    """Get SHA256 hash of file content."""
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()

def get_existing_file_hashes() -> Dict[str, str]:
    """Get dict of filename -> content hash for existing sovereign files."""
    existing = {}
    repo_root = Path(".")

    sovereign_roots = {
        "agentic_core", "apps_lic", "apps_rg", "apps_shared",
        "schemas", "prompt_governance", "observability", "config",
        "data", "archives"
    }

    for root in sovereign_roots:
        root_path = repo_root / root
        if root_path.exists():
            # Check both .py and .json files
            for file_path in root_path.rglob("*.py"):
                if "__pycache__" in file_path.parts:
                    continue
                existing[file_path.name] = get_file_hash(file_path)
            for file_path in root_path.rglob("*.json"):
                if "__pycache__" in file_path.parts:
                    continue
                existing[file_path.name] = get_file_hash(file_path)

    return existing

def analyze_and_extract() -> None:
    """Analyze legacy files and extract unique content (both Python and JSON)."""
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

    # Scan all Python and JSON files in legacy_lic
    all_files = list(source_dir.rglob("*.py")) + list(source_dir.rglob("*.json"))

    for file_path in all_files:
        if "__pycache__" in file_path.parts or ".git" in file_path.parts:
            continue

        filename = file_path.name
        legacy_hash = get_file_hash(file_path)

        if filename not in existing_hashes:
            # Truly new filename
            dest_path = staging_dir / filename
            shutil.copy2(file_path, dest_path)
            extracted_files.append(filename)

        elif existing_hashes[filename] != legacy_hash:
            # Same filename but different content - might be valuable
            # Rename with _LIC suffix to preserve
            name_parts = filename.rsplit('.', 1)
            new_name = f"{name_parts[0]}_LIC.{name_parts[1]}"
            dest_path = staging_dir / new_name
            shutil.copy2(file_path, dest_path)
            unique_content_files.append((filename, new_name))

        else:
            duplicate_files.append(filename)

    return extracted_files, unique_content_files, duplicate_files

if __name__ == "__main__":

    extracted, unique_content, duplicates = analyze_and_extract()

    if extracted:
        #logger.info(f"\nExtracted files ({len(extracted)}):")
        for f in sorted(extracted):
            #logger.info(f"  - {f}")
            pass

    if unique_content:
        #logger.info(f"\nUnique content files ({len(unique_content)}):")
        for orig, new in sorted(unique_content):
            #logger.info(f"  - {orig} -> {new}")
            pass
