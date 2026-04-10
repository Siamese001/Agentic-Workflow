"""Tests for structure blueprint yaml_loader module."""
from __future__ import annotations

from agentic_core.L0_routing.config.path_constants import PROJECT_ROOT_WHITELIST, ROOT_WHITELIST
from agentic_core.L5_safety.config.structure_blueprint.territories_loader import (
    build_territories_from_yaml,
    get_all_territories_yaml,
    get_territory_yaml,
)
from agentic_core.L5_safety.config.structure_blueprint.yaml_loader import (
    get_all_layer_names,
    get_all_territory_names,
    get_layer_override,
    get_territory,
    load_ast_signals,
    load_layer_overrides,
    load_territories,
    match_wildcard_territory,
)


class TestLoadTerritories:
    """Test load_territories function."""

    def test_load_territories_returns_data(self):
        """Happy path: load_territories returns YAML data."""
        data = load_territories()
        assert "territories" in data
        assert "schema_version" in data
        assert "agentic_core" in data["territories"]

    def test_territories_have_required_fields(self):
        """Validation: all territories have required fields."""
        data = load_territories()
        for name, territory in data["territories"].items():
            assert "depth" in territory, f"{name} missing depth"
            assert "purpose" in territory, f"{name} missing purpose"

    def test_load_territories_caching(self):
        """Edge case: load_territories uses cache (no repeated file reads)."""
        data1 = load_territories()
        data2 = load_territories()
        # Same object reference due to caching
        assert data1 is data2


class TestLoadLayerOverrides:
    """Test load_layer_overrides function."""

    def test_load_layer_overrides_returns_data(self):
        """Happy path: load_layer_overrides returns YAML data."""
        data = load_layer_overrides()
        assert "overrides" in data
        assert "schema_version" in data
        assert "L0_routing" in data["overrides"]

    def test_all_layers_have_purpose(self):
        """Validation: all layer overrides have purpose field."""
        data = load_layer_overrides()
        for name, override in data["overrides"].items():
            assert "purpose" in override, f"{name} missing purpose"

    def test_load_layer_overrides_caching(self):
        """Edge case: load_layer_overrides uses cache (no repeated file reads)."""
        data1 = load_layer_overrides()
        data2 = load_layer_overrides()
        # Same object reference due to caching
        assert data1 is data2


class TestGetTerritory:
    """Test get_territory function."""

    def test_get_existing_territory(self):
        """Happy path: get existing territory returns data."""
        territory = get_territory("agentic_core")
        assert territory is not None
        assert territory["purpose"] == "Core framework logic (L0-L6)"

    def test_get_nonexistent_territory_returns_none(self):
        """Failure path: get non-existent territory returns None."""
        territory = get_territory("nonexistent_territory")
        assert territory is None


class TestGetLayerOverride:
    """Test get_layer_override function."""

    def test_get_existing_layer(self):
        """Happy path: get existing layer override returns data."""
        layer = get_layer_override("L0_routing")
        assert layer is not None
        assert "purpose" in layer

    def test_get_nonexistent_layer_returns_none(self):
        """Failure path: get non-existent layer returns None."""
        layer = get_layer_override("nonexistent_layer")
        assert layer is None


class TestMatchWildcardTerritory:
    """Test match_wildcard_territory function."""

    def test_match_apps_wildcard(self):
        """Happy path: match apps_* wildcard pattern."""
        match = match_wildcard_territory("apps_eval")
        assert match is not None
        assert "pattern" in match

    def test_no_match_returns_none(self):
        """Failure path: no wildcard match returns None."""
        match = match_wildcard_territory("invalid_name")
        assert match is None


class TestGetAllNames:
    """Test get_all_* functions."""

    def test_get_all_territory_names(self):
        """Happy path: returns list of territory names."""
        names = get_all_territory_names()
        assert isinstance(names, list)
        assert "agentic_core" in names
        assert "apps_eval" in names

    def test_get_all_layer_names(self):
        """Happy path: returns list of layer names."""
        names = get_all_layer_names()
        assert isinstance(names, list)
        assert "L0_routing" in names
        assert "L1_cognition" in names


class TestLoadAstSignals:
    """Test load_ast_signals function."""

    def test_load_ast_signals_returns_data(self):
        """Happy path: load_ast_signals returns YAML data."""
        data = load_ast_signals()
        assert "ast_signals" in data
        assert isinstance(data["ast_signals"], dict)

    def test_ast_signals_have_required_keys(self):
        """Validation: AST signals have required structure."""
        data = load_ast_signals()
        ast_signals = data["ast_signals"]
        assert isinstance(ast_signals, dict)
        assert len(ast_signals) > 0
        # AST signals are keyed by path, e.g., 'agentic_core/base_agents'
        assert "agentic_core/base_agents" in ast_signals

    def test_ast_signals_nonempty_content(self):
        """Edge case: AST signals contain expected signal types."""
        data = load_ast_signals()
        ast_signals = data["ast_signals"]
        # Verify at least one signal has expected structure
        if "agentic_core/base_agents" in ast_signals:
            signal = ast_signals["agentic_core/base_agents"]
            assert isinstance(signal, dict)

    def test_load_ast_signals_caching(self):
        """Edge case: load_ast_signals uses cache (no repeated file reads)."""
        data1 = load_ast_signals()
        data2 = load_ast_signals()
        # Same object reference due to caching
        assert data1 is data2


class TestTerritoriesLoader:
    """Test territories_loader module functions."""

    def test_build_territories_from_yaml_returns_data(self):
        """Happy path: build_territories_from_yaml returns data."""
        territories = build_territories_from_yaml()
        assert isinstance(territories, dict)
        assert "agentic_core" in territories

    def test_build_territories_includes_ast_signals(self):
        """Validation: AST signals merged into agentic_core territory."""
        territories = build_territories_from_yaml()
        assert "agentic_core" in territories
        assert "ast_signals" in territories["agentic_core"]

    def test_get_all_territories_yaml_returns_data(self):
        """Happy path: get_all_territories_yaml returns data."""
        territories = get_all_territories_yaml()
        assert isinstance(territories, dict)
        assert "agentic_core" in territories

    def test_get_territory_yaml_existing(self):
        """Happy path: get_territory_yaml returns existing territory."""
        territory = get_territory_yaml("agentic_core")
        assert territory is not None
        assert "purpose" in territory

    def test_get_territory_yaml_nonexistent(self):
        """Failure path: get_territory_yaml returns None for nonexistent."""
        territory = get_territory_yaml("nonexistent_territory")
        assert territory is None


class TestBackwardCompatibility:
    """Test backward compatibility aliases."""

    def test_root_whitelist_is_alias(self):
        """Validation: ROOT_WHITELIST is an alias to PROJECT_ROOT_WHITELIST."""
        assert ROOT_WHITELIST is PROJECT_ROOT_WHITELIST

    def test_root_whitelist_content(self):
        """Validation: ROOT_WHITELIST contains expected territory names."""
        # Verify the alias has correct content, not just identity
        assert isinstance(ROOT_WHITELIST, frozenset)
        assert "agentic_core" in ROOT_WHITELIST
        assert "tests" in ROOT_WHITELIST
        assert "docs" in ROOT_WHITELIST

    def test_sovereign_registry_alias(self):
        """Validation: SOVEREIGN_TERRITORIES accessible via package (formerly SOVEREIGN_REGISTRY alias)."""
        from agentic_core.L5_safety.config.structure_blueprint.territories import get_all_territories

        # Verify SOVEREIGN_TERRITORIES is accessible and has expected content
        # Note: SOVEREIGN_REGISTRY was an alias in the deprecated shim
        sovereign_territories = get_all_territories()
        assert hasattr(sovereign_territories, "__getitem__")
        assert "agentic_core" in sovereign_territories

    def test_sovereign_territories_fallback(self):
        """Validation: SOVEREIGN_TERRITORIES accessible via __getattr__ fallback."""
        from agentic_core.L5_safety.config.structure_blueprint import SOVEREIGN_TERRITORIES

        # Check that it's a mapping with expected content
        assert hasattr(SOVEREIGN_TERRITORIES, "__getitem__")
        assert "agentic_core" in SOVEREIGN_TERRITORIES
