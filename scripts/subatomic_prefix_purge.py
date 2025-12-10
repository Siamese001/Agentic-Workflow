#!/usr/bin/env python3
"""
SUBATOMIC CANON 2025 — TOTAL PREFIX PURGE
==========================================
Removes all 01-10 prefixes except 06_data (curated knowledge plane).
Promotes apps_lic and apps_rg to top-level.
Updates all imports repo-wide.
"""

import re
import shutil
from pathlib import Path
from typing import Dict, List
import json

# =============================================================================
# CONFIGURATION
# =============================================================================

REPO_ROOT = Path(__file__).parent.parent.resolve()

# Folder rename mappings (previous -> new)
FOLDER_RENAMES: Dict[str, str] = {
    "agentic_core": "agentic_core",
    "schemas": "schemas",
    "runtime": "runtime",
    "prompt_governance": "prompt_governance",
    "config": "config",
    # 06_data stays as-is (curated knowledge plane)
    "observability": "observability",
    "scripts": "scripts",
    # 09_apps is special - we promote its children
    "tests": "tests",
}

# Import path mappings for fixing imports
IMPORT_RENAMES: Dict[str, str] = {
    "agentic_core": "agentic_core",
    "schemas": "schemas",
    "runtime": "runtime",
    "prompt_governance": "prompt_governance",
    "config": "config",
    "observability": "observability",
    "scripts": "scripts",
    "apps_lic": "apps_lic",
    "apps_rg": "apps_rg",
    "09_apps": "",      "tests": "tests",
}

# =============================================================================
# FOLDER OPERATIONS
# =============================================================================

def rename_top_level_folders() -> List[str]:
    """Rename all numbered folders to their clean names."""
    renamed = []

    for old_name, new_name in FOLDER_RENAMES.items():
        old_path = REPO_ROOT / old_name
        new_path = REPO_ROOT / new_name

        if old_path.exists() and not new_path.exists():
            shutil.move(str(old_path), str(new_path))
            renamed.append(f"{old_name} -> {new_name}")
            print(f"  ✓ Renamed: {old_name} -> {new_name}")
        elif old_path.exists() and new_path.exists():
            # Merge contents
            for item in old_path.iterdir():
                dest = new_path / item.name
                if not dest.exists():
                    shutil.move(str(item), str(dest))
            shutil.rmtree(old_path)
            renamed.append(f"{old_name} -> {new_name} (merged)")
            print(f"  ✓ Merged: {old_name} -> {new_name}")

    return renamed


def promote_apps_to_top_level() -> List[str]:
    """Promote apps_lic and apps_rg from 09_apps/ to top-level."""
    promoted = []
    apps_dir = REPO_ROOT / "09_apps"

    if not apps_dir.exists():
        return promoted

    # Promote apps_lic
    apps_lic_src = apps_dir / "apps_lic"
    apps_lic_dst = REPO_ROOT / "apps_lic"
    if apps_lic_src.exists() and not apps_lic_dst.exists():
        shutil.move(str(apps_lic_src), str(apps_lic_dst))
        promoted.append("09_apps/apps_lic -> apps_lic")
        print("  ✓ Promoted: 09_apps/apps_lic -> apps_lic")

    # Promote apps_rg
    apps_rg_src = apps_dir / "apps_rg"
    apps_rg_dst = REPO_ROOT / "apps_rg"
    if apps_rg_src.exists() and not apps_rg_dst.exists():
        shutil.move(str(apps_rg_src), str(apps_rg_dst))
        promoted.append("09_apps/apps_rg -> apps_rg")
        print("  ✓ Promoted: 09_apps/apps_rg -> apps_rg")

        if apps_dir.exists():
        remaining = list(apps_dir.iterdir())
        if len(remaining) == 0:
            apps_dir.rmdir()
            print("  ✓ Removed empty: 09_apps/")
        else:
            # Move any remaining items to appropriate locations
            for item in remaining:
                if item.name == "shared":
                    # Move shared to top-level apps_shared or merge with existing shared
                    dest = REPO_ROOT / "apps_shared"
                    if not dest.exists():
                        shutil.move(str(item), str(dest))
                        print("  ✓ Moved: 09_apps/shared -> apps_shared")
                else:
                    # Move other items to top level
                    dest = REPO_ROOT / item.name
                    if not dest.exists():
                        shutil.move(str(item), str(dest))
                        print(f"  ✓ Moved: 09_apps/{item.name} -> {item.name}")

                        try:
                shutil.rmtree(apps_dir)
                print("  ✓ Removed: 09_apps/")
            except (ValueError, TypeError, KeyError) as e:
                print(f"  ⚠ Could not remove 09_apps: {e}")

    return promoted


# =============================================================================
# IMPORT FIXING
# =============================================================================

def fix_imports_in_file(file_path: Path) -> bool:
    """Fix imports in a single Python file."""
    try:
        content = file_path.read_text(encoding="utf-8")
        original = content

        # Fix import statements
        for old_path, new_path in IMPORT_RENAMES.items():
            if not old_path:
                continue

            # Handle "from X import Y" patterns
            if new_path:
                content = re.sub(
                    rf"\bfrom\s+{re.escape(old_path)}\.(\S+)",
                    rf"from {new_path}.\1",
                    content
                )
                content = re.sub(
                    rf"\bfrom\s+{re.escape(old_path)}\b",
                    rf"from {new_path}",
                    content
                )
                content = re.sub(
                    rf"\bimport\s+{re.escape(old_path)}\.(\S+)",
                    rf"import {new_path}.\1",
                    content
                )
                content = re.sub(
                    rf"\bimport\s+{re.escape(old_path)}\b",
                    rf"import {new_path}",
                    content
                )
            else:
                                content = re.sub(
                    rf"\bfrom\s+{re.escape(old_path)}\.(\S+)",
                    r"from \1",
                    content
                )
                content = re.sub(
                    rf"\bimport\s+{re.escape(old_path)}\.(\S+)",
                    r"import \1",
                    content
                )

        # Also fix string references in paths
        for old_path, new_path in IMPORT_RENAMES.items():
            if old_path and new_path:
                # Fix path strings like "agentic_core/..."
                content = content.replace(f'"{old_path}/', f'"{new_path}/')
                content = content.replace(f"'{old_path}/", f"'{new_path}/")
                content = content.replace(f'"{old_path}"', f'"{new_path}"')
                content = content.replace(f"'{old_path}'", f"'{new_path}'")

        if content != original:
            file_path.write_text(content, encoding="utf-8")
            return True
        return False
    except (ValueError, TypeError, KeyError) as e:
        print(f"  ⚠ Could not fix imports in {file_path}: {e}")
        return False


def fix_all_imports() -> int:
    """Fix imports across the entire repository."""
    fixed_count = 0

    for py_file in REPO_ROOT.rglob("*.py"):
        # Skip files in .git, __pycache__, etc.
        if any(part.startswith('.') or part == '__pycache__' for part in py_file.parts):
            continue
        if fix_imports_in_file(py_file):
            fixed_count += 1

    return fixed_count


# =============================================================================
# YAML UPDATES
# =============================================================================

def update_yaml_files() -> None:
    """Update both YAML SSoT files with new folder names."""

    # Update main YAML
    main_yaml = REPO_ROOT / "unified_structure_subatomic.yaml"
    if main_yaml.exists():
        content = main_yaml.read_text(encoding="utf-8")

        # Replace all numbered prefixes
        for old_name, new_name in FOLDER_RENAMES.items():
            content = content.replace(old_name, new_name)

                content = content.replace("09_apps/apps_lic", "apps_lic")
        content = content.replace("09_apps/apps_rg", "apps_rg")
        content = content.replace("09_apps.", "")
        content = content.replace("09_apps:", "# 09_apps removed - apps_lic and apps_rg are now top-level")

        main_yaml.write_text(content, encoding="utf-8")
        print("  ✓ Updated: unified_structure_subatomic.yaml")

    # Update meta YAML
    meta_yaml = REPO_ROOT / "unified_structure_subatomic_meta.yaml"
    if meta_yaml.exists():
        content = meta_yaml.read_text(encoding="utf-8")

        # Replace all numbered prefixes
        for old_name, new_name in FOLDER_RENAMES.items():
            content = content.replace(old_name, new_name)

                content = content.replace("09_apps/apps_lic", "apps_lic")
        content = content.replace("09_apps/apps_rg", "apps_rg")
        content = content.replace("09_apps.", "")

        # Add numbered folder exception section if not present
        if "numbered_folder_exception:" not in content:
            exception_section = """
# ---------------------------------------------------------------------
# 12. NUMBERED FOLDER EXCEPTION — ETERNAL LAW
# ---------------------------------------------------------------------
numbered_folder_exception:
  "06_data":
    reason: "Pure curated knowledge plane — never imported as code"
    permanent: true
"""
            content += exception_section

        meta_yaml.write_text(content, encoding="utf-8")
        print("  ✓ Updated: unified_structure_subatomic_meta.yaml")


def update_workspace_file() -> None:
    """Update the VS Code workspace file."""
    workspace_file = REPO_ROOT / "Agentic.code-workspace"
    if workspace_file.exists():
        content = workspace_file.read_text(encoding="utf-8")

        for old_name, new_name in FOLDER_RENAMES.items():
            content = content.replace(old_name, new_name)

        content = content.replace("09_apps", "apps_lic")  # Point to one of the promoted folders

        workspace_file.write_text(content, encoding="utf-8")
        print("  ✓ Updated: Agentic.code-workspace")


def update_ssot_validator() -> None:
    """Update the SSOT validator script."""
    validator = REPO_ROOT / "SSOT_validator.py"
    if validator.exists():
        content = validator.read_text(encoding="utf-8")

        for old_name, new_name in FOLDER_RENAMES.items():
            content = content.replace(f'"{old_name}"', f'"{new_name}"')
            content = content.replace(f"'{old_name}'", f"'{new_name}'")
            content = content.replace(f'"{old_name}/', f'"{new_name}/')
            content = content.replace(f"'{old_name}/", f"'{new_name}/")

        content = content.replace('"09_apps"', '"apps_lic", "apps_rg"')

        validator.write_text(content, encoding="utf-8")
        print("  ✓ Updated: SSOT_validator.py")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    print("=" * 70)
    print("SUBATOMIC CANON 2025 — TOTAL PREFIX PURGE")
    print("=" * 70)

    log = {
        "renamed_folders": [],
        "promoted_apps": [],
        "fixed_imports": 0,
        "yaml_updated": True,
    }

    # Step 1: Rename top-level folders
    print("\n[STEP 1] Renaming numbered folders...")
    log["renamed_folders"] = rename_top_level_folders()

    # Step 2: Promote apps to top-level
    print("\n[STEP 2] Promoting apps_lic and apps_rg to top-level...")
    log["promoted_apps"] = promote_apps_to_top_level()

    # Step 3: Fix all imports
    print("\n[STEP 3] Fixing imports repo-wide...")
    log["fixed_imports"] = fix_all_imports()
    print(f"  ✓ Fixed imports in {log['fixed_imports']} files")

    # Step 4: Update YAML files
    print("\n[STEP 4] Updating YAML SSoT files...")
    update_yaml_files()

    # Step 5: Update other config files
    print("\n[STEP 5] Updating config files...")
    update_workspace_file()
    update_ssot_validator()

    # Write log
    log_path = REPO_ROOT / "subatomic_prefix_purge_log.json"
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, default=str)
    print(f"\n[LOG] Transformation log written to: {log_path}")

    print("\n" + "=" * 70)
    print("PREFIX PURGE COMPLETE")
    print("=" * 70)
    print("\nNew top-level structure:")
    print("  ✓ agentic_core/     (was 01_agentic_core)")
    print("  ✓ schemas/          (was 02_schemas)")
    print("  ✓ runtime/          (was 03_runtime)")
    print("  ✓ prompt_governance/(was 04_prompt_governance)")
    print("  ✓ config/           (was 05_config)")
    print("  ✓ 06_data/          (PRESERVED - curated knowledge)")
    print("  ✓ observability/    (was 07_observability)")
    print("  ✓ scripts/          (was 08_scripts)")
    print("  ✓ apps_lic/         (was 09_apps/apps_lic)")
    print("  ✓ apps_rg/          (was 09_apps/apps_rg)")
    print("  ✓ tests/            (was 10_tests)")
    print("\nNext steps:")
    print("  1. git add -A")
    print("  2. git commit -m 'feat: FINAL subatomic canon 2025 — total prefix purge, flat L2/L3/L5, imperative naming, 06_data only survivor'")
    print("  3. git push")


if __name__ == "__main__":
    main()
