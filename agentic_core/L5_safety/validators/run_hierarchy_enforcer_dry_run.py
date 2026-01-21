"""
Run HierarchyEnforcerAgent in dry-run mode (validation only)
This will scan for hierarchy violations and depth issues without making changes.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from agentic_core.L5_safety.validators.structure_blueprint import (
    CORE_SUBFOLDER_MAP,
    SOVEREIGN_REGISTRY,
)


class MockContext:
    """Mock context for dry-run mode."""
    def report(self, agent_name, key, passed, details):
        pass

def validate_l2_l3_structure(project_root: Path) -> dict:
    """Validate L2/L3 structure (CORE_SUBFOLDER_MAP) without making changes."""
    violations = []
    missing_dirs = []

    l1_structure = SOVEREIGN_REGISTRY["agentic_core"]["subfolders"]

    for l1_name in l1_structure:
        l1_path = project_root / "agentic_core" / l1_name
        if not l1_path.exists():
            continue

        # Get expected L2 subfolders from CORE_SUBFOLDER_MAP
        expected_l2 = set(CORE_SUBFOLDER_MAP.get(l1_name, []))
        if not expected_l2:
            continue

        actual_l2 = {p.name for p in l1_path.iterdir() if p.is_dir() and not p.name.startswith(".")}

        missing_l2 = expected_l2 - actual_l2
        if missing_l2:
            for missing in missing_l2:
                missing_dirs.append(f"agentic_core/{l1_name}/{missing}")
            violations.append({
                "path": f"{l1_name}",
                "missing": list(missing_l2)
            })

    return {
        "violations": violations,
        "missing_dirs": missing_dirs,
        "compliant": len(violations) == 0
    }

def validate_depth_precision(project_root: Path) -> dict:
    """Validate apps_* depth without archiving."""
    apps_exact_depth = SOVEREIGN_REGISTRY["apps_rg"]["depth"]
    violations = []

    # Phase 6.5: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery import get_data_files, get_python_files
    all_files = list(get_python_files(project_root)) + list(get_data_files(project_root, extensions=['.json', '.md', '.yaml', '.yml']))
    for file_path in all_files:
        if file_path.is_dir():
            continue

        rel = file_path.relative_to(project_root)
        if not rel.parts[0].startswith("apps_"):
            continue

        # [FIX] Depth = folder level where file resides, not path length
        depth = len(rel.parts) - 1  # Subtract 1 because file itself is not a level
        if depth != apps_exact_depth:
            violations.append({
                "file": str(rel),
                "actual_depth": depth,
                "expected_depth": apps_exact_depth
            })

    return violations

def validate_tests_depth(project_root: Path) -> dict:
    """Validate tests depth without archiving."""
    tests_exact_depth = SOVEREIGN_REGISTRY["tests"]["depth"]
    violations = []

    # Phase 6.5: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery import get_data_files, get_python_files
    all_files = list(get_python_files(project_root)) + list(get_data_files(project_root, extensions=['.json', '.md', '.yaml', '.yml']))
    for file_path in all_files:
        if file_path.is_dir():
            continue

        rel = file_path.relative_to(project_root)
        if rel.parts[0] != "tests":
            continue

        # [FIX] Depth = folder level where file resides, not path length
        depth = len(rel.parts) - 1  # Subtract 1 because file itself is not a level
        if depth != tests_exact_depth:
            violations.append({
                "file": str(rel),
                "actual_depth": depth,
                "expected_depth": tests_exact_depth
            })

    return violations

def validate_universal_depth(project_root: Path) -> dict:
    """Validate universal depth for non-Python files without archiving."""
    agentic_core_exact_depth = SOVEREIGN_REGISTRY["agentic_core"]["depth"]
    violations = []

    # Phase 6.5: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery import get_data_files
    target_exts = [".json", ".md", ".yaml", ".yml", ".toml", ".txt"]
    for file_path in get_data_files(project_root, extensions=target_exts):
        if file_path.is_dir():
            continue

        if file_path.suffix.lower() not in target_exts:
            continue

        rel = file_path.relative_to(project_root)
        if rel.parts[0] == "agentic_core":
            # [FIX] Depth = folder level where file resides, not path length
            depth = len(rel.parts) - 1  # Subtract 1 because file itself is not a level
            if depth != agentic_core_exact_depth:
                violations.append({
                    "file": str(rel),
                    "actual_depth": depth,
                    "expected_depth": agentic_core_exact_depth,
                    "type": file_path.suffix
                })

    return violations

def main():
    print("=" * 80)
    print("HIERARCHY ENFORCER - DRY RUN MODE (VALIDATION ONLY)")
    print("=" * 80)
    print("Validating L2/L3 structure and depth compliance (no changes will be made)...\n")

    project_root = Path.cwd()

    # Validate L2/L3 structure
    print("[1/4] Validating L2/L3 directory structure (CORE_SUBFOLDER_MAP)...")
    l2_l3_result = validate_l2_l3_structure(project_root)

    if l2_l3_result["compliant"]:
        print("  ✅ L2/L3 structure is compliant")
    else:
        print(f"  ⚠️  Found {len(l2_l3_result['violations'])} L2/L3 structure violations")
        print("\n  Missing directories that would be created:")
        for missing_dir in l2_l3_result["missing_dirs"][:10]:
            print(f"    - {missing_dir}")
        if len(l2_l3_result["missing_dirs"]) > 10:
            print(f"    ... and {len(l2_l3_result['missing_dirs']) - 10} more")

    # Validate apps_* depth
    print("\n[2/4] Validating apps_* depth precision...")
    apps_violations = validate_depth_precision(project_root)

    if not apps_violations:
        print("  ✅ apps_* depth is compliant")
    else:
        print(f"  ⚠️  Found {len(apps_violations)} apps_* depth violations")
        print("\n  Files that would be archived:")
        for violation in apps_violations[:5]:
            print(f"    - {violation['file']} (depth {violation['actual_depth']}, expected {violation['expected_depth']})")
        if len(apps_violations) > 5:
            print(f"    ... and {len(apps_violations) - 5} more")

    # Validate tests depth
    print("\n[3/4] Validating tests depth precision...")
    tests_violations = validate_tests_depth(project_root)

    if not tests_violations:
        print("  ✅ tests depth is compliant")
    else:
        print(f"  ⚠️  Found {len(tests_violations)} tests depth violations")
        print("\n  Files that would be archived:")
        for violation in tests_violations[:5]:
            print(f"    - {violation['file']} (depth {violation['actual_depth']}, expected {violation['expected_depth']})")
        if len(tests_violations) > 5:
            print(f"    ... and {len(tests_violations) - 5} more")

    # Validate universal depth
    print("\n[4/4] Validating universal depth (non-Python files)...")
    universal_violations = validate_universal_depth(project_root)

    if not universal_violations:
        print("  ✅ Universal depth is compliant")
    else:
        print(f"  ⚠️  Found {len(universal_violations)} universal depth violations")
        print("\n  Files that would be archived:")
        for violation in universal_violations[:5]:
            print(f"    - {violation['file']} (depth {violation['actual_depth']}, expected {violation['expected_depth']})")
        if len(universal_violations) > 5:
            print(f"    ... and {len(universal_violations) - 5} more")

    # Summary
    print("\n" + "=" * 80)
    print("DRY RUN SUMMARY")
    print("=" * 80)

    total_issues = (
        len(l2_l3_result["missing_dirs"]) +
        len(apps_violations) +
        len(tests_violations) +
        len(universal_violations)
    )

    print(f"L2/L3 directories to create: {len(l2_l3_result['missing_dirs'])}")
    print(f"apps_* files to archive: {len(apps_violations)}")
    print(f"tests files to archive: {len(tests_violations)}")
    print(f"Universal depth files to archive: {len(universal_violations)}")
    print(f"\nTotal actions that would be taken: {total_issues}")

    print("\n" + "=" * 80)
    print("DRY RUN COMPLETE - No changes were made")
    print("=" * 80)

    if total_issues > 0:
        print("\n⚠️  To apply these changes, run HierarchyEnforcerAgent with execute=True")

if __name__ == "__main__":
    main()
