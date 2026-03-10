#!/usr/bin/env python3
"""
Phase 2: Structural Remediation - Move mislocated tests and create missing tests.
"""

import json
import pathlib
import shutil

from agentic_core.L0_routing.config.path_constants import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    TESTS_DIR,
    get_validated_project_root,
)

_ROOT = get_validated_project_root()


def load_mislocated_tests() -> list[dict]:
    """Identify all mislocated tests that need to be moved."""
    # Use the discovery from phase 0
    with open("docs/reports/plans/phase0_discovery_report.json") as f:
        report = json.load(f)

    mislocated = []
    for module in report["modules"]:
        if module["status"] == "MISLOCATED":
            # Find the actual test file
            test_root = _ROOT / TESTS_DIR
            expected_name = pathlib.Path(module["expected_test"]).name

            # Search for the test file
            for test_file in test_root.rglob("test_*.py"):
                if test_file.name == expected_name:
                    mislocated.append(
                        {
                            "module": module["module"],
                            "expected_test": module["expected_test"],
                            "actual_test": str(test_file),
                        },
                    )
                    break

    return mislocated


def move_test_to_canonical_location(source: pathlib.Path, target: pathlib.Path) -> bool:
    """Move a test file to its canonical location."""
    if source == target:
        return True

    # Create target directory if needed
    target.parent.mkdir(parents=True, exist_ok=True)

    # Move the file
    try:
        shutil.move(str(source), str(target))
        print(f"Moved: {source} -> {target}")
        return True
    except Exception as e:
        print(f"Failed to move {source} to {target}: {e}")
        return False


def update_imports_in_test(test_file: pathlib.Path, old_location: pathlib.Path, new_location: pathlib.Path):
    """Update imports in a test file after moving it."""
    if not test_file.exists():
        return

    content = test_file.read_text(encoding="utf-8")

    # Simple import path updates based on relative location changes
    # This is a basic implementation - could be enhanced with AST parsing
    lines = content.split("\n")
    updated_lines = []

    for line in lines:
        updated_line = line
        # Update relative imports that reference the old location
        if line.strip().startswith("from ") or line.strip().startswith("import "):
            # Basic heuristic - could be made more sophisticated
            if "tests.unit" in line:
                # Convert from tests.unit.* to tests.* (mirror structure)
                updated_line = line.replace("tests.unit.", "tests.")

        updated_lines.append(updated_line)

    test_file.write_text("\n".join(updated_lines), encoding="utf-8")


def clean_empty_directories(root: pathlib.Path):
    """Remove empty directories after moving files."""
    for directory in sorted(root.rglob("*"), key=lambda x: len(x.parts), reverse=True):
        if directory.is_dir() and not any(directory.iterdir()):
            try:
                directory.rmdir()
                print(f"Removed empty directory: {directory}")
            except OSError:
                # Directory not empty or can't be removed
                pass


def move_all_mislocated_tests():
    """Move all mislocated tests to canonical locations."""
    print("=== PHASE 2: STRUCTURAL REMEDIATION ===\n")

    mislocated = load_mislocated_tests()
    print(f"Found {len(mislocated)} mislocated tests to move\n")

    moved_count = 0
    failed_count = 0

    for item in mislocated:
        source = pathlib.Path(item["actual_test"])
        target = pathlib.Path(item["expected_test"])

        print(f"Processing: {item['module']}")
        print(f"  Source: {source}")
        print(f"  Target: {target}")

        if move_test_to_canonical_location(source, target):
            # Update imports if needed
            update_imports_in_test(target, source.parent, target.parent)
            moved_count += 1
        else:
            failed_count += 1
        print()

    # Clean up empty directories
    print("Cleaning empty directories...")
    clean_empty_directories(_ROOT / TESTS_DIR)

    print("\nSummary:")
    print(f"  Moved: {moved_count}")
    print(f"  Failed: {failed_count}")
    print(f"  Total processed: {len(mislocated)}")

    return moved_count, failed_count


def create_missing_test_scaffolds():
    """Create minimal test scaffolds for missing tests (placeholder for now)."""
    print("\n=== CREATING MISSING TEST SCAFFOLDS ===\n")

    # Load discovery report to get missing modules
    with open("docs/reports/plans/phase0_discovery_report.json") as f:
        report = json.load(f)

    missing_modules = [m for m in report["modules"] if m["status"] == "MISSING"]

    # Skip waived modules
    waivers_file = pathlib.Path("tests/_contracts/mirror_waivers.yaml")
    waived_patterns = set()
    if waivers_file.exists():
        import yaml

        with open(waivers_file) as f:
            waivers = yaml.safe_load(f)
        for waiver in waivers.get("waivers", []):
            waived_patterns.add(waiver["module"])

    # Filter out waived modules
    import fnmatch

    non_waived_missing = []
    for module in missing_modules:
        module_str = module["module"].replace("\\", "/")
        is_waived = False
        for pattern in waived_patterns:
            if fnmatch.fnmatch(module_str, pattern.replace("\\", "/")):
                is_waived = True
                break
        if not is_waived:
            non_waived_missing.append(module)

    print(f"Found {len(non_waived_missing)} non-waived missing modules")

    # For now, just report the count - actual test creation will be done manually
    # or in a separate phase to ensure quality
    print("Note: Test scaffolding will be created in Phase 3 with proper assertions")

    return len(non_waived_missing)


if __name__ == "__main__":
    moved, failed = move_all_mislocated_tests()
    missing_count = create_missing_test_scaffolds()

    print("\n=== PHASE 2 COMPLETE ===")
    print(f"Mislocated tests moved: {moved}")
    print(f"Failed moves: {failed}")
    print(f"Missing tests remaining: {missing_count}")
