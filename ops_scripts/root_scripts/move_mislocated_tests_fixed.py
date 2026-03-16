#!/usr/bin/env python3
"""
Move mislocated tests to canonical mirror locations - Fixed version.
Phase 2: Structural remediation - move tests from unit/ structure to mirror structure.
"""

import os
import pathlib
import shutil

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    TESTS_DIR,
    get_validated_project_root,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "move_mislocated_tests_fixed")
_emit_applies_guardrail("p0", "move_mislocated_tests_fixed", "p0_governance")
_emit_reads_policy_state("p0", "move_mislocated_tests_fixed", "policy_binding")
_emit_snapshots_state("p0", "move_mislocated_tests_fixed", "state_snapshot")
emit_replay_key("p0", "move_mislocated_tests_fixed")
emit_determinism_digest("p0", "move_mislocated_tests_fixed")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

_ROOT = get_validated_project_root()

_APP_DIRS: frozenset[str] = frozenset({AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR})


def discover_mislocated_tests() -> list[tuple[pathlib.Path, pathlib.Path, pathlib.Path]]:
    """Discover all mislocated tests and their target locations."""
    mislocated = []

    test_root = _ROOT / TESTS_DIR
    if not test_root.exists():
        return mislocated

    for test_file in test_root.rglob("test_*.py"):
        # Skip contract tests
        if "_contracts" in test_file.parts:
            continue

        relative = test_file.relative_to(test_root)
        parts = list(relative.parts)

        # Check if this is in unit structure for our packages
        if len(parts) >= 3 and parts[0] == "unit" and parts[1] in _APP_DIRS:
            # This should be moved to mirror structure
            # tests/unit/agentic_core/base_agents/test_foo.py -> tests/agentic_core/base_agents/test_foo.py

            package = parts[1]  # agentic_core, apps_lic, etc.
            module_parts = parts[2:]  # base_agents, test_foo.py

            # Target location in mirror structure
            target_path = pathlib.Path(TESTS_DIR) / package / pathlib.Path(*module_parts)

            # Reconstruct module path for reporting
            test_filename = parts[-1]
            if test_filename.startswith("test_") and test_filename.endswith(".py"):
                module_filename = test_filename[5:]  # Remove "test_"
                module_path = pathlib.Path(package) / pathlib.Path(*module_parts[:-1]) / module_filename
            else:
                module_path = pathlib.Path(package) / pathlib.Path(*module_parts[:-1]) / test_filename

            mislocated.append((test_file, target_path, module_path))

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
        raise
        print(f"Failed to move {source}: {e}")
        return False


def update_imports_in_moved_test(test_file: pathlib.Path):
    """Update imports in the moved test file to reflect new location."""
    try:
        content = test_file.read_text(encoding="utf-8")

        # Update relative imports based on new location
        lines = content.split("\n")
        updated_lines = []

        for line in lines:
            # Skip non-import lines
            if not (line.strip().startswith("from ") or line.strip().startswith("import ")):
                updated_lines.append(line)
                continue

            # Remove 'unit.' from imports
            if "unit." in line:
                updated_line = line.replace("unit.", "")
                updated_lines.append(updated_line)
            else:
                updated_lines.append(line)

        updated_content = "\n".join(updated_lines)

        if updated_content != content:
            test_file.write_text(updated_content, encoding="utf-8")
            print(f"Updated imports in: {test_file}")

    except Exception as e:
        raise
        print(f"Failed to update imports in {test_file}: {e}")


def main():
    """Main execution."""
    print("=== Phase 2: Move Mislocated Tests to Canonical Locations ===\n")

    mislocated = discover_mislocated_tests()

    if not mislocated:
        print("✅ No mislocated tests found!")
        return

    print(f"Found {len(mislocated)} mislocated tests to move\n")

    # Group by package for better organization
    by_package = {}
    for source, target, module_path in mislocated:
        package = target.parts[1] if len(target.parts) > 1 else "misc"
        if package not in by_package:
            by_package[package] = []
        by_package[package].append((source, target, module_path))

    total_moved = 0

    for package, tests in sorted(by_package.items()):
        print(f"### Moving {package} tests ({len(tests)} files)")

        for source, target, module_path in sorted(tests):
            print(f"  {module_path}")
            print(
                f"    {source.relative_to(_ROOT / TESTS_DIR)} -> {target.relative_to(_ROOT / TESTS_DIR)}",
            )

            # Move the file
            if move_test_file(source, target, dry_run=False):
                update_imports_in_moved_test(target)
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
                        print(f"Removed empty directory: {dir_path.relative_to(test_root)}")
                except OSError:
                    pass  # Directory not empty or other error


if __name__ == "__main__":
    main()
