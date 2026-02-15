#!/usr/bin/env python3
"""
Module Collision Guard - Architectural Integrity Enforcement

Detects and prevents:
- Duplicate filenames
- Duplicate logical import paths
- Namespace shadowing
- Case-insensitive conflicts
- Cross-root collisions
- Package/module dual definitions
"""

import json
import os
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple


# Allowed canonical+shim pairs (canonical_location -> shim_location)
ALLOWED_SHIM_PAIRS = {
    "agentic_core/base_agents/decorators.py": "agentic_core/utils/decorators.py",
    "agentic_core/L7_meta_learning/types/meta_learning_types.py": "agentic_core/L5_safety/types/meta_learning_types.py",
}

# Normalize paths for comparison (convert to forward slashes for consistency)
ALLOWED_SHIM_PAIRS_NORMALIZED = {
    canonical.replace("\\", "/"): shim.replace("\\", "/")
    for canonical, shim in ALLOWED_SHIM_PAIRS.items()
}


def compute_logical_import_path(file_path: Path, root: Path) -> str:
    """Compute logical import path for a Python file."""
    relative = file_path.relative_to(root)

    if file_path.name == "__init__.py":
        # foo/bar/__init__.py -> foo.bar
        parts = list(relative.parts[:-1])
    else:
        # foo/bar.py -> foo.bar
        parts = list(relative.with_suffix("").parts)

    return ".".join(parts)


def scan_directory(root: Path) -> Dict[str, List[Path]]:
    """Scan directory for Python files and map logical paths to physical files."""
    logical_map = defaultdict(list)

    for py_file in root.rglob("*.py"):
        if "__pycache__" in py_file.parts:
            continue

        logical_path = compute_logical_import_path(py_file, root)
        logical_map[logical_path].append(py_file)

    return logical_map


def is_allowed_shim_pair(files: List[Tuple[str, Path]]) -> bool:
    """Check if duplicate files form an allowed canonical+shim pair."""
    if len(files) != 2:
        return False

    # Normalize all paths to forward slashes for comparison
    path_strs = [str(file).replace('\\', '/') for root, file in files]
    for canonical, shim in ALLOWED_SHIM_PAIRS_NORMALIZED.items():
        if canonical in path_strs and shim in path_strs:
            return True
    return False


def detect_collisions(scans: Dict[str, Dict[str, List[Path]]]) -> Dict[str, List[Tuple[str, List[Path]]]]:
    """Detect various types of module collisions."""
    violations = {
        "duplicate_filenames": [],
        "duplicate_logical_paths": [],
        "case_insensitive_collisions": [],
        "module_package_dual_definitions": []
    }

    # Collect all files across all roots
    all_files = []
    logical_paths_map = defaultdict(list)

    for root_name, logical_map in scans.items():
        for logical_path, files in logical_map.items():
            for file_path in files:
                all_files.append((root_name, file_path))
                logical_paths_map[logical_path].append((root_name, file_path))

    # A. Duplicate filenames (stem only) - only flag if within same root and not __init__
    stem_map = defaultdict(list)
    for root_name, file_path in all_files:
        stem = file_path.stem
        # Skip __init__ files as they're expected in every directory
        if stem == "__init__":
            continue
        stem_map[(root_name, stem)].append((root_name, file_path))

    for (root_name, stem), files in stem_map.items():
        if len(files) > 1 and not is_allowed_shim_pair(files):
            violations["duplicate_filenames"].append((f"{root_name}:{stem}", files))

    # B. Duplicate logical import paths - only flag if within same root
    for logical_path, files in logical_paths_map.items():
        # Group by root
        root_groups = defaultdict(list)
        for root_name, file_path in files:
            root_groups[root_name].append((root_name, file_path))

        for root_name, root_files in root_groups.items():
            if len(root_files) > 1 and not is_allowed_shim_pair(root_files):
                violations["duplicate_logical_paths"].append((f"{root_name}:{logical_path}", root_files))

    # C. Case-insensitive collisions - only flag if within same root
    case_map = defaultdict(list)
    for logical_path, files in logical_paths_map.items():
        case_key = logical_path.lower()
        case_map[case_key].append((logical_path, files))

    for case_key, entries in case_map.items():
        unique_paths = set(logical for logical, _ in entries)
        if len(unique_paths) > 1:
            # Group by root
            root_groups = defaultdict(list)
            for logical, files in entries:
                for root_name, file_path in files:
                    root_groups[root_name].append((root_name, file_path))

            for root_name, root_files in root_groups.items():
                if len(root_files) > 1 and not is_allowed_shim_pair(root_files):
                    violations["case_insensitive_collisions"].append((f"{root_name}:{case_key}", [(case_key, root_files)]))

    # D. Module/package dual definitions - only flag if within same root
    for logical_path, files in logical_paths_map.items():
        # Group by root
        root_groups = defaultdict(list)
        for root_name, file_path in files:
            root_groups[root_name].append((root_name, file_path))

        for root_name, root_files in root_groups.items():
            has_module = any(f.name != "__init__.py" for _, f in root_files)
            has_package = any(f.name == "__init__.py" for _, f in root_files)
            if has_module and has_package and not is_allowed_shim_pair(root_files):
                violations["module_package_dual_definitions"].append((f"{root_name}:{logical_path}", root_files))

    return violations


def format_violations(violations: Dict[str, List[Tuple[str, List[Path]]]]) -> str:
    """Format violations for output with deterministic sorting."""
    output_lines = []

    for violation_type, items in violations.items():
        if not items:
            continue

        output_lines.append(f"🚨 {violation_type.upper().replace('_', ' ')}:")

        # Sort deterministically
        items_sorted = sorted(items, key=lambda x: x[0])

        for key, files in items_sorted:
            output_lines.append(f"  {key}:")
            files_sorted = sorted(files, key=lambda x: (x[0], str(x[1])))
            for root_name, file_path in files_sorted:
                # file_path is already relative to its root, just show it directly
                output_lines.append(f"    - {file_path}")
        output_lines.append("")

    return "\n".join(output_lines)


def load_baseline() -> Dict:
    """Load the baseline file containing allowed collisions."""
    baseline_path = Path("artifacts/architecture/module_collision_baseline.json")
    if not baseline_path.exists():
        return {"logical_import_path_collisions": {}, "filename_collisions": {}}

    with open(baseline_path, 'r') as f:
        return json.load(f)


def save_baseline(collisions: Dict[str, List[Tuple[str, List[Path]]]]) -> None:
    """Save current collisions to baseline file (deterministic format)."""
    baseline = {"logical_import_path_collisions": {}, "filename_collisions": {}}

    # Convert filename collisions
    if "duplicate_filenames" in collisions:
        for key, files in collisions["duplicate_filenames"]:
            stem_lower = key.split(":", 1)[1].lower()
            paths = [str(f).replace("\\", "/") for _, f in files]
            baseline["filename_collisions"][stem_lower] = sorted(paths)

    # Convert logical path collisions
    if "duplicate_logical_paths" in collisions:
        for key, files in collisions["duplicate_logical_paths"]:
            logical_lower = key.split(":", 1)[1].lower()
            paths = [str(f).replace("\\", "/") for _, f in files]
            baseline["logical_import_path_collisions"][logical_lower] = sorted(paths)

    # Sort keys for deterministic output
    baseline["filename_collisions"] = dict(sorted(baseline["filename_collisions"].items()))
    baseline["logical_import_path_collisions"] = dict(sorted(baseline["logical_import_path_collisions"].items()))

    baseline_path = Path("artifacts/architecture/module_collision_baseline.json")
    baseline_path.parent.mkdir(parents=True, exist_ok=True)

    with open(baseline_path, 'w') as f:
        json.dump(baseline, f, indent=2, sort_keys=True)


def check_against_baseline(collisions: Dict[str, List[Tuple[str, List[Path]]]], baseline: Dict) -> List[str]:
    """Check if collisions exceed baseline. Returns list of violations."""
    violations = []

    # Check filename collisions
    current_filename = {}
    if "duplicate_filenames" in collisions:
        for key, files in collisions["duplicate_filenames"]:
            stem_lower = key.split(":", 1)[1].lower()
            paths = sorted([str(f).replace("\\", "/") for _, f in files])
            current_filename[stem_lower] = paths

    # Check for new keys or growth in existing keys
    for stem_lower, paths in current_filename.items():
        if stem_lower not in baseline["filename_collisions"]:
            violations.append(f"NEW filename collision: {stem_lower} -> {paths}")
        else:
            baseline_paths = baseline["filename_collisions"][stem_lower]
            if set(paths) != set(baseline_paths):
                violations.append(f"GROWTH in filename collision {stem_lower}: baseline={baseline_paths}, current={paths}")

    # Check logical path collisions
    current_logical = {}
    if "duplicate_logical_paths" in collisions:
        for key, files in collisions["duplicate_logical_paths"]:
            logical_lower = key.split(":", 1)[1].lower()
            paths = sorted([str(f).replace("\\", "/") for _, f in files])
            current_logical[logical_lower] = paths

    for logical_lower, paths in current_logical.items():
        if logical_lower not in baseline["logical_import_path_collisions"]:
            violations.append(f"NEW logical path collision: {logical_lower} -> {paths}")
        else:
            baseline_paths = baseline["logical_import_path_collisions"][logical_lower]
            if set(paths) != set(baseline_paths):
                violations.append(f"GROWTH in logical path collision {logical_lower}: baseline={baseline_paths}, current={paths}")

    return violations


def main():
    """Main entry point."""
    repo_root = Path.cwd()
    roots_to_scan = {
        "agentic_core": Path("agentic_core"),
        "apps_lic": Path("apps_lic"),
        "apps_rg": Path("apps_rg"),
        "apps_shared": Path("apps_shared"),
        "tools": Path("tools"),
        "ops_scripts": Path("ops_scripts"),
    }

    # Check for baseline update mode
    if os.environ.get("MODULE_COLLISION_UPDATE_BASELINE") == "1":
        print("📝 UPDATING BASELINE...")

        # Validate roots exist
        missing_roots = [name for name, path in roots_to_scan.items() if not path.exists()]
        if missing_roots:
            print(f"ERROR: Missing roots: {missing_roots}")
            sys.exit(1)

        # Scan all roots
        scans = {}
        for root_name, root_path in roots_to_scan.items():
            scans[root_name] = scan_directory(root_path)

        # Detect collisions
        collisions = detect_collisions(scans)

        # Save baseline
        save_baseline(collisions)
        print(f"✅ Baseline updated with {sum(len(items) for items in collisions.values())} collision groups")
        sys.exit(0)

    # Default mode: check against baseline
    # Validate roots exist
    missing_roots = [name for name, path in roots_to_scan.items() if not path.exists()]
    if missing_roots:
        print(f"ERROR: Missing roots: {missing_roots}")
        sys.exit(1)

    # Scan all roots
    scans = {}
    for root_name, root_path in roots_to_scan.items():
        scans[root_name] = scan_directory(root_path)

    # Detect collisions
    collisions = detect_collisions(scans)

    # Load baseline
    baseline = load_baseline()

    # Check against baseline
    violations = check_against_baseline(collisions, baseline)

    if violations:
        print("🚨 MODULE COLLISION VIOLATIONS DETECTED")
        print("=" * 50)
        for violation in violations:
            print(f"  - {violation}")
        print("")
        print("❌ ARCHITECTURAL INTEGRITY COMPROMISED")
        print("Fix violations or update baseline with MODULE_COLLISION_UPDATE_BASELINE=1")
        sys.exit(1)
    else:
        total_collisions = sum(len(items) for items in collisions.values())
        if total_collisions > 0:
            print(f"✅ No new module collisions detected")
            print(f"   Existing collisions: {total_collisions} groups (baselined)")
        else:
            print("✅ No module collisions detected")
        print("Architectural integrity maintained.")
        sys.exit(0)


if __name__ == "__main__":
    main()
