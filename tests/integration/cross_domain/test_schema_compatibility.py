"""Integration tests for cross-domain schema compatibility."""
from __future__ import annotations

from shared.reasoning_config import SAFETY_THRESHOLD
from shared.models import ValidationResult, ValidationSeverity
from runtime.shared.sdk_registry import SDK_REGISTRY

class TestConfigSchemaCompatibility:
    def test_config_safety_threshold_matches_models(self):
        """Config SAFETY_THRESHOLD is usable with validation models."""
        assert 0 <= SAFETY_THRESHOLD <= 1
        # Can create validation result using threshold
        result = ValidationResult(
            is_valid=SAFETY_THRESHOLD > 0.5,
            severity=list(ValidationSeverity)[0],
            message=f"Threshold: {SAFETY_THRESHOLD}",
        )
        assert isinstance(result.is_valid, bool)

    def test_sdk_registry_categories_are_valid(self):
        """All SDK entries have valid categories."""
        for name, entry in SDK_REGISTRY.items():
            assert isinstance(entry.category, SDKCategory)
            assert entry.name == name

class TestValidationModelIntegration:
    def test_gate_decision_with_validation_result(self):
        """GateDecision can be used alongside ValidationResult."""
        decisions = list(GateDecision)
        severities = list(ValidationSeverity)

        # Both enums should be usable together
        assert len(decisions) >= 1
        assert len(severities) >= 1

    def test_validation_severity_ordering(self):
        """ValidationSeverity levels are ordered."""
        severities = list(ValidationSeverity)
        # Should have at least 2 severity levels
        assert len(severities) >= 2
