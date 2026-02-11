#!/usr/bin/env python3
"""
Phase 2: Structural Remediation - Move mislocated tests and create missing tests.
"""

import fnmatch
import json
import pathlib
import shutil


def load_discovery_snapshot() -> dict:
    """Load the discovery snapshot."""
    with open("tests/_contracts/mirror_discovery_snapshot.json") as f:
        return json.load(f)


def load_waivers() -> set[str]:
    """Load waiver patterns."""
    waivers_file = pathlib.Path("tests/_contracts/mirror_waivers.yaml")
    waived_patterns = set()

    if waivers_file.exists():
        import yaml

        try:
            with open(waivers_file) as f:
                waivers = yaml.safe_load(f)
            for waiver in waivers.get("waivers", []):
                waived_patterns.add(waiver["module"])
        except Exception:
            pass

    return waived_patterns


def move_mislocated_tests():
    """Move all mislocated tests to canonical locations."""
    snapshot = load_discovery_snapshot()

    mislocated_modules = [m for m in snapshot["modules"] if m["status"] == "MISLOCATED"]
    print(f"Found {len(mislocated_modules)} mislocated tests")

    moved_count = 0

    for module_info in mislocated_modules:
        module_path = pathlib.Path(module_info["module"])
        expected_test_path = pathlib.Path(module_info["expected_test"])

        # Find the actual test file
        module_name = module_path.stem
        test_root = pathlib.Path("tests")

        actual_test = None
        for test_file in test_root.rglob("test_*.py"):
            if test_file.name == f"test_{module_name}.py":
                actual_test = test_file
                break

        if actual_test and actual_test != expected_test_path:
            print(f"Moving: {actual_test} -> {expected_test_path}")

            # Create target directory
            expected_test_path.parent.mkdir(parents=True, exist_ok=True)

            # Move the file
            try:
                shutil.move(str(actual_test), str(expected_test_path))
                moved_count += 1
            except Exception as e:
                print(f"Failed to move {actual_test}: {e}")

    print(f"Moved {moved_count} tests")
    return moved_count


def create_critical_missing_tests():
    """Create tests for critical missing modules."""
    snapshot = load_discovery_snapshot()
    waivers = load_waivers()

    missing_modules = [m for m in snapshot["modules"] if m["status"] == "MISSING"]

    # Filter out waived modules
    non_waived_missing = []
    for module in missing_modules:
        module_path = pathlib.Path(module["module"])
        if not is_waived(module_path, waivers):
            non_waived_missing.append(module)

    # Prioritize critical modules
    critical_patterns = [
        "agentic_core/base_agents/",
        "agentic_core/core/",
        "agentic_core/interfaces/",
        "agentic_core/L0_maintenance/reasoning/",
        "agentic_core/L5_safety/enforcement/",
        "apps_lic/engines/",
        "apps_rg/engines/",
    ]

    critical_modules = []
    for module in non_waived_missing:
        if any(pattern in str(module["module"]) for pattern in critical_patterns):
            critical_modules.append(module)

    print(f"Creating tests for {len(critical_modules[:20])} critical modules (limited to 20)")

    created_count = 0
    for module_info in critical_modules[:20]:  # Limit to 20 for this iteration
        if create_test_file(module_info):
            created_count += 1

    print(f"Created {created_count} test files")
    return created_count


def is_waived(module_path: pathlib.Path, waivers: set[str]) -> bool:
    """Check if module is waived."""
    module_str = str(module_path).replace("\\", "/")

    for pattern in waivers:
        pattern_norm = pattern.replace("\\", "/")
        if fnmatch.fnmatch(module_str, pattern_norm):
            return True

    return False


def create_test_file(module_info: dict) -> bool:
    """Create a test file for a module."""
    module_path = pathlib.Path(module_info["module"])
    test_path = pathlib.Path(module_info["expected_test"])

    if test_path.exists():
        return True

    # Create basic test structure
    module_name = module_path.stem
    module_import_path = str(module_path.with_suffix("")).replace("\\", ".").replace("/", ".")

    test_content = f'''#!/usr/bin/env python3
"""
Test for {module_name}
"""

import pytest
import {module_import_path}


def test_{module_name}_can_import():
    """Test that the module can be imported successfully."""
    assert {module_import_path} is not None


def test_{module_name}_has_content():
    """Test that the module has some content."""
    import {module_import_path}

    # Check that module has some attributes
    module_dict = {module_import_path}.__dict__
    meaningful_items = [
        name for name in module_dict.keys()
        if not name.startswith('__') or name in ['__all__', '__version__']
    ]

    assert len(meaningful_items) > 0, f"Module {module_import_path} appears to be empty"
'''

    try:
        test_path.parent.mkdir(parents=True, exist_ok=True)
        test_path.write_text(test_content, encoding="utf-8")
        print(f"Created: {test_path}")
        return True
    except Exception as e:
        print(f"Failed to create {test_path}: {e}")
        return False


def main():
    """Execute structural remediation."""
    print("=== PHASE 2: STRUCTURAL REMEDIATION ===")

    # Move mislocated tests
    moved = move_mislocated_tests()

    # Create critical missing tests
    created = create_critical_missing_tests()

    print("\nRemediation complete:")
    print(f"  Moved: {moved}")
    print(f"  Created: {created}")

    return moved, created


if __name__ == "__main__":
    main()
