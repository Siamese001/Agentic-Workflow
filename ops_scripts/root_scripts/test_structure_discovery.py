#!/usr/bin/env python3
"""
Test Structure Mirror Contract - Phase 0 Discovery
Generates mapping report of code modules to expected test locations.
"""

import pathlib
from collections import defaultdict
from dataclasses import dataclass

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    TESTS_DIR,
    get_validated_project_root,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)

_ROOT = get_validated_project_root()


@dataclass
class ModuleInfo:
    path: pathlib.Path
    expected_test_path: pathlib.Path
    status: str  # PRESENT, MISSING, MISLOCATED, WAIVED
    actual_test_path: pathlib.Path = None


def discover_python_modules(root: pathlib.Path) -> list[pathlib.Path]:
    """Discover all Python modules in scope."""
    modules = []
    exclude_dirs = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES

    for py_file in root.rglob("*.py"):
        # Skip excluded directories
        if any(exclude in str(py_file) for exclude in exclude_dirs):
            continue
        # Skip test files themselves
        if TESTS_DIR in py_file.parts:
            continue
        modules.append(py_file)

    return sorted(modules)


def discover_existing_tests() -> list[pathlib.Path]:
    """Discover all existing test files."""
    test_root = _ROOT / TESTS_DIR
    if not test_root.exists():
        return []

    return sorted(test_root.rglob("test_*.py"))


def compute_expected_test_path(module_path: pathlib.Path) -> pathlib.Path:
    """Compute expected test path based on mirror rules."""
    # Convert module path to test path
    if module_path.parts[0] == AGENTIC_CORE_DIR:
        # agentic_core/L1_cognition/reasoning/foo.py -> tests/agentic_core/L1_cognition/reasoning/test_foo.py
        relative_parts = module_path.parts[1:]  # Skip 'agentic_core'
        test_name = f"test_{module_path.stem}.py"
        return pathlib.Path(TESTS_DIR) / AGENTIC_CORE_DIR / pathlib.Path(*relative_parts).parent / test_name
    elif module_path.parts[0].startswith("apps_"):
        # apps_lic/engines/foo.py -> tests/apps_lic/engines/test_foo.py
        relative_parts = module_path.parts[1:]  # Skip 'apps_*'
        test_name = f"test_{module_path.stem}.py"
        return (
            pathlib.Path(TESTS_DIR) / module_path.parts[0] / pathlib.Path(*relative_parts).parent / test_name
        )
    else:
        raise ValueError(f"Unexpected module root: {module_path.parts[0]}")


def check_test_status(
    module_path: pathlib.Path,
    expected_test_path: pathlib.Path,
    existing_tests: list[pathlib.Path],
) -> tuple[str, pathlib.Path]:
    """Check test status for a module."""
    existing_test_paths = set(existing_tests)

    if expected_test_path in existing_test_paths:
        return "PRESENT", expected_test_path

    # Check if test exists elsewhere (mislocated)
    expected_name = expected_test_path.name
    for test_path in existing_tests:
        if test_path.name == expected_name and test_path.parent != expected_test_path.parent:
            return "MISLOCATED", test_path

    return "MISSING", None


def generate_mapping_report() -> dict:
    """Generate complete mapping report."""
    root = pathlib.Path(".")

    # Discover modules
    agentic_modules = discover_python_modules(_ROOT / AGENTIC_CORE_DIR)
    apps_lic_modules = discover_python_modules(_ROOT / APPS_LIC_DIR)
    apps_rg_modules = discover_python_modules(_ROOT / APPS_RG_DIR)
    apps_shared_modules = discover_python_modules(_ROOT / APPS_SHARED_DIR)

    all_modules = agentic_modules + apps_lic_modules + apps_rg_modules + apps_shared_modules

    # Discover existing tests
    existing_tests = discover_existing_tests()

    # Process each module
    modules_info = []
    status_counts = defaultdict(int)

    for module_path in all_modules:
        expected_test_path = compute_expected_test_path(module_path)
        status, actual_test_path = check_test_status(module_path, expected_test_path, existing_tests)

        module_info = ModuleInfo(
            path=module_path,
            expected_test_path=expected_test_path,
            status=status,
            actual_test_path=actual_test_path,
        )
        modules_info.append(module_info)
        status_counts[status] += 1

    # Generate summary
    summary = {
        "total_modules": len(all_modules),
        "status_counts": dict(status_counts),
        "agentic_core_count": len(agentic_modules),
        "apps_lic_count": len(apps_lic_modules),
        "apps_rg_count": len(apps_rg_modules),
        "apps_shared_count": len(apps_shared_modules),
        "existing_tests_count": len(existing_tests),
    }

    return {
        "summary": summary,
        "modules": modules_info,
    }


def main():
    """Generate and print mapping report."""
    print("=== TEST STRUCTURE MIRROR CONTRACT - PHASE 0 DISCOVERY ===\n")

    report = generate_mapping_report()

    # Print summary
    summary = report["summary"]
    print("## SUMMARY")
    print(f"Total modules: {summary['total_modules']}")
    print(f"  - agentic_core: {summary['agentic_core_count']}")
    print(f"  - apps_lic: {summary['apps_lic_count']}")
    print(f"  - apps_rg: {summary['apps_rg_count']}")
    print(f"  - apps_shared: {summary['apps_shared_count']}")
    print(f"Existing tests: {summary['existing_tests_count']}")
    print("\nStatus breakdown:")
    for status, count in summary["status_counts"].items():
        print(f"  {status}: {count}")

    print("\n## DETAILED MAPPING")

    # Group by status
    by_status = defaultdict(list)
    for module in report["modules"]:
        by_status[module.status].append(module)

    # Print MISSING modules
    if "MISSING" in by_status:
        print(f"\n### MISSING ({len(by_status['MISSING'])})")
        for module in sorted(by_status["MISSING"], key=lambda m: str(m.path)):
            print(f"  {module.path} -> {module.expected_test_path}")

    # Print MISLOCATED modules
    if "MISLOCATED" in by_status:
        print(f"\n### MISLOCATED ({len(by_status['MISLOCATED'])})")
        for module in sorted(by_status["MISLOCATED"], key=lambda m: str(m.path)):
            print(f"  {module.path}")
            print(f"    Expected: {module.expected_test_path}")
            print(f"    Actual:   {module.actual_test_path}")

    # Print PRESENT modules (just count)
    if "PRESENT" in by_status:
        print(f"\n### PRESENT ({len(by_status['PRESENT'])})")
        print("  All tests correctly located")

    print("\n=== END REPORT ===")


if __name__ == "__main__":
    main()
