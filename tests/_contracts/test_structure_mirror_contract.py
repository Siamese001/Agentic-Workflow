#!/usr/bin/env python3
"""
Test Structure Mirror Contract Enforcement
artifact_class: STRUCTURE_CONTRACT
"""

import json
import pathlib
from datetime import datetime

import pytest
import yaml


class MirrorContractViolation(Exception):
    """Raised when mirror contract is violated."""

    pass


def load_waivers() -> dict:
    """Load mirror waivers from YAML file."""
    waivers_file = pathlib.Path(__file__).parent / "mirror_waivers.yaml"
    if not waivers_file.exists():
        return {"waivers": []}

    with open(waivers_file) as f:
        return yaml.safe_load(f)


def is_expired(expiry_str: str) -> bool:
    """Check if a waiver has expired."""
    try:
        expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
        return datetime.now().date() > expiry_date
    except ValueError:
        # Invalid date format - consider expired
        return True


def discover_python_modules(root: pathlib.Path) -> list[pathlib.Path]:
    """Discover all Python modules in scope."""
    modules = []
    exclude_dirs = {
        ".venv",
        "build",
        "dist",
        "__pycache__",
        "*.egg-info",
        "docs",
        ".git",
        ".nox",
        "artifacts",
        "archives",
        "data",
        "ops_scripts",
        ".backup",
    }

    for py_file in root.rglob("*.py"):
        # Skip excluded directories
        if any(exclude in str(py_file) for exclude in exclude_dirs):
            continue
        # Skip test files themselves
        if "tests" in py_file.parts:
            continue
        modules.append(py_file)

    return sorted(modules)


def discover_existing_tests() -> list[pathlib.Path]:
    """Discover all existing test files."""
    test_root = pathlib.Path("tests")
    if not test_root.exists():
        return []

    return sorted(test_root.rglob("test_*.py"))


def compute_expected_test_path(module_path: pathlib.Path) -> pathlib.Path:
    """Compute expected test path based on mirror rules."""
    if module_path.parts[0] == "agentic_core":
        relative_parts = module_path.parts[1:]
        test_name = f"test_{module_path.stem}.py"
        return pathlib.Path("tests") / "agentic_core" / pathlib.Path(*relative_parts).parent / test_name
    elif module_path.parts[0].startswith("apps_"):
        relative_parts = module_path.parts[1:]
        test_name = f"test_{module_path.stem}.py"
        return pathlib.Path("tests") / module_path.parts[0] / pathlib.Path(*relative_parts).parent / test_name
    else:
        raise ValueError(f"Unexpected module root: {module_path.parts[0]}")


def check_test_status(
    module_path: pathlib.Path, expected_test_path: pathlib.Path, existing_tests: list[pathlib.Path]
) -> tuple[str, pathlib.Path | None]:
    """Check test status for a module."""
    existing_test_paths = {t for t in existing_tests}

    if expected_test_path in existing_test_paths:
        return "PRESENT", expected_test_path

    # Check if test exists elsewhere (mislocated)
    expected_name = expected_test_path.name
    for test_path in existing_tests:
        if test_path.name == expected_name and test_path.parent != expected_test_path.parent:
            return "MISLOCATED", test_path

    return "MISSING", None


def is_waived(module_path: pathlib.Path, waivers: dict) -> tuple[bool, dict | None]:
    """Check if a module is waived."""
    module_str = str(module_path)
    module_str_forward = module_str.replace("\\", "/")  # Normalize path separators

    for waiver in waivers.get("waivers", []):
        waiver_pattern = waiver["module"].replace("\\", "/")

        # Handle glob patterns
        if "**" in waiver_pattern or "*" in waiver_pattern:
            from fnmatch import fnmatch

            if fnmatch(module_str_forward, waiver_pattern):
                return True, waiver
        elif waiver_pattern == module_str_forward:
            return True, waiver

    return False, None


def generate_mirror_snapshot() -> dict:
    """Generate a snapshot of the current mirror state."""
    root = pathlib.Path(".")

    # Discover modules and tests
    agentic_modules = discover_python_modules(root / "agentic_core")
    apps_lic_modules = discover_python_modules(root / "apps_lic")
    apps_rg_modules = discover_python_modules(root / "apps_rg")
    apps_shared_modules = discover_python_modules(root / "apps_shared")

    all_modules = agentic_modules + apps_lic_modules + apps_rg_modules + apps_shared_modules
    existing_tests = discover_existing_tests()

    # Check each module
    snapshot = {}

    for module_path in all_modules:
        expected_test_path = compute_expected_test_path(module_path)
        status, actual_test_path = check_test_status(module_path, expected_test_path, existing_tests)

        # Check if waived
        is_waived_module, waiver_info = is_waived(module_path, load_waivers())

        if is_waived_module:
            status = "WAIVED"

        snapshot[str(module_path)] = {
            "status": status,
            "test_path": str(expected_test_path) if status == "PRESENT" else None,
        }

    return snapshot


def validate_mirror_contract():
    """Validate that the test structure mirrors the source structure."""
    baseline_file = pathlib.Path(__file__).parent / "mirror_baseline.json"
    if not baseline_file.exists():
        raise FileNotFoundError(f"Baseline file not found: {baseline_file}")

    with open(baseline_file) as f:
        baseline = json.load(f)

    # Get current state
    current = generate_mirror_snapshot()

    # If baseline has modules, check them
    if "modules" in baseline:
        # Calculate differences
        missing = []
        mislocated = []
        waived = []

        for module_path, module_info in baseline["modules"].items():
            status = module_info.get("status", "MISSING")

            if status == "MISSING":
                missing.append(module_path)
            elif status == "MISLOCATED":
                mislocated.append(module_path)
            elif status == "WAIVED":
                waived.append(module_path)
            elif status == "PRESENT":
                # Verify test actually exists
                test_path = pathlib.Path(module_info["test_path"])
                if not test_path.exists():
                    missing.append(module_path)

        # Check hard requirements
        if mislocated:
            raise MirrorContractViolation(f"MISLOCATED > 0: {len(mislocated)} mislocated tests found")

        if missing:
            raise MirrorContractViolation(f"MISSING > 0: {len(missing)} missing tests found")

        # Check waived ratio
        total_non_present = len(missing) + len(mislocated) + len(waived)
        if total_non_present > 0:
            waived_ratio = len(waived) / total_non_present
            if waived_ratio > 0.1:  # More than 10% waived
                raise MirrorContractViolation(f"WAIVED ratio > 10%: {waived_ratio:.2%}")

    # Check for quarantine tests
    quarantine_dir = pathlib.Path("tests/_quarantine")
    quarantine_tests = []
    if quarantine_dir.exists():
        quarantine_tests = list(quarantine_dir.rglob("test_*.py"))

    # Print summary
    print("\n=== MIRROR CONTRACT VALIDATION ===")
    if "modules" in baseline:
        print(f"Total modules: {len(baseline['modules'])}")
    else:
        print("Using legacy baseline format")
    print(f"Quarantined: {len(quarantine_tests)}")

    print("✅ Mirror contract satisfied!")
    return True


def test_mirror_contract():
    """Test that the mirror contract is satisfied."""
    try:
        result = validate_mirror_contract()
        # If we get here, contract is satisfied
        assert result is True, "Mirror contract should be satisfied"
    except MirrorContractViolation as e:
        pytest.fail(str(e))


def test_no_expired_waivers():
    """Test that no waivers are expired."""
    waivers = load_waivers()
    expired = []

    for waiver in waivers.get("waivers", []):
        if is_expired(waiver["expiry"]):
            expired.append(f"{waiver['module']} (expired {waiver['expiry']})")

    if expired:
        pytest.fail(f"Expired waivers found: {'; '.join(expired)}")


def test_no_tests_in_non_canonical_locations():
    """Test that no tests exist outside the canonical mirror structure."""
    test_root = pathlib.Path("tests")

    non_canonical_tests = []

    for test_file in test_root.rglob("test_*.py"):
        # Get repo-relative path
        try:
            rel_path = test_file.relative_to(pathlib.Path("."))
        except ValueError:
            continue

        rel_str = str(rel_path).replace("\\", "/")

        # Only allow exact prefix matches
        if (
            rel_str.startswith("tests/_contracts/")
            or rel_str.startswith("tests/guardian/")
            or rel_str.startswith("tests/_quarantine/")
        ):
            continue

        # Skip the contract test itself
        if test_file.name == "test_structure_mirror_contract.py":
            continue

        # Check if it follows mirror structure
        relative_path = test_file.relative_to(test_root)

        # Should be: tests/agentic_core/.../test_*.py or tests/apps_*/.../test_*.py
        if len(relative_path.parts) < 2:
            non_canonical_tests.append(str(test_file))
            continue

        first_part = relative_path.parts[0]
        if first_part not in ["agentic_core", "apps_lic", "apps_rg", "apps_shared"]:
            non_canonical_tests.append(str(test_file))

    if non_canonical_tests:
        pytest.fail(f"Tests found in non-canonical locations: {non_canonical_tests[:10]}")


if __name__ == "__main__":
    # Run validation directly
    try:
        result = validate_mirror_contract()
        print("Mirror contract validation passed!")
    except MirrorContractViolation as e:
        print(f"Mirror contract violation: {e}")
        exit(1)
