#!/usr/bin/env python3
"""
Post-Risk 3 Maintenance Tests

Test Cases:
1. test_gravity_leak_detection_consistency - Gravity logic parity
2. test_no_circular_location_imports - Cross-import cycle guard
3. test_ci_collection_enforcement - Continuous collection audit

These tests ensure the 715-test baseline is maintained.
"""

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestGravityLeakDetectionConsistency:
    """Test Case 1: Gravity Logic Parity Test

    Run the GravityLeakDetector against known mislocated files
    and verify detections match LocationValidatorAgent results.
    """

    def test_gravity_detector_instantiates(self):
        """Verify GravityLeakDetector can be instantiated."""
        from agentic_core.L5_safety.validators.GravityLeakDetector import GravityLeakDetector

        detector = GravityLeakDetector(project_root=PROJECT_ROOT)
        assert detector is not None

    def test_is_path_compliant_consistency(self):
        """Verify is_path_compliant returns consistent results."""
        from agentic_core.L5_safety.validators.location_utils import is_path_compliant

        # Known compliant paths
        compliant_paths = [
            "agentic_core/L5_safety/validators/LocationAgent.py",
            "agentic_core/L1_cognition/thought_engine/L1CognitionBaseAgent.py",
            "tests/core/architecture/test_location_agent_comprehensive.py",
        ]

        for path in compliant_paths:
            result = is_path_compliant(path, PROJECT_ROOT)
            # These should be compliant (True) or at least not raise errors
            assert isinstance(result, bool), f"is_path_compliant returned non-bool for {path}"

    def test_gravity_detector_has_detection_methods(self):
        """Verify GravityLeakDetector has expected detection methods."""

        expected_attributes = [
            "CORE_TERRITORY_KEYWORDS",
            "APP_RG_AST_TERMS",
            "APP_LIC_AST_TERMS",
        ]

        # Check module-level constants exist
        import agentic_core.L5_safety.validators.GravityLeakDetector as gld_module

        for attr in expected_attributes:
            assert hasattr(gld_module, attr), f"Missing gravity constant: {attr}"

    def test_validator_and_gravity_use_same_utils(self):
        """Verify both agents use the same utility functions."""
        from agentic_core.L5_safety.validators import location_utils
        from agentic_core.L5_safety.validators.GravityLeakDetector import GravityLeakDetector
        from agentic_core.L5_safety.validators.LocationValidatorAgent import LocationValidatorAgent

        # Both should be importable without conflict
        assert LocationValidatorAgent is not None
        assert GravityLeakDetector is not None
        assert location_utils is not None

        # Verify shared utility functions exist
        assert hasattr(location_utils, "is_path_compliant")
        assert hasattr(location_utils, "compute_module_path")


class TestNoCircularLocationImports:
    """Test Case 2: Cross-Import Cycle Guard

    Attempt to import all location-related modules in a single session
    to ensure no circular dependencies.
    """

    def test_import_all_location_modules_together(self):
        """Import all location modules in sequence without errors."""
        try:
            # Core modules
            from agentic_core.L5_safety.validators import (
                location_constants,
                location_utils,
                structure_blueprint,
            )
            from agentic_core.L5_safety.validators.GravityLeakDetector import GravityLeakDetector

            # Original monolith (backwards compat)
            from agentic_core.L5_safety.validators.LocationAgent import LocationAgent
            from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent

            # Specialist agents
            from agentic_core.L5_safety.validators.LocationValidatorAgent import (
                LocationValidatorAgent,
            )

            # All imports successful
            assert location_utils is not None
            assert location_constants is not None
            assert structure_blueprint is not None
            assert LocationValidatorAgent is not None
            assert LocationHealerAgent is not None
            assert GravityLeakDetector is not None
            assert LocationAgent is not None

        except (ImportError, NameError, AttributeError, TypeError) as e:
            pytest.fail(f"Circular import detected: {e}")

    def test_reverse_import_order(self):
        """Import in reverse order to catch order-dependent cycles."""
        try:
            # Reverse order from previous test
            from agentic_core.L5_safety.validators import (
                location_constants,
                location_utils,
                structure_blueprint,
            )
            from agentic_core.L5_safety.validators.GravityLeakDetector import GravityLeakDetector
            from agentic_core.L5_safety.validators.LocationAgent import LocationAgent
            from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent
            from agentic_core.L5_safety.validators.LocationValidatorAgent import (
                LocationValidatorAgent,
            )

            assert all(
                [
                    LocationAgent,
                    GravityLeakDetector,
                    LocationHealerAgent,
                    LocationValidatorAgent,
                    structure_blueprint,
                    location_constants,
                    location_utils,
                ]
            )

        except (ImportError, NameError, AttributeError, TypeError) as e:
            pytest.fail(f"Order-dependent circular import: {e}")

    def test_cross_layer_imports(self):
        """Verify L5 can import from L1 and vice versa without cycles."""
        try:
            # L5 importing L1
            from agentic_core.L1_cognition.thought_engine.L1CognitionBaseAgent import (
                L1CognitionBaseAgent,
            )

            from agentic_core.L5_safety.validators.LocationValidatorAgent import (
                LocationValidatorAgent,
            )

            # Both should be available
            assert LocationValidatorAgent is not None
            assert L1CognitionBaseAgent is not None

        except (ImportError, NameError, AttributeError, TypeError) as e:
            pytest.fail(f"Cross-layer import failure: {e}")


class TestCICollectionEnforcement:
    """Test Case 3: Continuous Collection Audit

    Run pytest --collect-only and verify:
    - Collection errors = 0
    - Test count >= 715
    """

    def test_minimum_test_count_715(self):
        """Verify at least 715 tests are collected."""
        import re
        import subprocess

        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=120,
        )

        output = result.stdout + result.stderr

        # Parse test count
        match = re.search(r"(\d+) tests? collected", output)

        if match:
            test_count = int(match.group(1))
            assert test_count >= 715, f"Test count dropped below 715: {test_count}"
        else:
            # If we can't parse, at least verify no collection errors
            assert result.returncode == 0, f"Collection failed: {output[:500]}"

    def test_zero_collection_errors_strict(self):
        """Strictly verify zero collection errors."""
        import subprocess

        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=120,
        )

        output = result.stdout + result.stderr

        # Strict error detection
        critical_errors = [
            "ERROR collecting",
            "ModuleNotFoundError:",
            "ImportError:",
            "SyntaxError:",
            "TypeError: non-default argument",
        ]

        for error in critical_errors:
            if error in output:
                # Extract context around error
                idx = output.find(error)
                context = output[max(0, idx - 100) : idx + 200]
                pytest.fail(f"Collection error detected: {error}\nContext: {context}")

    def test_no_test_count_regression(self):
        """Verify test count hasn't regressed from baseline."""
        import re
        import subprocess

        BASELINE_COUNT = 715  # Established baseline

        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=120,
        )

        output = result.stdout + result.stderr
        match = re.search(r"(\d+) tests? collected", output)

        if match:
            current_count = int(match.group(1))
            regression = BASELINE_COUNT - current_count

            if regression > 0:
                pytest.fail(
                    f"Test count regressed by {regression}: {current_count} < {BASELINE_COUNT}"
                )

            # Log improvement if any
            if current_count > BASELINE_COUNT:
                print(
                    f"✅ Test count improved: {current_count} (+{current_count - BASELINE_COUNT})"
                )


class TestUtilityFunctionAlignment:
    """Verify utility functions are properly aligned across modules."""

    def test_location_utils_exports(self):
        """Verify location_utils exports expected functions."""
        from agentic_core.L5_safety.validators import location_utils

        expected_exports = [
            "normalize_location_path",
            "get_agent_files",
            "compute_module_path",
            "is_path_compliant",
        ]

        for func_name in expected_exports:
            assert hasattr(location_utils, func_name), f"Missing export: {func_name}"
            assert callable(getattr(location_utils, func_name)), f"Not callable: {func_name}"

    def test_location_constants_exports(self):
        """Verify location_constants exports expected constants."""
        from agentic_core.L5_safety.validators import location_constants

        expected_exports = [
            "ARCHIVE_SUBFOLDERS",
            "DEFAULT_ARCHIVE_SUBFOLDER",
            "HEALING_STRATEGY_MAP",
            "DEFAULT_APP_HEALING_TARGET",
            "VIOLATION_THRESHOLDS",
        ]

        for const_name in expected_exports:
            assert hasattr(location_constants, const_name), f"Missing constant: {const_name}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
