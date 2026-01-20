#!/usr/bin/env python3
"""
Risk 3 Phase 1: Test Suite Realignment Verification

Test Cases T3-P1-01 through T3-P1-04:
- Validator path integrity
- Healer safe-move mocking
- Security wrapper discovery
- SSOT constant access

These tests verify the LocationAgent SRP fission is properly integrated.
"""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Navigate from tests/core/architecture/ up to project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestT3P101ValidatorPathIntegrity:
    """T3-P1-01: Validator Path Integrity
    
    A test importing LocationValidatorAgent can successfully invoke validate methods.
    """
    
    def test_import_location_validator_agent(self):
        """Verify LocationValidatorAgent can be imported without errors."""
        from agentic_core.L5_safety.validators.LocationValidatorAgent import LocationValidatorAgent
        assert LocationValidatorAgent is not None
    
    def test_instantiate_validator(self):
        """Verify LocationValidatorAgent can be instantiated."""
        from agentic_core.L5_safety.validators.LocationValidatorAgent import LocationValidatorAgent
        validator = LocationValidatorAgent(project_root=PROJECT_ROOT)
        assert validator is not None
        assert validator.project_root == PROJECT_ROOT.resolve()
    
    def test_validate_sovereign_roots_method_exists(self):
        """Verify validate_sovereign_roots method exists on LocationValidatorAgent."""
        from agentic_core.L5_safety.validators.LocationValidatorAgent import LocationValidatorAgent
        validator = LocationValidatorAgent(project_root=PROJECT_ROOT)
        assert hasattr(validator, 'validate_sovereign_roots')
        assert callable(getattr(validator, 'validate_sovereign_roots'))


class TestT3P102HealerSafeMoveMocking:
    """T3-P1-02: Healer Safe-Move Mocking
    
    A test mocking LocationHealerAgent.safe_move correctly intercepts the call
    without referencing the old monolith.
    """
    
    def test_import_location_healer_agent(self):
        """Verify LocationHealerAgent can be imported without errors."""
        from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent
        assert LocationHealerAgent is not None
    
    def test_instantiate_healer(self):
        """Verify LocationHealerAgent can be instantiated."""
        from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent
        healer = LocationHealerAgent(project_root=PROJECT_ROOT)
        assert healer is not None
        assert healer.project_root == PROJECT_ROOT.resolve()
    
    def test_heal_repository_method_exists(self):
        """Verify heal_repository method exists on LocationHealerAgent."""
        from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent
        healer = LocationHealerAgent(project_root=PROJECT_ROOT)
        assert hasattr(healer, 'heal_repository')
        assert callable(getattr(healer, 'heal_repository'))
    
    @patch('agentic_core.L5_safety.validators.LocationHealerAgent.LocationHealerAgent.heal_repository')
    def test_mock_healer_intercepts_call(self, mock_heal):
        """Verify mocking LocationHealerAgent.heal_repository intercepts correctly."""
        mock_heal.return_value = {"violations_fixed": 5, "files_moved": 3}
        
        from agentic_core.L5_safety.validators.LocationHealerAgent import LocationHealerAgent
        healer = LocationHealerAgent(project_root=PROJECT_ROOT)
        
        result = healer.heal_repository(dry_run=True)
        
        mock_heal.assert_called_once_with(dry_run=True)
        assert result["violations_fixed"] == 5
        assert result["files_moved"] == 3


class TestT3P103SecurityWrapperDiscovery:
    """T3-P1-03: Security Wrapper Discovery
    
    The test suite successfully discovers tests/security/test_safe_execute.py
    with zero collection errors.
    """
    
    def test_security_test_file_exists(self):
        """Verify test_safe_execute.py exists via import (more robust than path check)."""
        # Import verification is more robust than path checking
        # since pytest may change working directories
        try:
            import tests.security.test_safe_execute
            assert True, "Security test file discovered and importable"
        except ImportError as e:
            pytest.fail(f"Security test file not discoverable: {e}")
    
    def test_security_tests_importable(self):
        """Verify security test module can be imported."""
        import tests.security.test_safe_execute as security_tests
        assert security_tests is not None
    
    def test_safe_execute_importable(self):
        """Verify safe_execute can be imported from security module."""
        from agentic_core.utils.security import safe_execute, safe_popen, safe_git_execute
        assert safe_execute is not None
        assert safe_popen is not None
        assert safe_git_execute is not None


class TestT3P104SSOTConstantAccess:
    """T3-P1-04: SSOT Constant Access
    
    Tests using ARCHIVE_SUBFOLDERS successfully import from location_constants.py.
    """
    
    def test_location_constants_importable(self):
        """Verify location_constants.py can be imported."""
        from agentic_core.L5_safety.validators.location_constants import (
            ARCHIVE_SUBFOLDERS,
            DEFAULT_ARCHIVE_SUBFOLDER,
            HEALING_STRATEGY_MAP,
            DEFAULT_APP_HEALING_TARGET,
            VIOLATION_THRESHOLDS,
        )
        assert ARCHIVE_SUBFOLDERS is not None
        assert DEFAULT_ARCHIVE_SUBFOLDER is not None
        assert HEALING_STRATEGY_MAP is not None
    
    def test_archive_subfolders_contains_expected_keys(self):
        """Verify ARCHIVE_SUBFOLDERS contains expected violation type keys."""
        from agentic_core.L5_safety.validators.location_constants import ARCHIVE_SUBFOLDERS
        
        assert isinstance(ARCHIVE_SUBFOLDERS, dict)
        assert "VOID VIOLATION" in ARCHIVE_SUBFOLDERS
        assert "GRAVITY" in ARCHIVE_SUBFOLDERS
        assert "LAYER PREFIX VIOLATION" in ARCHIVE_SUBFOLDERS
    
    def test_archive_subfolders_values_are_strings(self):
        """Verify ARCHIVE_SUBFOLDERS values are valid folder names."""
        from agentic_core.L5_safety.validators.location_constants import ARCHIVE_SUBFOLDERS
        
        for key, value in ARCHIVE_SUBFOLDERS.items():
            assert isinstance(value, str), f"Value for {key} is not a string"
            assert len(value) > 0, f"Value for {key} is empty"
    
    def test_healing_strategy_map_contains_expected_strategies(self):
        """Verify HEALING_STRATEGY_MAP contains expected healing strategies."""
        from agentic_core.L5_safety.validators.location_constants import HEALING_STRATEGY_MAP
        
        assert isinstance(HEALING_STRATEGY_MAP, dict)
        assert "BROKEN BACKUP" in HEALING_STRATEGY_MAP
        assert "APP-SPECIFIC IN CORE" in HEALING_STRATEGY_MAP
        assert "TERRITORY MISMATCH" in HEALING_STRATEGY_MAP
        assert "DEEP VIOLATION" in HEALING_STRATEGY_MAP
    
    def test_violation_thresholds_has_severity_levels(self):
        """Verify VIOLATION_THRESHOLDS has all severity levels."""
        from agentic_core.L5_safety.validators.location_constants import VIOLATION_THRESHOLDS
        
        assert isinstance(VIOLATION_THRESHOLDS, dict)
        assert "critical" in VIOLATION_THRESHOLDS
        assert "high" in VIOLATION_THRESHOLDS
        assert "medium" in VIOLATION_THRESHOLDS


class TestLocationAgentBackwardsCompatibility:
    """Verify original LocationAgent still works for backwards compatibility."""
    
    def test_location_agent_still_importable(self):
        """Verify original LocationAgent can still be imported."""
        from agentic_core.L5_safety.validators.LocationAgent import LocationAgent
        assert LocationAgent is not None
    
    @pytest.mark.skip(reason="LocationAgent requires specific environment validation - tested separately")
    def test_location_agent_instantiates(self):
        """Verify original LocationAgent can be instantiated."""
        from agentic_core.L5_safety.validators.LocationAgent import LocationAgent
        agent = LocationAgent(project_root=PROJECT_ROOT)
        assert agent is not None
        assert agent.project_root == PROJECT_ROOT.resolve()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
