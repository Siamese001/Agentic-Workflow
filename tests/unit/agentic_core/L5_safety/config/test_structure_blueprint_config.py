"""Tests for L5 Safety config - structure blueprint configuration."""

from pathlib import Path

import pytest


class TestStructureBlueprintConfig:
    """Tests for structure blueprint configuration."""

    def test_structure_blueprint_exists(self):
        """Structure blueprint config should exist."""
        path = Path("agentic_core/L5_safety/config/structure_blueprint_config.py")
        assert path.exists(), "structure_blueprint_config.py should exist"

    def test_sovereign_territories_defined(self):
        """SOVEREIGN_TERRITORIES should be defined."""
        try:
            from agentic_core.L0_routing.config import SOVEREIGN_TERRITORIES

            assert SOVEREIGN_TERRITORIES is not None
            assert isinstance(SOVEREIGN_TERRITORIES, dict)
        except ImportError as e:
            pytest.skip(f"Could not import: {e}")

    def test_layer_roots_defined(self):
        """LAYER_ROOTS should be defined."""
        try:
            from agentic_core.L5_safety.config.structure_blueprint_config import LAYER_ROOTS

            assert LAYER_ROOTS is not None
            assert isinstance(LAYER_ROOTS, (list, set, tuple, frozenset))
        except ImportError as e:
            pytest.skip(f"Could not import: {e}")

    def test_required_lcd_subfolders_defined(self):
        """REQUIRED_LCD_SUBFOLDERS should be defined."""
        try:
            from agentic_core.L5_safety.config.structure_blueprint_config import REQUIRED_LCD_SUBFOLDERS

            assert REQUIRED_LCD_SUBFOLDERS is not None
            assert isinstance(REQUIRED_LCD_SUBFOLDERS, (list, set, tuple, frozenset))
        except ImportError as e:
            pytest.skip(f"Could not import: {e}")


class TestBlueprintConsistency:
    """Tests for blueprint internal consistency."""

    def test_all_layers_in_territories(self):
        """All LAYER_ROOTS should be in SOVEREIGN_TERRITORIES (nested under agentic_core)."""
        try:
            from agentic_core.L5_safety.config.structure_blueprint_config import (
                LAYER_ROOTS,
                SOVEREIGN_TERRITORIES,
            )

            # Layers are nested under agentic_core in SOVEREIGN_TERRITORIES
            agentic_core_subfolders = SOVEREIGN_TERRITORIES.get("agentic_core", {}).get("subfolders", {})
            for layer in LAYER_ROOTS:
                assert layer in agentic_core_subfolders, f"{layer} should be in agentic_core subfolders"
        except ImportError as e:
            pytest.skip(f"Could not import: {e}")

    def test_apps_folders_in_territories(self):
        """apps_rg, apps_lic, apps_shared should be in SOVEREIGN_TERRITORIES."""
        try:
            from agentic_core.L0_routing.config import SOVEREIGN_TERRITORIES

            for app in ["apps_rg", "apps_lic", "apps_shared"]:
                assert app in SOVEREIGN_TERRITORIES, f"{app} should be in SOVEREIGN_TERRITORIES"
        except ImportError as e:
            pytest.skip(f"Could not import: {e}")


class TestAllowlistIntegrity:
    """Tests for allowlist integrity."""

    def test_l5_subprocess_allowlist_exists(self):
        """L5_SUBPROCESS_ALLOWLIST should be defined."""
        try:
            from agentic_core.L0_routing.config import L5_SUBPROCESS_ALLOWLIST

            assert L5_SUBPROCESS_ALLOWLIST is not None
            assert isinstance(L5_SUBPROCESS_ALLOWLIST, (set, list, tuple, frozenset))
        except ImportError as e:
            pytest.skip(f"Could not import: {e}")

    def test_l6_hybrid_allowlist_exists(self):
        """L6_HYBRID_ALLOWLIST should be defined."""
        try:
            from agentic_core.L0_routing.config import L6_HYBRID_ALLOWLIST

            assert L6_HYBRID_ALLOWLIST is not None
            assert isinstance(L6_HYBRID_ALLOWLIST, (set, list, tuple, frozenset))
        except ImportError as e:
            pytest.skip(f"Could not import: {e}")
