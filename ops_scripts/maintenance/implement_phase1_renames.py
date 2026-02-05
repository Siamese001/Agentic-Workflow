#!/usr/bin/env python3
"""
Phase 1 Implementation: SCRIPT Renames
Renames PascalCase files in scripts folders to snake_case and updates imports.
"""

import json
import os
import re
from pathlib import Path
from typing import Any


def load_proposals() -> list[dict[str, Any]]:
    """Load proposals from the classification report"""
    with open("file_classification_report.json") as f:
        data = json.load(f)
    return [p for p in data["proposals"] if p["file_type"] == "SCRIPT"]


def update_imports_in_file(file_path: Path, old_module: str, new_module: str) -> bool:
    """Update imports in a single file"""
    try:
        content = file_path.read_text(encoding="utf-8")
        if old_module not in content:
            return False

        # Regex patterns for import statements
        patterns = [
            (rf"(from\s+[\w.]*){re.escape(old_module)}(\s+import)", rf"\1{new_module}\2"),
            (rf"(import\s+[\w.]*){re.escape(old_module)}(\s|$|,)", rf"\1{new_module}\2"),
        ]

        new_content = content
        for pattern, replacement in patterns:
            new_content = re.sub(pattern, replacement, new_content)

        if new_content != content:
            file_path.write_text(new_content, encoding="utf-8")
            return True
        return False
    except Exception as e:
        print(f"  Error updating {file_path}: {e}")
        return False


def find_all_imports(project_root: Path, old_module: str) -> list[Path]:
    """Find all files that import the old module"""
    files_with_imports = []
    exclude_dirs = {
        ".git",
        "archives",
        "__pycache__",
        "node_modules",
        "venv",
        ".env",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
    }

    for dirpath, dirnames, filenames in os.walk(project_root):
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        for filename in filenames:
            if filename.endswith(".py"):
                file_path = Path(dirpath) / filename
                try:
                    content = file_path.read_text(encoding="utf-8")
                    if old_module in content:
                        files_with_imports.append(file_path)
                except:
                    continue
    return files_with_imports


def rename_file(src: Path, dest: Path) -> bool:
    """Rename a file safely"""
    try:
        if dest.exists():
            print(f"  WARNING: Destination exists: {dest}")
            return False
        src.rename(dest)
        return True
    except Exception as e:
        print(f"  Error renaming {src} -> {dest}: {e}")
        return False


def main():
    project_root = Path(__file__).parent.resolve()
    proposals = load_proposals()

    print("=" * 80)
    print(f"PHASE 1: SCRIPT RENAMES ({len(proposals)} files)")
    print("=" * 80)

    success_count = 0
    import_update_count = 0
    errors = []

    for i, proposal in enumerate(proposals, 1):
        src_path = Path(proposal["current_path"])
        dest_name = proposal["proposed_name"]
        dest_path = src_path.parent / dest_name
        old_module = proposal["current_name"].replace(".py", "")
        new_module = dest_name.replace(".py", "")

        print(f"\n[{i}/{len(proposals)}] {proposal['relative_path']}")
        print(f"  {proposal['current_name']} -> {dest_name}")

        # Step 1: Find files that import this module
        files_to_update = find_all_imports(project_root, old_module)
        print(f"  Found {len(files_to_update)} files with imports to update")

        # Step 2: Update imports BEFORE renaming
        for file_path in files_to_update:
            if file_path != src_path:  # Don't update the file being renamed
                if update_imports_in_file(file_path, old_module, new_module):
                    import_update_count += 1
                    print(f"    Updated: {file_path.relative_to(project_root)}")

        # Step 3: Rename the file
        if rename_file(src_path, dest_path):
            success_count += 1
            print("  SUCCESS: Renamed")
        else:
            errors.append(proposal["relative_path"])
            print("  FAILED: Could not rename")

    print("\n" + "=" * 80)
    print("PHASE 1 SUMMARY")
    print("=" * 80)
    print(f"Files renamed: {success_count}/{len(proposals)}")
    print(f"Import updates: {import_update_count}")
    print(f"Errors: {len(errors)}")

    if errors:
        print("\nFailed files:")
        for err in errors:
            print(f"  - {err}")

    return success_count == len(proposals)


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
