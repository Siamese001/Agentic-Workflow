#!/usr/bin/env python3
"""
Unit Tests for SSOT Canonical Logic
====================================

Tests the canonical functions in canonical_truth.py to ensure:
1. Health score calculation is accurate and consistent
2. Layer inference is correct for all path patterns
3. No duplicate implementations exist in codebase

These tests enforce the Single Source of Truth principle.
"""

from pathlib import Path

import pytest

from agentic_core.L5_safety.validators.canonical_truth import (
    HEALTH_WEIGHTS,
    calculate_health_score,
    categorize_agent,
    get_agent_categories,
    get_canonical_layer,
    get_health_weights,
    validate_health_components,
)


class TestHealthScoreCalculation:
    """Test suite for canonical health score calculation."""

    def test_perfect_health_score(self):
        """Test that perfect scores (100.0 across all metrics) yield 100.0."""
        result = calculate_health_score(
            heal_cap=100.0, invoc=100.0, test_cov=100.0, obs=100.0, comp_health=100.0
        )
        assert result == 100.0, "Perfect health should be 100.0"

    def test_zero_health_score(self):
        """Test that zero scores across all metrics yield 0.0."""
        result = calculate_health_score(
            heal_cap=0.0, invoc=0.0, test_cov=0.0, obs=0.0, comp_health=0.0
        )
        assert result == 0.0, "Zero health should be 0.0"

    def test_weighted_formula_accuracy(self):
        """Test that weights are applied correctly."""
        # Known inputs with expected output
        result = calculate_health_score(
            heal_cap=90.0,  # 90 * 0.30 = 27.0
            invoc=80.0,  # 80 * 0.10 = 8.0
            test_cov=70.0,  # 70 * 0.25 = 17.5
            obs=85.0,  # 85 * 0.20 = 17.0
            comp_health=60.0,  # 60 * 0.15 = 9.0
        )
        # Total: 27.0 + 8.0 + 17.5 + 17.0 + 9.0 = 78.5
        expected = 78.5
        assert result == expected, f"Expected {expected}, got {result}"

    def test_weights_sum_to_one(self):
        """Verify that health weights sum to 1.0 (100%)."""
        total = sum(HEALTH_WEIGHTS.values())
        assert abs(total - 1.0) < 0.0001, f"Weights must sum to 1.0, got {total}"

    def test_precision_rounding(self):
        """Test that results are rounded to 4 decimal places."""
        result = calculate_health_score(
            heal_cap=33.333, invoc=66.666, test_cov=99.999, obs=12.345, comp_health=87.654
        )
        # Verify result has at most 4 decimal places
        assert len(str(result).split(".")[-1]) <= 4, "Result should be rounded to 4 decimals"

    def test_invalid_input_below_range(self):
        """Test that values below 0.0 raise ValueError."""
        with pytest.raises(ValueError, match="must be between 0.0 and 100.0"):
            calculate_health_score(
                heal_cap=-1.0, invoc=50.0, test_cov=50.0, obs=50.0, comp_health=50.0
            )

    def test_invalid_input_above_range(self):
        """Test that values above 100.0 raise ValueError."""
        with pytest.raises(ValueError, match="must be between 0.0 and 100.0"):
            calculate_health_score(
                heal_cap=50.0, invoc=101.0, test_cov=50.0, obs=50.0, comp_health=50.0
            )

    def test_edge_case_boundary_values(self):
        """Test boundary values (0.0 and 100.0) are accepted."""
        # Should not raise
        result = calculate_health_score(
            heal_cap=0.0, invoc=100.0, test_cov=0.0, obs=100.0, comp_health=50.0
        )
        assert 0.0 <= result <= 100.0, "Result should be in valid range"


class TestLayerInference:
    """Test suite for canonical layer inference."""

    def test_l0_maintenance_detection(self):
        """Test L0 layer detection from path."""
        paths = [
            "agentic_core/L0_maintenance/scripts/agent.py",
            "C:/Git/Agentic-Workflow/agentic_core/L0_maintenance/logs/log.py",
            "/home/user/project/agentic_core/L0_maintenance/benchmarks/test.py",
        ]
        for path in paths:
            assert get_canonical_layer(path) == "L0", f"Failed to detect L0 in {path}"

    def test_l5_safety_detection(self):
        """Test L5 layer detection from path."""
        paths = [
            "agentic_core/L5_safety/validators/LocationAgent.py",
            "C:\\Git\\Agentic-Workflow\\agentic_core\\L5_safety\\guardrails\\agent.py",
            "agentic_core/L5_safety/red_teaming/test.py",
        ]
        for path in paths:
            assert get_canonical_layer(path) == "L5", f"Failed to detect L5 in {path}"

    def test_apps_detection(self):
        """Test Apps layer detection from path."""
        paths = [
            "apps_rg/engines/engine.py",
            "apps_lic/domain/agent.py",
            "apps_shared/utils/helper.py",
        ]
        for path in paths:
            assert get_canonical_layer(path) == "Apps", f"Failed to detect Apps in {path}"

    def test_utils_detection(self):
        """Test utils detection from path."""
        paths = ["agentic_core/utils/core_extensions/helper.py", "utils/general_helpers/tool.py"]
        for path in paths:
            assert get_canonical_layer(path) == "utils", f"Failed to detect utils in {path}"

    def test_tests_detection(self):
        """Test tests detection from path."""
        paths = [
            "tests/unit/test_agent.py",
            "tests/integration/test_e2e.py",
            "tests/e2e/test_dashboard.py",
        ]
        for path in paths:
            assert get_canonical_layer(path) == "tests", f"Failed to detect tests in {path}"

    def test_all_layers_l0_to_l6(self):
        """Test all layers L0-L6 are correctly detected."""
        layer_map = {
            "L0": "agentic_core/L0_maintenance/scripts/agent.py",
            "L1": "agentic_core/L1_cognition/thought_engine/agent.py",
            "L2": "agentic_core/L2_execution/tool_registry/agent.py",
            "L3": "agentic_core/L3_orchestration/workflow_engines/agent.py",
            "L4": "agentic_core/L4_state/validation_context/agent.py",
            "L5": "agentic_core/L5_safety/validators/agent.py",
            "L6": "agentic_core/L6_observability/dashboards/agent.py",
        }
        for expected_layer, path in layer_map.items():
            result = get_canonical_layer(path)
            assert result == expected_layer, f"Expected {expected_layer}, got {result} for {path}"

    def test_windows_path_normalization(self):
        """Test that Windows paths with backslashes are handled correctly."""
        windows_path = (
            "C:\\Git\\Agentic-Workflow\\agentic_core\\L3_orchestration\\workflow_engines\\agent.py"
        )
        result = get_canonical_layer(windows_path)
        assert result == "L3", f"Windows path normalization failed: {windows_path}"

    def test_unknown_path(self):
        """Test that unknown paths return 'Unknown'."""
        unknown_paths = [
            "random/folder/file.py",
            "unknown_dir/agent.py",
            "C:/some/other/path/file.py",
        ]
        for path in unknown_paths:
            result = get_canonical_layer(path)
            assert result == "Unknown", f"Expected 'Unknown' for {path}, got {result}"

    def test_path_object_input(self):
        """Test that Path objects are accepted as input."""
        path_obj = Path("agentic_core/L5_safety/validators/agent.py")
        result = get_canonical_layer(path_obj)
        assert result == "L5", "Path object input should work"


class TestValidationFunctions:
    """Test suite for validation helper functions."""

    def test_validate_health_components_valid(self):
        """Test that valid components pass validation."""
        result = validate_health_components(
            heal_cap=90.0, invoc=80.0, test_cov=70.0, obs=85.0, comp_health=60.0
        )
        assert result is True, "Valid components should pass"

    def test_validate_health_components_invalid(self):
        """Test that invalid components fail validation."""
        result = validate_health_components(
            heal_cap=90.0,
            invoc=101.0,  # Invalid: > 100
            test_cov=70.0,
            obs=85.0,
            comp_health=60.0,
        )
        assert result is False, "Invalid components should fail"

    def test_get_health_weights_returns_copy(self):
        """Test that get_health_weights returns a copy, not the original."""
        weights1 = get_health_weights()
        weights2 = get_health_weights()

        # Modify one copy
        weights1["heal_capability"] = 0.99

        # Verify original is unchanged
        assert weights2["heal_capability"] == 0.30, "Should return independent copies"
        assert HEALTH_WEIGHTS["heal_capability"] == 0.30, "Original should be unchanged"


class TestAgentCategorization:
    """Test suite for canonical agent categorization."""

    def test_validator_categorization(self):
        """Test that validator agents are correctly categorized."""
        test_cases = [
            "BaseClassEnforcerAgent",
            "ValidationAgent",
            "ComplianceOrchestratorAgent",
            "AuditAgent",
        ]
        for agent_name in test_cases:
            result = categorize_agent(agent_name)
            assert result == "Validator", (
                f"{agent_name} should be categorized as Validator, got {result}"
            )

    def test_healer_categorization(self):
        """Test that healer agents are correctly categorized."""
        test_cases = [
            "TerritoryHealerAgent",
            "StructuralHealerAgent",
            "RecoveryAgent",
            "RepairAgent",
        ]
        for agent_name in test_cases:
            result = categorize_agent(agent_name)
            assert result == "Healer", f"{agent_name} should be categorized as Healer, got {result}"

    def test_orchestrator_categorization(self):
        """Test that orchestrator agents are correctly categorized."""
        test_cases = ["WorkflowEngine", "OrchestrationAgent", "CoordinatorAgent", "RouterAgent"]
        for agent_name in test_cases:
            result = categorize_agent(agent_name)
            assert result == "Orchestrator", (
                f"{agent_name} should be categorized as Orchestrator, got {result}"
            )

    def test_guardian_categorization(self):
        """Test that guardian agents are correctly categorized."""
        test_cases = ["SafetyGuardianAgent", "SecurityAgent", "ProtectionAgent", "SentinelAgent"]
        for agent_name in test_cases:
            result = categorize_agent(agent_name)
            assert result == "Guardian", (
                f"{agent_name} should be categorized as Guardian, got {result}"
            )

    def test_categorization_with_base_classes(self):
        """Test that base classes influence categorization."""
        # Agent name doesn't match, but base class does
        result = categorize_agent("CustomAgent", base_classes=["HealerMixin", "BaseAgent"])
        assert result == "Healer", "Base classes should influence categorization"

    def test_categorization_with_docstring(self):
        """Test that docstring influences categorization."""
        # Neither name nor base classes match, but docstring does
        result = categorize_agent(
            "CustomAgent",
            base_classes=["BaseAgent"],
            docstring="This agent validates and enforces compliance rules",
        )
        assert result == "Validator", "Docstring should influence categorization"

    def test_generic_agent_fallback(self):
        """Test that unmatched agents return GenericAgent."""
        result = categorize_agent("RandomCustomAgent")
        assert result == "GenericAgent", "Unmatched agents should return GenericAgent"

    def test_priority_order(self):
        """Test that first pattern match wins (priority order)."""
        # Agent could match multiple categories, first should win
        result = categorize_agent("ValidatorHealerAgent")
        # Validator comes before Healer in AGENT_CATEGORY_PATTERNS
        assert result == "Validator", "First pattern match should win"

    def test_case_insensitive_matching(self):
        """Test that pattern matching is case-insensitive."""
        test_cases = [
            ("validatoragent", "Validator"),
            ("HEALERAGENT", "Healer"),
            ("OrChEsTrAtOrAgEnT", "Orchestrator"),
        ]
        for agent_name, expected_category in test_cases:
            result = categorize_agent(agent_name)
            assert result == expected_category, f"{agent_name} should match {expected_category}"

    def test_get_agent_categories(self):
        """Test that get_agent_categories returns all categories."""
        categories = get_agent_categories()
        assert "Validator" in categories, "Should include Validator"
        assert "Healer" in categories, "Should include Healer"
        assert "GenericAgent" in categories, "Should include GenericAgent fallback"
        assert len(categories) > 5, "Should have multiple categories"


class TestSSOTEnforcement:
    """Test suite to ensure no duplicate implementations exist."""

    def test_no_hardcoded_health_weights_in_dashboard(self):
        """Verify dashboard generator doesn't have hardcoded health weights."""
        dashboard_path = Path(
            "C:/Git/Agentic-Workflow/agentic_core/L6_observability/dashboards/generate_dashboard.py"
        )
        if dashboard_path.exists():
            content = dashboard_path.read_text(encoding="utf-8")
            # Should NOT have inline weight calculations
            assert "(heal_cap_pct * 0.30)" not in content, "Dashboard has hardcoded health weights"
            # SHOULD import from canonical_truth
            assert (
                "from agentic_core.L5_safety.validators.canonical_truth_1 import calculate_health_score"
                in content
            ), "Dashboard should import canonical health function"

    def test_no_hardcoded_health_weights_in_tests(self):
        """Verify E2E tests don't have hardcoded health weights."""
        test_path = Path("C:/Git/Agentic-Workflow/scripts/test_dashboard_end_to_end.py")
        if test_path.exists():
            content = test_path.read_text(encoding="utf-8")
            # Should NOT have inline weight calculations
            assert "(heal_cap * 0.30)" not in content, "E2E tests have hardcoded health weights"
            # SHOULD import from canonical_truth
            assert (
                "from agentic_core.L5_safety.validators.canonical_truth_1 import calculate_health_score"
                in content
            ), "E2E tests should import canonical health function"


class TestCategorizationMatrix:
    """Matrix test for specific agent examples from codebase."""

    def test_real_world_agents(self):
        """Test categorization of actual agents from the codebase."""
        # Real agents with expected categories
        test_matrix = [
            ("BaseClassEnforcerAgent", "Validator"),
            ("TerritoryHealerAgent", "Healer"),
            ("SemanticTerritoryMapperAgent", "Governor"),
            ("GeneralExerciserAgent", "Orchestrator"),
            ("SovereignHealthMonitor", "Monitor"),
            ("GravityValidatorAgent", "Validator"),
            ("StructuralHealerAgent", "Healer"),
            ("NervousSystemAgent", "Orchestrator"),
            ("LocationAgent", "Governor"),
            ("HierarchyAgent", "Governor"),
        ]

        for agent_name, expected_category in test_matrix:
            result = categorize_agent(agent_name)
            assert result == expected_category, (
                f"{agent_name} should be {expected_category}, got {result}"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
