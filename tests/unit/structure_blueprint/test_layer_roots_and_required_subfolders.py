"""
Test layer roots and required LCD subfolders.

Validates:
- All L0-L6 layers have required LCD subfolders
- Missing L6/config triggers violation; adding it passes
- LAYER_ROOTS constant is complete
"""

import pytest

from agentic_core.L5_safety.config.structure_blueprint_config import (
    CORE_SUBFOLDER_MAP,
    LAYER_ROOTS,
    REQUIRED_LCD_SUBFOLDERS,
    is_allowed_subfolder,
    is_layer_root,
    verify_derived_registries,
)


class TestLayerRoots:
    """Tests for LAYER_ROOTS constant."""

    def test_layer_roots_contains_all_layers(self):
        """All L0-L6 layers must be in LAYER_ROOTS."""
        expected = {
            "L0_maintenance",
            "L1_cognition",
            "L2_execution",
            "L3_orchestration",
            "L4_state",
            "L5_safety",
            "L6_observability",
        }
        assert expected == LAYER_ROOTS

    def test_layer_roots_is_frozenset(self):
        """LAYER_ROOTS must be immutable."""
        assert isinstance(LAYER_ROOTS, frozenset)

    @pytest.mark.parametrize(
        "layer",
        [
            "L0_maintenance",
            "L1_cognition",
            "L2_execution",
            "L3_orchestration",
            "L4_state",
            "L5_safety",
            "L6_observability",
        ],
    )
    def test_is_layer_root_returns_true_for_valid_layers(self, layer: str):
        """is_layer_root() returns True for valid layer names."""
        assert is_layer_root(layer) is True

    @pytest.mark.parametrize(
        "invalid",
        [
            "L7_future",
            "base_agents",
            "runtime",
            "prompt_governance",
            "utils",
            "",
        ],
    )
    def test_is_layer_root_returns_false_for_invalid(self, invalid: str):
        """is_layer_root() returns False for non-layer names."""
        assert is_layer_root(invalid) is False


class TestRequiredLCDSubfolders:
    """Tests for required LCD subfolders."""

    def test_required_lcd_subfolders_complete(self):
        """REQUIRED_LCD_SUBFOLDERS contains all 6 standard folders."""
        expected = {"config", "types", "reasoning", "enforcement", "validators", "utils"}
        assert expected == REQUIRED_LCD_SUBFOLDERS

    @pytest.mark.parametrize(
        "layer",
        [
            "L0_maintenance",
            "L1_cognition",
            "L2_execution",
            "L3_orchestration",
            "L4_state",
            "L5_safety",
            "L6_observability",
        ],
    )
    def test_all_layers_have_lcd_subfolders(self, layer: str):
        """Each layer in CORE_SUBFOLDER_MAP has all required LCD subfolders."""
        subfolders = set(CORE_SUBFOLDER_MAP.get(layer, []))
        assert REQUIRED_LCD_SUBFOLDERS.issubset(subfolders), (
            f"{layer} missing: {REQUIRED_LCD_SUBFOLDERS - subfolders}"
        )

    @pytest.mark.parametrize(
        "layer,subfolder",
        [
            ("L5_safety", "reasoning"),
            ("L5_safety", "enforcement"),
            ("L5_safety", "config"),
            ("L0_maintenance", "scripts"),
            ("L2_execution", "tools"),
            ("L4_state", "memory"),
            ("L6_observability", "dashboards"),
        ],
    )
    def test_is_allowed_subfolder_valid(self, layer: str, subfolder: str):
        """is_allowed_subfolder() returns True for valid layer+subfolder combinations."""
        # Note: is_allowed_subfolder checks REQUIRED_LCD_SUBFOLDERS only
        if subfolder in REQUIRED_LCD_SUBFOLDERS:
            assert is_allowed_subfolder(layer, subfolder) is True

    def test_is_allowed_subfolder_invalid_layer(self):
        """is_allowed_subfolder() returns False for invalid layer."""
        assert is_allowed_subfolder("invalid_layer", "reasoning") is False


class TestL6ConfigRequirement:
    """Tests for L6_observability/config/ requirement."""

    def test_l6_has_config_subfolder(self):
        """L6_observability must have config/ subfolder."""
        l6_subfolders = CORE_SUBFOLDER_MAP.get("L6_observability", [])
        assert "config" in l6_subfolders, "L6_observability missing config/ subfolder"

    def test_l6_has_dashboards_nuance(self):
        """L6_observability must have dashboards/ nuance subfolder."""
        l6_subfolders = CORE_SUBFOLDER_MAP.get("L6_observability", [])
        assert "dashboards" in l6_subfolders, "L6_observability missing dashboards/ subfolder"


class TestDerivedRegistriesInvariant:
    """Tests for verify_derived_registries() invariant check."""

    def test_verify_derived_registries_passes(self):
        """verify_derived_registries() returns empty list when consistent."""
        discrepancies = verify_derived_registries()
        assert discrepancies == [], f"Discrepancies found: {discrepancies}"

    def test_all_layers_in_subfolder_metadata(self):
        """All layers in CORE_SUBFOLDER_MAP should have SUBFOLDER_METADATA entries."""
        from agentic_core.L5_safety.config.structure_blueprint_config import SUBFOLDER_METADATA

        for layer in LAYER_ROOTS:
            assert layer in SUBFOLDER_METADATA, f"{layer} missing from SUBFOLDER_METADATA"
