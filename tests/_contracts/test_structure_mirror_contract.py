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
    module_path: pathlib.Path,
    expected_test_path: pathlib.Path,
    existing_tests: list[pathlib.Path],
) -> tuple[str, pathlib.Path | None]:
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
    """Test that no tests exist outside the canonical mirror structure.

    Policy: BASELINE-AWARE (default)
    --------------------------------
    Legacy roots that pre-date the mirror contract are allowed but frozen.
    Their file count must not increase beyond the recorded baseline.
    Set LEGACY_ROOT_POLICY = "STRICT" to disallow all non-canonical roots.
    """
    # --- Policy configuration ---------------------------------------------------
    LEGACY_ROOT_POLICY = "BASELINE-AWARE"  # "STRICT" | "BASELINE-AWARE"

    # Frozen legacy roots: {prefix: max_test_file_count}
    # Count was captured from the committed state when the policy was adopted.
    LEGACY_ROOT_BASELINES: dict[str, int] = {
        "tests/core/": 15,
        "tests/e2e/": 32,
        "tests/fixtures/": 1,
        "tests/goldens/": 1,
        "tests/integration/": 3,
        "tests/misc/": 14,
        "tests/performance/": 1,
        "tests/stress/": 1,
        "tests/unit/": 717,
        "tests/unit_min_deps/": 8,
        "tests/behavioral/": 3,
    }

    # Infrastructure / governance directories (always allowed, not mirror-scoped)
    INFRA_PREFIXES = (
        "tests/_contracts/",
        "tests/guardian/",
        "tests/_quarantine/",
    )

    # Canonical mirror roots
    CANONICAL_ROOTS = {"agentic_core", "apps_lic", "apps_rg", "apps_shared"}
    # ---------------------------------------------------------------------------

    test_root = pathlib.Path("tests")
    non_canonical_tests = []
    legacy_growth_violations = []

    # Bucket legacy root counts
    legacy_counts: dict[str, int] = dict.fromkeys(LEGACY_ROOT_BASELINES, 0)

    for test_file in test_root.rglob("test_*.py"):
        try:
            rel_path = test_file.relative_to(pathlib.Path("."))
        except ValueError:
            continue

        rel_str = str(rel_path).replace("\\", "/")

        # Always-allowed infrastructure paths
        if rel_str.startswith(INFRA_PREFIXES):
            continue

        # Skip the contract test itself
        if test_file.name == "test_structure_mirror_contract.py":
            continue

        relative_path = test_file.relative_to(test_root)

        # Canonical mirror roots are always fine
        if len(relative_path.parts) >= 2 and relative_path.parts[0] in CANONICAL_ROOTS:
            continue

        # Check against legacy roots
        matched_legacy = False
        for legacy_prefix in LEGACY_ROOT_BASELINES:
            if rel_str.startswith(legacy_prefix):
                legacy_counts[legacy_prefix] += 1
                matched_legacy = True
                break

        if matched_legacy:
            if LEGACY_ROOT_POLICY == "STRICT":
                non_canonical_tests.append(rel_str)
            # BASELINE-AWARE: counted, checked below
            continue

        # Truly non-canonical
        non_canonical_tests.append(rel_str)

    # Enforce freeze rule on legacy roots (BASELINE-AWARE only)
    if LEGACY_ROOT_POLICY == "BASELINE-AWARE":
        for prefix, baseline_max in LEGACY_ROOT_BASELINES.items():
            actual = legacy_counts.get(prefix, 0)
            if actual > baseline_max:
                legacy_growth_violations.append(
                    f"{prefix}: {actual} files (baseline max {baseline_max})",
                )

    errors = []
    if non_canonical_tests:
        errors.append(
            f"Tests in non-canonical locations: {non_canonical_tests[:10]}",
        )
    if legacy_growth_violations:
        errors.append(
            f"Legacy root growth violations (freeze rule): {legacy_growth_violations}",
        )

    if errors:
        pytest.fail(" | ".join(errors))


if __name__ == "__main__":
    # Run validation directly
    try:
        result = validate_mirror_contract()
        print("Mirror contract validation passed!")
    except MirrorContractViolation as e:
        print(f"Mirror contract violation: {e}")
        exit(1)
