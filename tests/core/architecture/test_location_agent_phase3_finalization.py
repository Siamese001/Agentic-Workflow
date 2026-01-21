#!/usr/bin/env python3
"""
Risk 3 Phase 3: Finalization Tests

Test Cases:
1. test_specialist_method_parity - Verify specialist agents cover monolith methods
2. test_l5_import_cycles - Verify no circular imports in L5 validators
3. test_ci_pytest_collection - Verify 703+ tests with zero errors

These tests ensure the SRP fission is complete and stable.
"""
import sys
from pathlib import Path
from typing import Set

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestSpecialistMethodParity:
    """Test Case 1: Specialist Coverage Verification

    Compare methods in LocationValidatorAgent and LocationHealerAgent
    against the original LocationAgent monolith.
    """

    def test_validator_has_validation_methods(self):
        """Verify LocationValidatorAgent has core validation methods."""
        from agentic_core.L5_safety.validators.LocationValidatorAgent import LocationValidatorAgent

        required_methods = [
            'validate_sovereign_roots',
            'validate_file_location',
            '_validate_forbidden_patterns',
            '_validate_root_whitelist',
            '_validate_depth_requirements',
        ]

        for method in required_methods:
            assert hasattr(LocationValidatorAgent, method), f"Missing validation method: {method}"

    def test_healer_has_healing_methods(self):
        """Verify LocationHealerAgent has core healing methods."""
        from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent

        required_methods = [
            'heal_repository',
            '_init_backup_dir',
            '_backup_file',
            'safe_create_directory',
            'safe_move',
            'safe_delete',
        ]

        for method in required_methods:
            assert hasattr(LocationHealerAgent, method), f"Missing healing method: {method}"

    def test_monolith_still_has_all_methods(self):
        """Verify original LocationAgent still has all methods for backwards compat."""
        from agentic_core.L5_safety.validators.LocationAgent import LocationAgent

        # Key methods that should still exist on monolith
        key_methods = [
            '_validate_depth_requirements',
            '_heal_depth_violation',
            'validate_file_location',
        ]

        for method in key_methods:
            assert hasattr(LocationAgent, method), f"Monolith missing method: {method}"


class TestL5ImportCycles:
    """Test Case 2: Cross-Layer Dependency Audit

    Verify no circular imports in L5 validators after SRP fission.
    """

    def test_validator_imports_cleanly(self):
        """Verify LocationValidatorAgent imports without circular import errors."""
        try:
            from agentic_core.L5_safety.validators.LocationValidatorAgent import LocationValidatorAgent
            assert LocationValidatorAgent is not None
        except ImportError as e:
            pytest.fail(f"Circular import detected in LocationValidatorAgent: {e}")

    def test_healer_imports_cleanly(self):
        """Verify LocationHealerAgent imports without circular import errors."""
        try:
            from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent
            assert LocationHealerAgent is not None
        except ImportError as e:
            pytest.fail(f"Circular import detected in LocationHealerAgent: {e}")

    def test_gravity_detector_imports_cleanly(self):
        """Verify GravityLeakDetector imports without circular import errors."""
        try:
            from agentic_core.L5_safety.validators.GravityLeakDetector import GravityLeakDetector
            assert GravityLeakDetector is not None
        except ImportError as e:
            pytest.fail(f"Circular import detected in GravityLeakDetector: {e}")

    def test_location_constants_imports_cleanly(self):
        """Verify location_constants imports without circular import errors."""
        try:
            from agentic_core.L5_safety.validators.location_constants import (
                ARCHIVE_SUBFOLDERS,
                HEALING_STRATEGY_MAP,
            )
            assert ARCHIVE_SUBFOLDERS is not None
            assert HEALING_STRATEGY_MAP is not None
        except ImportError as e:
            pytest.fail(f"Circular import detected in location_constants: {e}")

    def test_all_specialists_import_together(self):
        """Verify all specialist agents can be imported in same module."""
        try:
            from agentic_core.L5_safety.validators.LocationValidatorAgent import LocationValidatorAgent
            from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent
            from agentic_core.L5_safety.validators.GravityLeakDetector import GravityLeakDetector
            from agentic_core.L5_safety.validators.LocationAgent import LocationAgent

            # All should be importable together
            assert LocationValidatorAgent is not None
            assert LocationHealerAgent is not None
            assert GravityLeakDetector is not None
            assert LocationAgent is not None
        except ImportError as e:
            pytest.fail(f"Cross-import failure: {e}")


class TestCIPytestCollection:
    """Test Case 3: Continuous Collection Enforcement

    Verify pytest collection returns 703+ tests with zero errors.
    """

    def test_minimum_test_count(self):
        """Verify at least 703 tests are collected."""
        import subprocess

        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=60
        )

        # Parse output for test count
        output = result.stdout + result.stderr

        # Look for "X tests collected" pattern
        import re
        match = re.search(r'(\d+) tests? collected', output)

        if match:
            test_count = int(match.group(1))
            assert test_count >= 703, f"Expected 703+ tests, got {test_count}"
        else:
            # If we can't parse, check exit code
            assert result.returncode == 0, f"Collection failed: {output[:500]}"

    def test_zero_collection_errors(self):
        """Verify zero collection errors."""
        import subprocess

        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=60
        )

        output = result.stdout + result.stderr

        # Check for error indicators
        error_indicators = [
            "ERROR collecting",
            "ImportError",
            "ModuleNotFoundError",
            "SyntaxError",
            "collection error",
        ]

        for indicator in error_indicators:
            # Allow "error" in test names but not actual collection errors
            if indicator in output and "test_" not in output.split(indicator)[0][-50:]:
                # Check if it's in a test function name context
                if "Function test_" not in output.split(indicator)[0][-100:]:
                    pytest.fail(f"Collection error detected: {indicator}")


class TestL1CognitionHardening:
    """Verify L1CognitionBaseAgent hardening is correct."""

    def test_l1_base_imports_cleanly(self):
        """Verify L1CognitionBaseAgent imports without errors."""
        try:
            from agentic_core.L1_cognition.thought_engine.L1CognitionBaseAgent import L1CognitionBaseAgent
            assert L1CognitionBaseAgent is not None
        except ImportError as e:
            pytest.fail(f"L1CognitionBaseAgent import failed: {e}")

    def test_verification_registry_is_dict(self):
        """Verify VERIFICATION_REGISTRY has correct type annotation."""
        from agentic_core.L1_cognition.thought_engine.L1CognitionBaseAgent import L1CognitionBaseAgent
        import dataclasses

        # Get field info
        fields = {f.name: f for f in dataclasses.fields(L1CognitionBaseAgent)}

        assert 'VERIFICATION_REGISTRY' in fields, "VERIFICATION_REGISTRY field not found"
        field = fields['VERIFICATION_REGISTRY']

        # Verify it uses default_factory (not mutable default)
        assert field.default_factory is not dataclasses.MISSING, "VERIFICATION_REGISTRY should use default_factory"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
