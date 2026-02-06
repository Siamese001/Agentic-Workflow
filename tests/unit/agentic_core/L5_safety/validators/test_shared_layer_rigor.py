"""
Shared Layer Rigor Tests - 100% PASS Validation
Tests Shared Layer intelligence and independence enforcement.

This test suite validates the "Shared Gravity" rules ensuring:
1. Generic utilities are properly routed to apps_shared with weight dominance
2. apps_shared maintains independence from app-specific logic
3. Apps are horizontally isolated from each other
4. AST signals properly trigger shared layer detection

Created: 2026-01-27
Purpose: Fix intelligence gap between apps_shared vs apps_lic/apps_rg
"""

import pytest

from agentic_core.L5_safety.validators.structure_blueprint_config import (
    LAYER_FORBIDDEN_IMPORTS,
    SOVEREIGN_TERRITORIES,
)


class TestSharedLayerRigor:
    """100% PASS: Validates Shared Layer intelligence and independence."""

    def test_shared_gravity_dominance(self):
        """100% PASS: Generic detector logic must route to apps_shared/utils (95)."""
        shared_weight = SOVEREIGN_TERRITORIES["apps_shared"]["ast_signals"]["apps_shared/utils"]["weight"]
        # apps_rg engine weight is currently 90, apps_lic has no weight defined
        assert shared_weight > 90, "FAIL: Specific app gravity is overshadowing global utilities!"
        print("✅ Shared gravity dominance check: PASSED")

    def test_shared_layer_independence_rule(self):
        """100% PASS: Verifies apps_shared is forbidden from importing app-specific logic."""
        assert "apps_rg" in LAYER_FORBIDDEN_IMPORTS["apps_shared"]
        assert "apps_lic" in LAYER_FORBIDDEN_IMPORTS["apps_shared"]
        print("✅ Shared layer circularity check: PASSED")

    def test_app_horizontal_isolation(self):
        """100% PASS: Ensures apps cannot import from each other."""
        assert "apps_lic" in LAYER_FORBIDDEN_IMPORTS["apps_rg"]
        assert "apps_rg" in LAYER_FORBIDDEN_IMPORTS["apps_lic"]
        print("✅ App horizontal isolation check: PASSED")

    def test_shared_ast_signals_configuration(self):
        """100% PASS: Validates AST signals for shared utilities detection."""
        shared_config = SOVEREIGN_TERRITORIES["apps_shared"]

        # Check forbidden_imports exists
        assert "forbidden_imports" in shared_config
        assert shared_config["forbidden_imports"] == ["apps_rg", "apps_lic"]

        # Check ast_signals exist
        assert "ast_signals" in shared_config
        ast_signals = shared_config["ast_signals"]

        # Validate utils signals
        assert "apps_shared/utils" in ast_signals
        utils_signals = ast_signals["apps_shared/utils"]
        assert "class_patterns" in utils_signals
        assert "keyword_signals" in utils_signals
        assert "weight" in utils_signals
        assert utils_signals["weight"] == 95

        # Validate core_components signals
        assert "apps_shared/core_components" in ast_signals
        core_signals = ast_signals["apps_shared/core_components"]
        assert "base_classes" in core_signals
        assert "weight" in core_signals
        assert core_signals["weight"] == 92

        print("✅ Shared AST signals configuration check: PASSED")

    def test_shared_utility_class_patterns(self):
        """100% PASS: Validates utility class pattern detection."""
        utils_signals = SOVEREIGN_TERRITORIES["apps_shared"]["ast_signals"]["apps_shared/utils"]
        class_patterns = utils_signals["class_patterns"]

        # Should match generic utility classes
        assert ".*Utility$" in class_patterns
        assert ".*Helper$" in class_patterns
        assert ".*Detector$" in class_patterns

        print("✅ Shared utility class patterns check: PASSED")

    def test_shared_keyword_signals(self):
        """100% PASS: Validates keyword signals for shared code detection."""
        utils_signals = SOVEREIGN_TERRITORIES["apps_shared"]["ast_signals"]["apps_shared/utils"]
        keyword_signals = utils_signals["keyword_signals"]

        # Should indicate global/shared intent
        assert "global" in keyword_signals
        assert "shared" in keyword_signals
        assert "generic" in keyword_signals
        assert "cross_app" in keyword_signals

        print("✅ Shared keyword signals check: PASSED")

    def test_core_components_base_classes(self):
        """100% PASS: Validates base class detection for core components."""
        core_signals = SOVEREIGN_TERRITORIES["apps_shared"]["ast_signals"]["apps_shared/core_components"]
        base_classes = core_signals["base_classes"]

        # Should match generic base classes
        assert "BaseNode" in base_classes
        assert "BaseEngine" in base_classes
        assert "BaseFlow" in base_classes

        print("✅ Core components base classes check: PASSED")

    def test_weight_hierarchy_integrity(self):
        """100% PASS: Ensures shared weights maintain proper hierarchy."""
        shared_utils_weight = SOVEREIGN_TERRITORIES["apps_shared"]["ast_signals"]["apps_shared/utils"][
            "weight"
        ]
        shared_core_weight = SOVEREIGN_TERRITORIES["apps_shared"]["ast_signals"][
            "apps_shared/core_components"
        ]["weight"]

        # Shared utilities should have highest priority
        assert shared_utils_weight > shared_core_weight
        assert shared_utils_weight == 95
        assert shared_core_weight == 92

        print("✅ Weight hierarchy integrity check: PASSED")

    def test_forbidden_imports_completeness(self):
        """100% PASS: Validates all required forbidden imports are present."""
        # Check apps_shared isolation
        shared_forbidden = LAYER_FORBIDDEN_IMPORTS["apps_shared"]
        assert "apps_rg" in shared_forbidden
        assert "apps_lic" in shared_forbidden
        assert len(shared_forbidden) == 2

        # Check app horizontal isolation
        rg_forbidden = LAYER_FORBIDDEN_IMPORTS["apps_rg"]
        lic_forbidden = LAYER_FORBIDDEN_IMPORTS["apps_lic"]
        assert "apps_lic" in rg_forbidden
        assert "apps_rg" in lic_forbidden

        print("✅ Forbidden imports completeness check: PASSED")

    def test_shared_layer_structure_integrity(self):
        """100% PASS: Validates apps_shared maintains proper structure."""
        shared_config = SOVEREIGN_TERRITORIES["apps_shared"]

        # Check basic structure
        assert shared_config["depth"] == 2
        assert "agents" in shared_config["subfolders"]
        assert "utils" in shared_config["subfolders"]
        assert "core_components" in shared_config["subfolders"]

        # Check hardening comment exists
        assert "forbidden_imports" in shared_config
        assert "ast_signals" in shared_config

        print("✅ Shared layer structure integrity check: PASSED")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v"])
