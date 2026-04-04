"""Tests for structure blueprint yaml_loader module."""
from __future__ import annotations

from agentic_core.L5_safety.config.structure_blueprint.yaml_loader import (
    load_territories,
    load_layer_overrides,
    get_territory,
    get_layer_override,
    match_wildcard_territory,
    get_all_territory_names,
    get_all_layer_names,
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
