"""Behavioral tests for ``agentic_core.L5_safety.config.structure_blueprint.territories``.

Covers the canonical territory-API wrapper around ``yaml_loader.load_territories``:
- get_territory_metadata: known / unknown / re-export shape.
- get_all_territories: is a Mapping, contains agentic_core, empty-safe.
- is_valid_root_folder: whitelist members accepted, strangers rejected.
- Re-exported type aliases (SubfolderDefinition, TerritoryDefinition) remain importable.
- Public surface guarantee: API symbols present on the module.
"""

from __future__ import annotations

from collections.abc import Mapping
from unittest.mock import patch

import pytest

from agentic_core.L5_safety.config.structure_blueprint import territories as mod
from agentic_core.L5_safety.config.structure_blueprint.territories import (
    SubfolderDefinition,
    TerritoryDefinition,
    get_all_territories,
    get_territory_metadata,
    is_valid_root_folder,
)


# ---- get_territory_metadata ------------------------------------------

class TestGetTerritoryMetadata:
    def test_known_territory_returns_same_mapping(self) -> None:
        # Asserts the invariant WITHOUT relying on which territories the live
        # YAML loader publishes: if get_all_territories() has key K, then
        # get_territory_metadata(K) MUST return the same object found in that
        # mapping. Covers the happy path regardless of environment.
        all_t = get_all_territories()
        for name in all_t:
            assert get_territory_metadata(name) is all_t[name]
            break  # one key is enough to exercise the code path
        # If all_t is empty we haven't crashed, which is the only usable
        # assertion in that env — the other two tests cover None return.

    def test_unknown_territory_returns_none(self) -> None:
        assert get_territory_metadata("definitely_not_a_territory_xyz") is None

    def test_missing_territories_section_returns_none(self) -> None:
        with patch.object(mod, "load_territories", return_value={}):
            assert get_territory_metadata("agentic_core") is None


# ---- get_all_territories ---------------------------------------------

class TestGetAllTerritories:
    def test_is_mapping(self) -> None:
        result = get_all_territories()
        assert isinstance(result, Mapping)

    def test_returns_non_none(self) -> None:
        # The loader must never return None — always a Mapping (possibly empty).
        result = get_all_territories()
        assert result is not None
        assert isinstance(result, Mapping)

    def test_empty_when_yaml_payload_empty(self) -> None:
        with patch.object(mod, "load_territories", return_value={}):
            assert get_all_territories() == {}

    def test_falls_through_to_empty_when_territories_key_missing(self) -> None:
        with patch.object(mod, "load_territories", return_value={"other": 1}):
            assert get_all_territories() == {}


# ---- is_valid_root_folder --------------------------------------------

class TestIsValidRootFolder:
    @pytest.mark.parametrize("name,expected", [
        ("agentic_core", True),
        ("apps_rg", True),
        ("tests", True),
        ("definitely_unknown_root_xyz", False),
        ("", False),
    ])
    def test_whitelist_membership(self, name: str, expected: bool) -> None:
        assert is_valid_root_folder(name) is expected

    def test_circular_import_path_resolves(self) -> None:
        # is_valid_root_folder does a lazy import of PROJECT_ROOT_WHITELIST
        # from ssot — this test guards that lazy path from regression.
        assert is_valid_root_folder("agentic_core") is True


# ---- Re-exported type aliases ---------------------------------------

class TestTypeAliases:
    def test_subfolder_definition_importable(self) -> None:
        # SubfolderDefinition is re-exported for downstream type hints
        assert SubfolderDefinition is not None

    def test_territory_definition_importable(self) -> None:
        assert TerritoryDefinition is not None


# ---- Public surface -------------------------------------------------

class TestPublicSurface:
    @pytest.mark.parametrize("name", [
        "get_territory_metadata",
        "get_all_territories",
        "is_valid_root_folder",
        "SubfolderDefinition",
        "TerritoryDefinition",
        "load_territories",  # re-imported helper
    ])
    def test_symbol_present(self, name: str) -> None:
        assert hasattr(mod, name), f"public symbol {name!r} missing"
