"""Unit tests for shared layer gravity utilities.

Tests for agentic_core.L4_state.utils.layer_gravity
"""

from pathlib import Path

from agentic_core.L4_state.utils.layer_gravity import (
    GRAVITY_RULES,
    LAYER_ORDER,
    extract_layer_from_module,
    extract_layer_from_path,
    get_allowed_layers,
    get_layer_order,
    is_gravity_violation,
)


class TestLayerOrderConstants:
    """Tests for LAYER_ORDER constant."""

    def test_layer_order_has_all_layers(self):
        """Should have L0 through L6."""
        expected_layers = {"L0", "L1", "L2", "L3", "L4", "L5", "L6"}
        assert set(LAYER_ORDER.keys()) == expected_layers

    def test_layer_order_is_ascending(self):
        """Layer values should increase from L0 to L6."""
        for i in range(7):
            assert LAYER_ORDER[f"L{i}"] == i


class TestGravityRulesConstants:
    """Tests for GRAVITY_RULES constant."""

    def test_gravity_rules_has_all_layers(self):
        """Should have rules for L0 through L6."""
        expected_layers = {"L0", "L1", "L2", "L3", "L4", "L5", "L6"}
        assert set(GRAVITY_RULES.keys()) == expected_layers

    def test_l0_can_only_import_l0(self):
        """L0 should only be able to import from L0."""
        assert GRAVITY_RULES["L0"] == {"L0"}

    def test_l6_can_import_all(self):
        """L6 should be able to import from all layers."""
        assert GRAVITY_RULES["L6"] == {"L0", "L1", "L2", "L3", "L4", "L5", "L6"}

    def test_layers_can_import_from_themselves(self):
        """Each layer should be able to import from itself."""
        for layer in LAYER_ORDER.keys():
            assert layer in GRAVITY_RULES[layer]

    def test_gravity_rules_are_cumulative(self):
        """Each layer should include all previous layers."""
        for i in range(1, 7):
            current = f"L{i}"
            previous = f"L{i - 1}"
            # Current layer's allowed set should contain all of previous layer's allowed set
            assert GRAVITY_RULES[previous].issubset(GRAVITY_RULES[current])


class TestExtractLayerFromPath:
    """Tests for layer extraction from file paths."""

    def test_extract_layer_from_path_l5(self):
        """Should extract L5 from path."""
        path = Path("agentic_core/L5_safety/validators/GovernanceAgent.py")
        assert extract_layer_from_path(path) == "L5"

    def test_extract_layer_from_path_l0(self):
        """Should extract L0 from path."""
        path = Path("agentic_core/L0_maintenance/scripts/cleanup.py")
        assert extract_layer_from_path(path) == "L0"

    def test_extract_layer_from_path_l3(self):
        """Should extract L3 from path."""
        path = Path("agentic_core/L3_orchestration/reasoning/engine.py")
        assert extract_layer_from_path(path) == "L3"

    def test_extract_layer_from_path_no_layer(self):
        """Should return None for paths without layer."""
        path = Path("apps_rg/engines/tool.py")
        assert extract_layer_from_path(path) is None

    def test_extract_layer_from_string_path(self):
        """Should work with string paths."""
        path = "agentic_core/L4_state/memory/store.py"
        assert extract_layer_from_path(path) == "L4"

    def test_extract_layer_windows_path(self):
        """Should work with Windows-style paths."""
        path = "agentic_core\\L2_execution\\mcp\\client.py"
        assert extract_layer_from_path(path) == "L2"

    def test_extract_layer_from_base_agents(self):
        """Should return None for base_agents (no layer prefix)."""
        path = Path("agentic_core/base_agents/SovereignBaseAgent.py")
        assert extract_layer_from_path(path) is None


class TestExtractLayerFromModule:
    """Tests for layer extraction from module paths."""

    def test_extract_layer_from_module_l3(self):
        """Should extract L3 from module path."""
        module = "agentic_core.L3_orchestration.reasoning.engine"
        assert extract_layer_from_module(module) == "L3"

    def test_extract_layer_from_module_l5(self):
        """Should extract L5 from module path."""
        module = "agentic_core.L5_safety.validators.GovernanceAgent"
        assert extract_layer_from_module(module) == "L5"

    def test_extract_layer_from_module_no_layer(self):
        """Should return None for modules without layer."""
        module = "apps_shared.utils.helpers"
        assert extract_layer_from_module(module) is None

    def test_extract_layer_starting_with_layer(self):
        """Should detect layer at start of module."""
        module = "L1_cognition.engine"
        assert extract_layer_from_module(module) == "L1"


class TestIsGravityViolation:
    """Tests for gravity violation detection."""

    def test_l3_importing_l5_is_violation(self):
        """L3 importing L5 should be a gravity violation."""
        assert is_gravity_violation("L3", "L5") is True

    def test_l5_importing_l3_is_not_violation(self):
        """L5 importing L3 should NOT be a gravity violation."""
        assert is_gravity_violation("L5", "L3") is False

    def test_l0_importing_l0_is_not_violation(self):
        """Same layer import should NOT be a violation."""
        assert is_gravity_violation("L0", "L0") is False

    def test_l6_can_import_all_layers(self):
        """L6 should be able to import from all layers."""
        for layer in LAYER_ORDER.keys():
            assert is_gravity_violation("L6", layer) is False

    def test_l0_importing_any_higher_is_violation(self):
        """L0 importing any higher layer should be a violation."""
        for i in range(1, 7):
            assert is_gravity_violation("L0", f"L{i}") is True

    def test_l1_importing_l2_is_violation(self):
        """L1 importing L2 should be a violation."""
        assert is_gravity_violation("L1", "L2") is True

    def test_l2_importing_l1_is_not_violation(self):
        """L2 importing L1 should NOT be a violation."""
        assert is_gravity_violation("L2", "L1") is False

    def test_unknown_source_layer(self):
        """Unknown source layer should treat as violation."""
        assert is_gravity_violation("UNKNOWN", "L0") is True


class TestGetAllowedLayers:
    """Tests for get_allowed_layers function."""

    def test_get_allowed_layers_l0(self):
        """L0 should only allow L0."""
        assert get_allowed_layers("L0") == {"L0"}

    def test_get_allowed_layers_l3(self):
        """L3 should allow L0, L1, L2, L3."""
        assert get_allowed_layers("L3") == {"L0", "L1", "L2", "L3"}

    def test_get_allowed_layers_l6(self):
        """L6 should allow all layers."""
        assert get_allowed_layers("L6") == {"L0", "L1", "L2", "L3", "L4", "L5", "L6"}

    def test_get_allowed_layers_unknown(self):
        """Unknown layer should return empty set."""
        assert get_allowed_layers("UNKNOWN") == set()


class TestGetLayerOrder:
    """Tests for get_layer_order function."""

    def test_get_layer_order_valid(self):
        """Should return correct order for valid layers."""
        assert get_layer_order("L0") == 0
        assert get_layer_order("L3") == 3
        assert get_layer_order("L6") == 6

    def test_get_layer_order_invalid(self):
        """Should return -1 for invalid layers."""
        assert get_layer_order("invalid") == -1
        assert get_layer_order("L7") == -1
        assert get_layer_order("") == -1
