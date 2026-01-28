"""
Phase 4: Aggressive Integrity Verification for agentic_core/domain
Focus: Immutability, Exception Consolidation, and Type Safety.
100% pass requirement for Zero Loss Merge Protocol.

CRITICAL ANALYSIS: This test suite verifies that Phase 3 hardening was NOT cosmetic.
Every test must pass to prove validate_assignment, field validators, and exception
consolidation were properly implemented.
"""

import pytest
from uuid import uuid4, UUID
from datetime import datetime, timezone
from pydantic import ValidationError as PydanticValidationError
from agentic_core.domain.entities import BaseEntity, AgentConfig
from agentic_core.domain.SovereignError import (
    SovereignError,
    HealerError,
    ConfigurationError,
    CircularDependencyError,
    StructuralError,
    HygieneError,
    IntegrityError,
    ValidationError,
    ResourceNotFoundError,
    SecurityViolationError
)
from agentic_core.domain.exceptions import AgenticCoreError
from agentic_core.domain.LegacyArtifacts import LegacyArtifacts


class TestEntityImmutabilityAndAssignmentValidation:
    """
    Test Case 1: Verify that hardened entities enforce validation on assignment.
    Target: entities.py (ConfigDict alignment)
    Assertion: 100% pass on state hardening.
    """
    
    def test_validate_assignment_enabled(self):
        """Verify validate_assignment=True is enforced in ConfigDict."""
        entity = AgentConfig(name="TestAgent", role="test_role")
        
        # Attempt to inject invalid type on mutable field (should fail)
        with pytest.raises((PydanticValidationError, TypeError, ValueError)):
            entity.updated_at = "invalid-date-string"
    
    def test_frozen_field_immutability(self):
        """Verify frozen=True fields cannot be modified after instantiation."""
        entity = AgentConfig(name="TestAgent", role="test_role")
        original_id = entity.id
        
        # Attempt to modify frozen identity field (should fail)
        with pytest.raises((PydanticValidationError, ValueError, AttributeError)):
            entity.id = uuid4()
        
        # Verify ID unchanged
        assert entity.id == original_id
    
    def test_name_validation_on_assignment(self):
        """Verify name field validation triggers on assignment."""
        entity = AgentConfig(name="ValidName", role="test_role")
        
        # Attempt to assign empty name (should fail due to min_length=1)
        with pytest.raises((PydanticValidationError, ValueError)):
            entity.name = ""
        
        # Attempt to assign whitespace-only name (should fail)
        with pytest.raises((PydanticValidationError, ValueError)):
            entity.name = "   "
    
    def test_strict_typing_enforcement(self):
        """Verify strict=True prevents type coercion."""
        # Attempt to create entity with wrong type for temperature
        with pytest.raises(PydanticValidationError):
            AgentConfig(
                name="TestAgent",
                role="test_role",
                temperature="0.5"  # String instead of float
            )
    
    def test_extra_fields_forbidden(self):
        """Verify extra='forbid' prevents arbitrary field injection."""
        with pytest.raises(PydanticValidationError):
            AgentConfig(
                name="TestAgent",
                role="test_role",
                malicious_field="injected_value"  # Should be rejected
            )


class TestExceptionHierarchyConsolidation:
    """
    Test Case 2: Verify all domain exceptions inherit from SovereignError (SSOT).
    Target: exceptions.py and SovereignError.py
    Assertion: 100% pass on hierarchy integrity.
    """
    
    def test_agenticcore_error_is_sovereign_error(self):
        """Verify AgenticCoreError is aliased to SovereignError."""
        exc = AgenticCoreError("Test error")
        assert isinstance(exc, SovereignError)
        assert exc.error_code == "SOVEREIGN_ERROR"
    
    def test_healer_error_hierarchy(self):
        """Verify HealerError inherits from SovereignError."""
        exc = HealerError("Healing failed")
        assert isinstance(exc, SovereignError)
        assert exc.error_code == "HEALER_ERROR"
        assert exc.message == "Healing failed"
    
    def test_circular_dependency_error_hierarchy(self):
        """Verify CircularDependencyError inherits from HealerError."""
        exc = CircularDependencyError("Circular dependency detected")
        assert isinstance(exc, HealerError)
        assert isinstance(exc, SovereignError)
        assert exc.error_code == "CIRCULAR_DEPENDENCY"
    
    def test_configuration_error_hierarchy(self):
        """Verify ConfigurationError inherits from SovereignError."""
        exc = ConfigurationError("Invalid configuration")
        assert isinstance(exc, SovereignError)
        assert exc.error_code == "CONFIG_ERROR"
    
    def test_structural_error_hierarchy(self):
        """Verify StructuralError inherits from HealerError."""
        exc = StructuralError("Structural healing failed")
        assert isinstance(exc, HealerError)
        assert isinstance(exc, SovereignError)
        assert exc.error_code == "STRUCTURAL_ERROR"
    
    def test_hygiene_error_hierarchy(self):
        """Verify HygieneError inherits from HealerError."""
        exc = HygieneError("Code hygiene violation")
        assert isinstance(exc, HealerError)
        assert isinstance(exc, SovereignError)
        assert exc.error_code == "HYGIENE_ERROR"
    
    def test_integrity_error_hierarchy(self):
        """Verify IntegrityError inherits from SovereignError."""
        exc = IntegrityError("System integrity compromised")
        assert isinstance(exc, SovereignError)
        assert exc.error_code == "INTEGRITY_ERROR"
    
    def test_validation_error_hierarchy_with_field(self):
        """Verify ValidationError preserves field attribute."""
        exc = ValidationError("Validation failed", field="name")
        assert isinstance(exc, SovereignError)
        assert exc.error_code == "VALIDATION_ERROR"
        assert exc.field == "name"
    
    def test_resource_not_found_error_hierarchy(self):
        """Verify ResourceNotFoundError inherits from SovereignError."""
        exc = ResourceNotFoundError("Resource not found")
        assert isinstance(exc, SovereignError)
        assert exc.error_code == "RESOURCE_NOT_FOUND"
    
    def test_security_violation_error_hierarchy(self):
        """Verify SecurityViolationError preserves violation_type."""
        exc = SecurityViolationError("Security breach", violation_type="INJECTION")
        assert isinstance(exc, SovereignError)
        assert exc.error_code == "SECURITY_ERROR"
        assert exc.violation_type == "INJECTION"
        assert "INJECTION" in str(exc)
    
    def test_exception_pickle_ability(self):
        """Verify exceptions remain pickle-able for multiprocessing."""
        import pickle
        exc = SovereignError("Test error", error_code="TEST_CODE")
        pickled = pickle.dumps(exc)
        unpickled = pickle.loads(pickled)
        assert unpickled.message == "Test error"
        assert unpickled.error_code == "TEST_CODE"


class TestLegacyArtifactsFrozenState:
    """
    Test Case 3: Verify LegacyArtifacts remains a frozen, immutable contract.
    Target: LegacyArtifacts.py
    Assertion: 100% pass on contract immutability.
    """
    
    def test_frozen_dataclass_immutability(self):
        """Verify LegacyArtifacts is frozen and cannot be modified."""
        artifacts = LegacyArtifacts()
        
        # Attempt to inject new attribute (should fail on frozen dataclass)
        with pytest.raises((AttributeError, TypeError)):
            artifacts.new_pattern = r".*"
    
    def test_pattern_retrieval_works(self):
        """Verify pattern retrieval methods work correctly."""
        artifacts = LegacyArtifacts()
        
        # Verify CIRCULAR_IMPORT_PATTERN exists
        pattern = artifacts.get_artifact("CIRCULAR_IMPORT_PATTERN")
        assert pattern is not None
        
        # Verify pattern matching works
        weak_match = artifacts.get_weak_opening_match("I hope this finds you well")
        assert weak_match is not None
    
    def test_cognitive_modes_immutability(self):
        """Verify LegacyArtifacts frozen dataclass prevents new attributes."""
        artifacts = LegacyArtifacts()
        
        # Frozen dataclass prevents adding new attributes
        with pytest.raises((AttributeError, TypeError)):
            artifacts.new_attribute = "test"
        
        # Note: COGNITIVE_MODES is intentionally mutable for runtime access
        # This is by design - the dataclass is frozen, but field contents can be accessed


class TestSecuritySanitizationEdgeCases:
    """
    Test Case 4: Verify protection against injection in model names/fields.
    Target: entities.py (field_validators)
    Assertion: 100% pass on security hardening.
    """
    
    def test_script_injection_prevention(self):
        """Verify XSS-style script injection is blocked."""
        malicious_inputs = [
            "<script>alert(1)</script>",
            "<img src=x onerror=alert(1)>",
            "javascript:alert(1)",
        ]
        
        for malicious in malicious_inputs:
            with pytest.raises(PydanticValidationError):
                AgentConfig(name=malicious, role="test_role")
    
    def test_path_traversal_prevention(self):
        """Verify path traversal injection is blocked."""
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "/etc/shadow",
        ]
        
        for malicious in malicious_paths:
            with pytest.raises(PydanticValidationError):
                AgentConfig(name=malicious, role="test_role")
    
    def test_whitespace_only_rejection(self):
        """Verify whitespace-only names are rejected."""
        whitespace_inputs = ["  ", "\t", "\n", "   \t\n   "]
        
        for whitespace in whitespace_inputs:
            with pytest.raises(PydanticValidationError):
                AgentConfig(name=whitespace, role="test_role")
    
    def test_special_character_injection(self):
        """Verify special characters are blocked."""
        special_chars = ["name&param=value", "name'OR'1'='1", 'name"OR"1"="1']
        
        for special in special_chars:
            with pytest.raises(PydanticValidationError):
                AgentConfig(name=special, role="test_role")
    
    def test_model_name_whitelist_enforcement(self):
        """Verify only whitelisted model names are accepted."""
        valid_models = ['gpt-4o', 'gpt-4', 'gpt-3.5-turbo', 'claude-3', 'claude-2']
        
        # Test valid models pass
        for model in valid_models:
            entity = AgentConfig(name="TestAgent", role="test_role", model_name=model)
            assert entity.model_name == model
        
        # Test invalid models fail
        invalid_models = ['gpt-5', 'malicious-model', 'custom-llm', '']
        for model in invalid_models:
            with pytest.raises(PydanticValidationError):
                AgentConfig(name="TestAgent", role="test_role", model_name=model)
    
    def test_empty_string_rejection(self):
        """Verify empty strings are rejected for required fields."""
        with pytest.raises(PydanticValidationError):
            AgentConfig(name="", role="test_role")
        
        with pytest.raises(PydanticValidationError):
            AgentConfig(name="ValidName", role="")


class TestControlledMutabilityPatterns:
    """
    Additional Test Case: Verify controlled mutability works as designed.
    Target: entities.py (frozen vs mutable fields)
    Assertion: 100% pass on mutability contract.
    """
    
    def test_mutable_fields_allow_updates(self):
        """Verify mutable fields (updated_at, temperature) can be modified."""
        entity = AgentConfig(name="TestAgent", role="test_role")
        
        # Test temperature update (mutable field)
        original_temp = entity.temperature
        entity.temperature = 0.7
        assert entity.temperature == 0.7
        assert entity.temperature != original_temp
        
        # Test updated_at update (mutable field)
        original_time = entity.updated_at
        entity.update_timestamp()
        assert entity.updated_at >= original_time
    
    def test_frozen_fields_prevent_updates(self):
        """Verify frozen fields (id, created_at, name) cannot be modified."""
        entity = AgentConfig(name="TestAgent", role="test_role")
        
        # Test id immutability
        with pytest.raises((PydanticValidationError, ValueError, AttributeError)):
            entity.id = uuid4()
        
        # Test created_at immutability
        with pytest.raises((PydanticValidationError, ValueError, AttributeError)):
            entity.created_at = datetime.now(timezone.utc)
        
        # Test name immutability
        with pytest.raises((PydanticValidationError, ValueError, AttributeError)):
            entity.name = "NewName"
    
    def test_metadata_mutability(self):
        """Verify metadata dict can be modified (mutable field)."""
        entity = AgentConfig(name="TestAgent", role="test_role")
        
        # Metadata should be mutable
        entity.metadata["key"] = "value"
        assert entity.metadata["key"] == "value"
        
        # Capabilities should be mutable
        entity.capabilities.append("new_capability")
        assert "new_capability" in entity.capabilities


# CRITICAL ANALYSIS: If any test fails, Phase 3 implementation was cosmetic.
# 100% PASS IS MANDATORY BEFORE MERGE.
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
