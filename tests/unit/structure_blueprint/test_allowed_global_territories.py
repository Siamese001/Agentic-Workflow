"""
Test allowed global territories policy.

Validates:
- Only declared global territories are allowed at repo root
- Unknown root directories trigger violations
- SOVEREIGN_TERRITORIES defines allowed territories
"""

import pytest

from agentic_core.L5_safety.config.structure_blueprint_config import (
    SOVEREIGN_TERRITORIES,
    CORE_SUBFOLDER_MAP,
)


class TestSovereignTerritories:
    """Tests for SOVEREIGN_TERRITORIES constant."""

    def test_sovereign_territories_exists(self):
        """SOVEREIGN_TERRITORIES must be defined."""
        assert SOVEREIGN_TERRITORIES is not None
        assert len(SOVEREIGN_TERRITORIES) > 0

    def test_agentic_core_is_territory(self):
        """agentic_core must be a sovereign territory."""
        assert "agentic_core" in SOVEREIGN_TERRITORIES

    @pytest.mark.parametrize("territory", [
        "agentic_core",
        "apps_rg",
        "apps_lic",
        "apps_shared",
        "ops_scripts",
        "tests",
    ])
    def test_expected_territories_exist(self, territory: str):
        """Expected territories must be defined."""
        assert territory in SOVEREIGN_TERRITORIES, f"Missing territory: {territory}"

    def test_agentic_core_has_depth_3(self):
        """agentic_core territory must have depth 3."""
        agentic_core = SOVEREIGN_TERRITORIES.get("agentic_core", {})
        assert agentic_core.get("depth") == 3


class TestGlobalTerritorySubfolders:
    """Tests for global territory subfolders."""

    @pytest.mark.parametrize("global_territory", [
        "base_agents",
        "runtime",
        "interfaces",
        "mixins",
        "knowledge",
        "prompt_governance",
        "config",
        "utils",
    ])
    def test_global_territories_in_core_subfolder_map(self, global_territory: str):
        """Global territories must be in CORE_SUBFOLDER_MAP."""
        assert global_territory in CORE_SUBFOLDER_MAP, f"Missing global territory: {global_territory}"

    def test_base_agents_is_flat(self):
        """base_agents should have no subfolders (flat structure)."""
        base_agents_subfolders = CORE_SUBFOLDER_MAP.get("base_agents", [])
        # base_agents is flat - no LCD subfolders
        assert len(base_agents_subfolders) == 0 or base_agents_subfolders == []


class TestUnknownTerritoryDetection:
    """Tests for unknown territory detection."""

    def test_known_territories_complete(self):
        """All CORE_SUBFOLDER_MAP keys should be valid territories or layer subfolders."""
        valid_prefixes = {"L0", "L1", "L2", "L3", "L4", "L5", "L6"}
        known_globals = {"base_agents", "runtime", "interfaces", "mixins", "knowledge", "prompt_governance", "config", "utils", "semantic_memory"}

        for key in CORE_SUBFOLDER_MAP:
            is_layer = any(key.startswith(p) for p in valid_prefixes)
            is_global = key in known_globals
            assert is_layer or is_global, f"Unknown territory in CORE_SUBFOLDER_MAP: {key}"

    def test_no_unexpected_layer_prefixes(self):
        """No unexpected layer prefixes (L7+) should exist."""
        for key in CORE_SUBFOLDER_MAP:
            if key.startswith("L"):
                # Extract layer number
                import re
                match = re.match(r"L(\d+)", key)
                if match:
                    layer_num = int(match.group(1))
                    assert 0 <= layer_num <= 6, f"Unexpected layer number: {key}"
