"""Tests for L5 Safety config - structure blueprint configuration."""

from pathlib import Path


class TestStructureBlueprintConfig:
    """Tests for structure blueprint configuration."""

    def test_structure_blueprint_exists(self):
        """Structure blueprint config should exist."""
        path = Path("agentic_core/L5_safety/config/structure_blueprint_config.py")
        assert path.exists(), "structure_blueprint_config.py should exist"

    def test_sovereign_territories_defined(self):
        """PROJECT_ROOT_WHITELIST should be defined (replaces SOVEREIGN_TERRITORIES)."""
        from agentic_core.L5_safety.config.structure_blueprint import PROJECT_ROOT_WHITELIST
        assert PROJECT_ROOT_WHITELIST is not None
        assert isinstance(PROJECT_ROOT_WHITELIST, frozenset)
        assert len(PROJECT_ROOT_WHITELIST) > 0

class TestBlueprintConsistency:
    """Tests for blueprint internal consistency."""

    def test_all_layers_in_territories(self):
        """All LAYER_ROOTS should be in CORE_SUBFOLDER_MAP (derived from SOVEREIGN_TERRITORIES)."""
        from agentic_core.L5_safety.config.structure_blueprint import (
            CORE_SUBFOLDER_MAP,
            LAYER_ROOTS,
        )
        for layer in LAYER_ROOTS:
            assert layer in CORE_SUBFOLDER_MAP, f"{layer} should be in CORE_SUBFOLDER_MAP"

class TestAllowlistIntegrity:
    """Tests for allowlist integrity."""

    def test_l5_subprocess_allowlist_exists(self):
        """L5_SUBPROCESS_ALLOWLIST should be defined."""
        from agentic_core.L0_routing.config import L5_SUBPROCESS_ALLOWLIST
        assert L5_SUBPROCESS_ALLOWLIST is not None
        assert isinstance(L5_SUBPROCESS_ALLOWLIST, (set, list, tuple, frozenset))
