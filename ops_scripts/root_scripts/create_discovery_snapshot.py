#!/usr/bin/env python3
"""
Phase 0: Discovery - Create deterministic snapshot for contract enforcement.
"""

import fnmatch
import hashlib
import json
import pathlib

import yaml

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
    for apps_dir in _ROOT.glob("apps_*"):
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
    test_root = _ROOT / TESTS_DIR
    if not test_root.exists():
        return []

    return sorted(test_root.rglob("test_*.py"))


def compute_expected_test_path(module_path: pathlib.Path) -> pathlib.Path:
    """Compute canonical expected test path for a module."""
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


def load_waivers() -> set[str]:
    """Load waiver patterns."""
    waivers_file = pathlib.Path("tests/_contracts/mirror_waivers.yaml")
    waived_patterns = set()

    if waivers_file.exists():
        try:
            with open(waivers_file) as f:
                waivers = yaml.safe_load(f)
            for waiver in waivers.get("waivers", []):
                waived_patterns.add(waiver["module"])
        except (OSError, yaml.YAMLError, KeyError):
            pass

    return waived_patterns


def is_waived(module_path: pathlib.Path, waivers: set[str]) -> bool:
    """Check if module is waived."""
    module_str = str(module_path).replace("\\", "/")

    for pattern in waivers:
        pattern_norm = pattern.replace("\\", "/")
        if fnmatch.fnmatch(module_str, pattern_norm):
            return True

    return False


def main():
    """Execute discovery with deterministic output."""
    # 1) Enumerate modules
    modules = enumerate_modules()

    # 2) Enumerate existing tests
    tests = enumerate_tests()

    # 3) Compute status for each module
    status_counts = {"PRESENT": 0, "MISSING": 0, "MISLOCATED": 0, "WAIVED": 0}
    module_status = []
    waivers = load_waivers()

    for module in modules:
        status = check_test_status(module, tests)

        # Check if waived
        if is_waived(module, waivers):
            status = "WAIVED"

        status_counts[status] += 1
        module_status.append(
            {
                "module": str(module),
                "expected_test": str(compute_expected_test_path(module)),
                "status": status,
            },
        )

    # 4) Generate integrity hash
    module_list_str = json.dumps([str(m) for m in modules], sort_keys=True)
    integrity_hash = hashlib.sha256(module_list_str.encode()).hexdigest()

    # 5) Persist deterministic output
    snapshot = {
        "timestamp": "2026-02-09T06:47:00Z",
        "integrity_hash": integrity_hash,
        "total_modules": len(modules),
        "total_tests": len(tests),
        "status_counts": status_counts,
        "modules": module_status,
    }

    # Ensure directory exists
    output_path = pathlib.Path("tests/_contracts/mirror_discovery_snapshot.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(snapshot, f, indent=2)

    print(f"Discovery snapshot created: {output_path}")
    print(f"Modules: {len(modules)}, Tests: {len(tests)}")
    print(f"Status: {status_counts}")

    return snapshot


if __name__ == "__main__":
    main()
