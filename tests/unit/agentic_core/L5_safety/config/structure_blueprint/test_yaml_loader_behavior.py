"""Behavioral tests for ``agentic_core.L5_safety.config.structure_blueprint.yaml_loader``.

Covers the hardcoded-constants loader that territories/_constants/ssot depend on:
- load_territories / load_layer_overrides / load_ast_signals return stable dicts.
- Module-level cache: second call returns same object.
- get_territory: known key returns dict, unknown returns None.
- get_layer_override: known layer returns dict, unknown returns None.
- match_wildcard_territory: returns None when no wildcards match.
- get_all_territory_names / get_all_layer_names return lists.
"""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.config.structure_blueprint import yaml_loader as mod
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


@pytest.fixture(autouse=True)
def clear_cache() -> None:
    """Reset module cache before each test so caching semantics can be verified."""
    mod._loaded_data.clear()


# ---- load_territories -------------------------------------------------

class TestLoadTerritories:
    def test_returns_dict(self) -> None:
        data = load_territories()
        assert isinstance(data, dict)

    def test_has_territories_key(self) -> None:
        data = load_territories()
        assert "territories" in data

    def test_cached_between_calls(self) -> None:
        first = load_territories()
        second = load_territories()
        assert first is second

    def test_territories_contains_root_and_config(self) -> None:
        data = load_territories()
        assert "__root__" in data["territories"]
        assert "config" in data["territories"]


# ---- load_layer_overrides --------------------------------------------

class TestLoadLayerOverrides:
    def test_returns_dict_with_overrides_key(self) -> None:
        data = load_layer_overrides()
        assert "overrides" in data

    def test_cached_between_calls(self) -> None:
        assert load_layer_overrides() is load_layer_overrides()


# ---- load_ast_signals -------------------------------------------------

class TestLoadAstSignals:
    def test_has_schema_version(self) -> None:
        data = load_ast_signals()
        assert "schema_version" in data
        assert "signals" in data

    def test_cached_between_calls(self) -> None:
        assert load_ast_signals() is load_ast_signals()


# ---- get_territory ----------------------------------------------------

class TestGetTerritory:
    def test_known_key_returns_dict(self) -> None:
        result = get_territory("__root__")
        assert result is not None
        assert isinstance(result, dict)

    def test_unknown_key_returns_none(self) -> None:
        assert get_territory("nonexistent_territory_xyz") is None


# ---- get_layer_override ----------------------------------------------

class TestGetLayerOverride:
    def test_unknown_layer_returns_none(self) -> None:
        assert get_layer_override("L999_fake") is None

    def test_known_layer_returns_dict_if_present(self) -> None:
        # Don't assume which layers have overrides — just invariant check
        data = load_layer_overrides()
        overrides = data.get("overrides", {})
        for layer_name in overrides:
            result = get_layer_override(layer_name)
            assert result is overrides[layer_name]
            break


# ---- match_wildcard_territory ----------------------------------------

class TestMatchWildcardTerritory:
    def test_no_match_returns_none(self) -> None:
        assert match_wildcard_territory("completely_unknown_name") is None

    def test_empty_name_returns_none(self) -> None:
        assert match_wildcard_territory("") is None


# ---- get_all_territory_names -----------------------------------------

class TestGetAllTerritoryNames:
    def test_returns_list(self) -> None:
        names = get_all_territory_names()
        assert isinstance(names, list)

    def test_contains_root(self) -> None:
        assert "__root__" in get_all_territory_names()

    def test_contains_config(self) -> None:
        assert "config" in get_all_territory_names()


# ---- get_all_layer_names ---------------------------------------------

class TestGetAllLayerNames:
    def test_returns_list(self) -> None:
        assert isinstance(get_all_layer_names(), list)


# ---- __all__ public surface -----------------------------------------

class TestPublicSurface:
    @pytest.mark.parametrize("name", [
        "load_territories", "load_layer_overrides", "load_ast_signals",
        "get_territory", "get_layer_override", "match_wildcard_territory",
        "get_all_territory_names", "get_all_layer_names",
    ])
    def test_symbol_present(self, name: str) -> None:
        assert hasattr(mod, name)
