#!/usr/bin/env python3
"""
Move mislocated tests to canonical mirror locations.
Phase 2: Structural remediation - move tests from unit/ structure to mirror structure.
"""

import os
import pathlib
import shutil

from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS


def discover_mislocated_tests() -> list[tuple[pathlib.Path, pathlib.Path, pathlib.Path]]:
    """Discover all mislocated tests and their target locations."""
    mislocated = []

    # Existing tests in old structure
    test_root = pathlib.Path(TESTS_DIR)
    if not test_root.exists():
        return mislocated

    for test_file in test_root.rglob("test_*.py"):
        # Skip contract tests
        if "_contracts" in test_file.parts:
            continue

        # Get relative path from tests/
        relative_test_path = test_file.relative_to(test_root)

        # Determine if this is in old unit structure
        if str(relative_test_path).startswith("unit/"):
            # Extract the actual module path from test path
            # tests/unit/agentic_core/base_agents/test_SovereignBaseAgent.py
            # -> agentic_core/base_agents/SovereignBaseAgent.py

            parts = list(relative_test_path.parts)
            if len(parts) >= 4 and parts[0] == "unit":
                # Reconstruct module path
                module_parts = parts[1:-1]  # Skip "unit" and test filename
                test_filename = parts[-1]

                # Convert test name back to module name
                if test_filename.startswith("test_") and test_filename.endswith(".py"):
                    module_filename = test_filename[5:]  # Remove "test_"
                else:
                    continue

                module_path = pathlib.Path(*module_parts) / module_filename

                # Compute expected test location (mirror structure)
                expected_test_path = (
                    pathlib.Path(TESTS_DIR) / module_parts[0] / pathlib.Path(*module_parts[1:]) / test_filename
                )

                if test_file != expected_test_path:
                    mislocated.append((test_file, expected_test_path, module_path))

    return mislocated


def move_test_file(source: pathlib.Path, target: pathlib.Path, dry_run: bool = True):
    """Move a test file to its canonical location."""
    # Create target directory if needed
    target.parent.mkdir(parents=True, exist_ok=True)

    if dry_run:
        print(f"Would move: {source} -> {target}")
        return False

    if target.exists():
        print(f"Target exists, skipping: {target}")
        return False

    try:
        shutil.move(str(source), str(target))
        print(f"Moved: {source} -> {target}")
        return True
    except Exception as e:
        print(f"Failed to move {source}: {e}")
        return False


def update_imports_in_moved_test(test_file: pathlib.Path, old_path: pathlib.Path, new_path: pathlib.Path):
    """Update imports in the moved test file to reflect new location."""
    try:
        content = test_file.read_text(encoding="utf-8")

        # Update relative imports based on new location
        # This is a simplified version - may need manual adjustments
        lines = content.split("\n")
        updated_lines = []

        for line in lines:
            # Skip non-import lines
            if not (line.strip().startswith("from ") or line.strip().startswith("import ")):
                updated_lines.append(line)
                continue

            # Simple heuristic for import updates - may need refinement
            if "unit." in line:
                # Remove 'unit.' from imports
                updated_line = line.replace("unit.", "")
                updated_lines.append(updated_line)
            else:
                updated_lines.append(line)

        updated_content = "\n".join(updated_lines)

        if updated_content != content:
            test_file.write_text(updated_content, encoding="utf-8")
            print(f"Updated imports in: {test_file}")

    except Exception as e:
        print(f"Failed to update imports in {test_file}: {e}")


def main():
    """Main execution."""
    print("=== Phase 2: Move Mislocated Tests to Canonical Locations ===\n")

    mislocated = discover_mislocated_tests()

    if not mislocated:
        print("✅ No mislocated tests found!")
        return

    print(f"Found {len(mislocated)} mislocated tests:\n")

    # Group by package for better organization
    by_package = {}
    for source, target, module_path in mislocated:
        package = target.parts[1] if len(target.parts) > 1 else "misc"
        if package not in by_package:
            by_package[package] = []
        by_package[package].append((source, target, module_path))

    total_moved = 0

    for package, tests in sorted(by_package.items()):
        print(f"### {package} ({len(tests)} tests)")

        for source, target, module_path in sorted(tests):
            print(f"  {module_path}")
            print(f"    {source} -> {target}")

            # Move the file
            if move_test_file(source, target, dry_run=False):
                update_imports_in_moved_test(target, source, target)
                total_moved += 1

        print()

    print(f"✅ Moved {total_moved} test files to canonical locations")

    # Clean up empty directories
    print("\n### Cleaning up empty directories...")
    test_root = pathlib.Path(TESTS_DIR)
    if test_root.exists():
        for root, dirs, files in os.walk(test_root, topdown=False):
            dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
            for dir_name in dirs:
                dir_path = pathlib.Path(root) / dir_name
                try:
                    if not any(dir_path.iterdir()):
                        dir_path.rmdir()
                        print(f"Removed empty directory: {dir_path}")
                except OSError:
                    pass  # Directory not empty or other error


if __name__ == "__main__":
    import os

    main()
