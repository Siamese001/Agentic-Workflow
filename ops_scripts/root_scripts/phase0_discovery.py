#!/usr/bin/env python3
"""
Phase 0 Discovery Script - Enumerate modules and tests for mirror contract analysis.
"""

import json
import pathlib

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    TESTS_DIR,
    get_validated_project_root,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)

_ROOT = get_validated_project_root()


def enumerate_modules() -> list[pathlib.Path]:
    """Enumerate all Python modules in scope."""
    modules = []

    # Search agentic_core
    agentic_core_path = _ROOT / AGENTIC_CORE_DIR
    if agentic_core_path.exists():
        modules.extend(agentic_core_path.rglob("*.py"))

    # Search apps_* directories
    for apps_dir in pathlib.Path(".").glob("apps_*"):
        if apps_dir.is_dir():
            modules.extend(apps_dir.rglob("*.py"))

    # Filter out excluded paths
    excluded_patterns = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS

    filtered_modules = []
    for module in modules:
        module_str = str(module)
        if not any(pattern in module_str for pattern in excluded_patterns):
            filtered_modules.append(module)

    return sorted(filtered_modules)


def enumerate_tests() -> list[pathlib.Path]:
    """Enumerate all existing test files."""
    tests_path = _ROOT / TESTS_DIR
    if not tests_path.exists():
        return []

    return sorted(tests_path.rglob("test_*.py"))


def compute_expected_test_path(module_path: pathlib.Path) -> pathlib.Path:
    """Compute canonical expected test path for a module."""
    # Convert agentic_core/foo/bar.py -> tests/agentic_core/foo/test_bar.py
    # Convert apps_lic/foo/bar.py -> tests/apps_lic/foo/test_bar.py

    module_str = str(module_path)

    if module_str.startswith(AGENTIC_CORE_DIR) or module_str.startswith(AGENTIC_CORE_DIR + "\\"):
        relative_parts = module_path.parts
        test_parts = [TESTS_DIR] + list(relative_parts[:-1]) + [f"test_{module_path.name}"]
        return pathlib.Path(*test_parts)
    elif any(module_str.startswith(apps) for apps in ["apps_", "apps_lic\\", "apps_rg\\", "apps_shared\\"]):
        relative_parts = module_path.parts
        test_parts = [TESTS_DIR] + list(relative_parts[:-1]) + [f"test_{module_path.name}"]
        return pathlib.Path(*test_parts)
    else:
        raise ValueError(f"Unexpected module path: {module_path}")


def check_test_status(module_path: pathlib.Path, existing_tests: list[pathlib.Path]) -> str:
    """Check if module has PRESENT, MISSING, or MISLOCATED test."""
    expected_path = compute_expected_test_path(module_path)

    # Check if test exists at expected location
    if expected_path in existing_tests:
        return "PRESENT"

    # Check if test exists elsewhere (mislocated)
    module_name = module_path.stem
    for test_path in existing_tests:
        if test_path.name == f"test_{module_name}.py":
            return "MISLOCATED"

    return "MISSING"


def main():
    """Main discovery execution."""
    print("=== PHASE 0: DISCOVERY LOCK ===\n")

    # 1) Enumerate modules
    print("1) Enumerating Python modules...")
    modules = enumerate_modules()
    print(f"Found {len(modules)} modules")

    # Count by package
    package_counts = {}
    for module in modules:
        if module.parts[0] == AGENTIC_CORE_DIR:
            package_counts[AGENTIC_CORE_DIR] = package_counts.get(AGENTIC_CORE_DIR, 0) + 1
        elif module.parts[0].startswith("apps_"):
            package = module.parts[0]
            package_counts[package] = package_counts.get(package, 0) + 1

    print("Package distribution:")
    for package, count in sorted(package_counts.items()):
        print(f"  {package}: {count} modules")

    # 2) Enumerate existing tests
    print("\n2) Enumerating existing tests...")
    tests = enumerate_tests()
    print(f"Found {len(tests)} test files")

    # 3) Compute status for each module
    print("\n3) Computing test status...")
    status_counts = {"PRESENT": 0, "MISSING": 0, "MISLOCATED": 0}
    module_status = []

    for module in modules:
        status = check_test_status(module, tests)
        status_counts[status] += 1
        module_status.append(
            {
                "module": str(module),
                "expected_test": str(compute_expected_test_path(module)),
                "status": status,
            },
        )

    # 4) Generate report
    print("\n4) Status breakdown:")
    for status, count in status_counts.items():
        print(f"  {status}: {count}")

    # Generate machine-readable report
    report = {
        "timestamp": "2026-02-09T06:41:00Z",
        "total_modules": len(modules),
        "total_tests": len(tests),
        "status_counts": status_counts,
        "package_counts": package_counts,
        "modules": module_status,
    }

    # Save report
    report_path = pathlib.Path("docs/reports/plans/phase0_discovery_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nReport saved to: {report_path}")

    # Print sample of each status
    print("\n5) Sample modules by status:")
    for status in ["PRESENT", "MISSING", "MISLOCATED"]:
        samples = [m for m in module_status if m["status"] == status][:3]
        print(f"\n{status} samples:")
        for sample in samples:
            print(f"  {sample['module']} -> {sample['expected_test']}")


if __name__ == "__main__":
    main()
