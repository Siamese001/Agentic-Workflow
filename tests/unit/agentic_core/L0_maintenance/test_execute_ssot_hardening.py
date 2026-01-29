#!/usr/bin/env python3
"""
Ultra-Hardened Test Suite for PreFlightValidator
Tests contract enforcement, signature validation, and instantiation guards.
"""

import inspect
import sys
from pathlib import Path
from unittest.mock import patch

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from agentic_core.L0_maintenance.scripts.execute_ssot import PreFlightValidator


class MockLegacyAgent:
    """Agent with legacy heal(path: str) signature - should be flagged."""

    def heal(self, path: str):
        return {"status": "success"}


class MockValidAgent:
    """Agent with correct heal(violation: dict) signature - should pass."""

    def heal(self, violation: dict):
        return {"status": "success"}


class MockBrokenInitAgent:
    """Agent that fails instantiation - should be caught."""

    def __init__(self, project_root):
        raise ImportError("Missing critical dependency X")


class MockNoHealAgent:
    """Agent without heal method - should be flagged."""

    def run(self):
        pass


class MockInvalidSignatureAgent:
    """Agent with invalid signature - should be flagged."""

    def heal(self, wrong_param, another_param):
        return {"status": "success"}


class MockNamingAgentWithoutMixin:
    """NamingAgent missing SubatomicTestingMixin - should be flagged."""

    def heal(self, violation: dict):
        return {"status": "success"}


class MockNamingAgentWithMixin:
    """Valid NamingAgent with proper mixin - should pass."""

    def heal(self, violation: dict):
        return {"status": "success"}


def test_preflight_catches_legacy_signature():
    """Verify that heal(path: str) is flagged as an error."""
    validator = PreFlightValidator(project_root=Path.cwd())
    agents = {"LegacyAgent": MockLegacyAgent()}
    errors = validator.validate_agent_integrity(agents)

    assert any("LEGACY SIGNATURE" in err for err in errors), (
        f"FAILED: Preflight did not catch legacy signature. Errors: {errors}"
    )
    print("✅ Test Case 1: Legacy Signature Detection - 100% PASS")


def test_preflight_allows_valid_signature():
    """Verify that heal(violation: dict) passes."""
    validator = PreFlightValidator(project_root=Path.cwd())
    agents = {"ValidAgent": MockValidAgent()}
    errors = validator.validate_agent_integrity(agents)

    assert len(errors) == 0, f"FAILED: Valid agent flagged with errors: {errors}"
    print("✅ Test Case 2: Valid Signature Acceptance - 100% PASS")


def test_preflight_catches_instantiation_failure():
    """Verify that broken imports/init are caught."""
    validator = PreFlightValidator(project_root=Path.cwd())
    agents = {"BrokenAgent": MockBrokenInitAgent}
    errors = validator.validate_agent_integrity(agents)

    assert any("FAILED INSTANTIATION" in err for err in errors), (
        f"FAILED: Did not catch init error. Errors: {errors}"
    )
    print("✅ Test Case 3: Instantiation Guard - 100% PASS")


def test_preflight_missing_heal_method():
    """Verify that agents without 'heal' are blocked."""
    validator = PreFlightValidator(project_root=Path.cwd())
    agents = {"NoHeal": MockNoHealAgent()}
    errors = validator.validate_agent_integrity(agents)

    assert any("Missing 'heal' method" in err for err in errors), (
        f"FAILED: Did not catch missing heal method. Errors: {errors}"
    )
    print("✅ Test Case 4: Missing Hook Guard - 100% PASS")


def test_preflight_catches_invalid_signature():
    """Verify that agents with incorrect signatures are flagged."""
    validator = PreFlightValidator(project_root=Path.cwd())
    agents = {"InvalidSignature": MockInvalidSignatureAgent()}
    errors = validator.validate_agent_integrity(agents)

    assert any("INVALID SIGNATURE" in err for err in errors), (
        f"FAILED: Did not catch invalid signature. Errors: {errors}"
    )
    print("✅ Test Case 5: Invalid Signature Detection - 100% PASS")


def test_preflight_naming_agent_mixin_validation():
    """Verify that NamingAgent mixin requirements are enforced."""
    validator = PreFlightValidator(project_root=Path.cwd())

    # Mock the MRO to simulate missing mixin
    with patch.object(inspect, "getmro", return_value=(MockNamingAgentWithoutMixin, object)):
        agents = {"NamingAgent": MockNamingAgentWithoutMixin()}
        errors = validator.validate_agent_integrity(agents)

        assert any("missing mandatory SubatomicTestingMixin" in err for err in errors), (
            f"FAILED: Did not catch missing mixin. Errors: {errors}"
        )

    print("✅ Test Case 6: NamingAgent Mixin Validation - 100% PASS")


def test_preflight_mixed_agent_validation():
    """Test validation with mixed valid/invalid agents."""
    validator = PreFlightValidator(project_root=Path.cwd())
    agents = {
        "ValidAgent": MockValidAgent(),
        "LegacyAgent": MockLegacyAgent(),
        "NoHeal": MockNoHealAgent(),
        "BrokenAgent": MockBrokenInitAgent,
    }
    errors = validator.validate_agent_integrity(agents)

    # Should have errors for 3 invalid agents but not for ValidAgent
    assert len(errors) >= 3, f"FAILED: Expected at least 3 errors, got {len(errors)}: {errors}"

    # Verify specific error types are present
    error_str = " ".join(errors)
    assert "LEGACY SIGNATURE" in error_str, "Missing legacy signature error"
    assert "Missing 'heal' method" in error_str, "Missing heal method error"
    assert "FAILED INSTANTIATION" in error_str, "Missing instantiation error"

    print("✅ Test Case 7: Mixed Agent Validation - 100% PASS")


def test_windows_long_paths_check():
    """Test Windows Long Paths validation."""
    validator = PreFlightValidator(project_root=Path.cwd())

    # Mock Windows platform
    with patch("platform.system", return_value="Windows"):
        # Mock successful registry check
        with (
            patch("winreg.OpenKey") as mock_open,
            patch("winreg.QueryValueEx", return_value=(1, None)),
        ):
            success, errors = validator.run_checks()
            assert success, f"Windows LongPaths check failed unexpectedly: {errors}"

        # Mock failed registry check
        with (
            patch("winreg.OpenKey") as mock_open,
            patch("winreg.QueryValueEx", return_value=(0, None)),
        ):
            success, errors = validator.run_checks()
            assert not success
            assert any("LongPathsEnabled is NOT active" in err for err in errors)

    print("✅ Test Case 8: Windows Long Paths Check - 100% PASS")


def test_directory_structure_validation():
    """Test critical directory structure validation."""
    validator = PreFlightValidator(project_root=Path.cwd())

    # Mock missing directory
    with patch.object(Path, "exists", return_value=False):
        success, errors = validator.run_checks()
        assert not success
        assert any("Critical directory missing" in err for err in errors)

    print("✅ Test Case 9: Directory Structure Validation - 100% PASS")


def test_write_permissions_check():
    """Test write permissions validation."""
    validator = PreFlightValidator(project_root=Path.cwd())

    # Mock write permission failure
    with patch.object(Path, "touch", side_effect=OSError("Permission denied")):
        success, errors = validator.run_checks()
        assert not success
        assert any("not writable" in err for err in errors)

    print("✅ Test Case 10: Write Permissions Check - 100% PASS")


if __name__ == "__main__":
    print("🧪 ULTRA-HARDENED PRE-FLIGHT VALIDATOR TEST SUITE")
    print("=" * 60)

    # Run all test cases
    test_preflight_catches_legacy_signature()
    test_preflight_allows_valid_signature()
    test_preflight_catches_instantiation_failure()
    test_preflight_missing_heal_method()
    test_preflight_catches_invalid_signature()
    test_preflight_naming_agent_mixin_validation()
    test_preflight_mixed_agent_validation()
    test_windows_long_paths_check()
    test_directory_structure_validation()
    test_write_permissions_check()

    print("=" * 60)
    print("🎉 ALL TESTS PASSED - ULTRA-HARDENING VERIFIED")
    print("✨ PreFlightValidator is ready for production deployment")
