#!/usr/bin/env python3
"""
Restore truly unique files from archives, excluding duplicates and backups.

Filters out:
- identity_duplicates/ folder
- .sovereign_healing_backup/ paths
- Any path containing 'backup' or 'duplicate'
- Files that already exist in current codebase
"""

import ast
import os
import shutil
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import ARCHIVES_DIR
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)

# ============================================================================
# CONFIGURATION
# ============================================================================

ARCHIVES_ROOT = Path(ARCHIVES_DIR)
CURRENT_DIRS = [AGENTIC_CORE_DIR, APPS_RG_DIR, APPS_LIC_DIR, APPS_SHARED_DIR, "scripts"]

# Folders to EXCLUDE (duplicates/backups)
EXCLUDE_FOLDERS = {
    "identity_duplicates",
    "hierarchy_violations",  # Contains many duplicates
    "void_violations",  # Contains many duplicates
    "location_violations",  # Contains many duplicates
    ".sovereign_healing_backup",
    "backups",
    "healing_backups",
    "fission_backups",
}

# Patterns in path to exclude
EXCLUDE_PATTERNS = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES

# Priority folders (scan these first)
PRIORITY_FOLDERS = [
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    "Reachout Engine Archive",
    "legacy_agents",
    "legacy_validators",
    "legacy_orchestrators",
    "consolidated_agents",
    "deprecated_agents",
]

# ============================================================================
# CODEBASE INDEX
# ============================================================================


def build_codebase_index() -> tuple[set[str], set[str], set[str]]:
    """Build index of classes, functions, and file hashes in current codebase."""
    classes = set()
    functions = set()
    file_contents = set()  # MD5 of file contents for duplicate detection

    import hashlib

    for dir_path in CURRENT_DIRS:
        if not Path(dir_path).exists():
            continue
        for py_file in Path(dir_path).rglob("*.py"):
            if "__pycache__" in str(py_file) or ARCHIVES_DIR in str(py_file):
                continue
            try:
                content = py_file.read_text(encoding="utf-8", errors="replace")
                file_contents.add(hashlib.md5(content.encode()).hexdigest())

                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        classes.add(node.name.lower())
                    elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                        functions.add(node.name.lower())
            # guardian: allow-silent-swallow
            except:
                pass

    return classes, functions, file_contents


# ============================================================================
# FILE ANALYSIS
# ============================================================================


def should_exclude_path(path: Path) -> bool:
    """Check if path should be excluded."""
    path_str = str(path).lower()

    # Check folder exclusions
    for folder in EXCLUDE_FOLDERS:
        if folder.lower() in path_str:
            return True

    # Check pattern exclusions
    for pattern in EXCLUDE_PATTERNS:
        if pattern in path_str:
            return True

    return False


def analyze_file(file_path: Path, existing_classes: set[str], existing_functions: set[str]) -> dict:
    """Analyze a file for unique content."""
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(content)
    except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime
        return {"valid": False, "error": "syntax"}
    except Exception as e:
        return {"valid": False, "error": str(e)}

    unique_agents = []
    unique_classes = []
    unique_functions = []
    existing = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            name_lower = node.name.lower()
            is_agent = node.name.endswith("Agent")

            if name_lower not in existing_classes:
                if is_agent:
                    unique_agents.append(node.name)
                else:
                    unique_classes.append(node.name)
            else:
                existing.append(node.name)

        elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            if not node.name.startswith("_"):
                if node.name.lower() not in existing_functions:
                    unique_functions.append(node.name)
                else:
                    existing.append(node.name)

    total = len(unique_agents) + len(unique_classes) + len(unique_functions) + len(existing)
    unique_count = len(unique_agents) + len(unique_classes) + len(unique_functions)

    uniqueness = (unique_count / total * 100) if total > 0 else 0
    # Boost for agents
    uniqueness += len(unique_agents) * 10
    uniqueness = min(100, uniqueness)

    return {
        "valid": True,
        "unique_agents": unique_agents,
        "unique_classes": unique_classes,
        "unique_functions": unique_functions,
        "existing": existing,
        "uniqueness": uniqueness,
        "loc": len(content.splitlines()),
    }


def infer_domain(file_path: Path, content: str = None) -> str:
    """Infer domain from path and content."""
    path_str = str(file_path).lower()

    if "lic" in path_str or "outreach" in path_str or "message" in path_str:
        return "outreach"
    if "rg" in path_str or "resume" in path_str:
        return "resume"
    return "shared"


def get_target_folder(domain: str, has_agents: bool) -> str:
    """Get target folder based on domain."""
    if domain == "outreach":
        return "apps_lic/engines/utils/" if not has_agents else "apps_lic/engines/"
    elif domain == "resume":
        return "apps_rg/engines/utils/" if not has_agents else "apps_rg/engines/"
    else:
        return "apps_shared/common_utils/" if not has_agents else "apps_shared/base_agents/"


# ============================================================================
# MAIN
# ============================================================================


def main():
    print("=" * 80)
    print("RESTORE UNIQUE FILES FROM ARCHIVES")
    print("Excluding duplicates and backups")
    print("=" * 80)

    # Build index
    print("\n[1/4] Building codebase index...")
    existing_classes, existing_functions, file_hashes = build_codebase_index()
    print(f"  Indexed: {len(existing_classes)} classes, {len(existing_functions)} functions")

    # Scan archives
    print("\n[2/4] Scanning archives (excluding duplicates)...")

    candidates = []
    skipped_folders = set()

    for root, dirs, files in os.walk(ARCHIVES_ROOT):
        root_path = Path(root)

        # Skip excluded folders
        if should_exclude_path(root_path):
            # Track which folders we're skipping
            rel = str(root_path.relative_to(ARCHIVES_ROOT)).split(os.sep)[0]
            skipped_folders.add(rel)
            dirs[:] = []  # Don't descend
            continue

        for file in files:
            if not file.endswith(".py") or file in SKIP_FILES:
                continue

            file_path = root_path / file

            # Check file hash for exact duplicates
            import hashlib

            try:
                content = file_path.read_text(encoding="utf-8", errors="replace")
                file_hash = hashlib.md5(content.encode()).hexdigest()
                if file_hash in file_hashes:
                    continue  # Exact duplicate
            # guardian: allow-silent-swallow
            except:
                continue

            # Analyze file
            result = analyze_file(file_path, existing_classes, existing_functions)

            if not result["valid"]:
                continue

            if result["uniqueness"] >= 50:  # At least 50% unique
                domain = infer_domain(file_path)
                has_agents = len(result["unique_agents"]) > 0
                target = get_target_folder(domain, has_agents)

                candidates.append(
                    {
                        "path": file_path,
                        "relative": str(file_path.relative_to(ARCHIVES_ROOT)),
                        "unique_agents": result["unique_agents"],
                        "unique_classes": result["unique_classes"],
                        "unique_functions": result["unique_functions"],
                        "uniqueness": result["uniqueness"],
                        "domain": domain,
                        "target": target,
                        "loc": result["loc"],
                    },
                )

    print(f"  Found {len(candidates)} unique files to restore")
    print(f"  Skipped folders: {skipped_folders}")

    # Sort by uniqueness
    candidates.sort(key=lambda x: -x["uniqueness"])

    # Show candidates
    print("\n[3/4] Restoration candidates...")
    print("-" * 60)

    for c in candidates[:30]:
        agents = c["unique_agents"]
        classes = c["unique_classes"][:3]
        print(f"\n  [{c['uniqueness']:.0f}%] {c['path'].name}")
        print(f"    Path: {c['relative']}")
        print(f"    Domain: {c['domain'].upper()}")
        if agents:
            print(f"    Agents: {agents}")
        if classes:
            print(f"    Classes: {classes}")
        print(f"    Target: {c['target']}")

    if len(candidates) > 30:
        print(f"\n  ... and {len(candidates) - 30} more files")

    # Execute restoration
    print("\n[4/4] Executing restoration...")
    print("-" * 60)

    restored = 0
    skipped = 0

    for c in candidates:
        src = c["path"]
        target_dir = Path(c["target"])
        target_dir.mkdir(parents=True, exist_ok=True)

        # Generate PascalCase filename
        if c["unique_agents"]:
            dst_name = c["unique_agents"][0] + ".py"
        else:
            # Convert snake_case to PascalCase
            name = src.stem
            if "_" in name:
                parts = name.split("_")
                dst_name = "".join(p.capitalize() for p in parts) + ".py"
            else:
                dst_name = name[0].upper() + name[1:] + ".py" if name else src.name

        dst = target_dir / dst_name

        if dst.exists():
            skipped += 1
            continue

        shutil.move(str(src), str(dst))
        print(f"  ✓ {dst}")
        restored += 1

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"  Restored: {restored} files")
    print(f"  Skipped (exists): {skipped} files")
    print(f"  Total candidates: {len(candidates)} files")


if __name__ == "__main__":
    main()
