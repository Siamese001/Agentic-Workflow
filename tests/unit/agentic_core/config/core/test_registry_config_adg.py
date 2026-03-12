"""ADG-driven tests for agentic_core/config/core/registry_config.py — fan_in=4.

Contract tests: SOVEREIGN_REGISTRY, HEALING_CONFIG, CORE_SUBFOLDER_MAP,
VARIABLE_DEPTH_SUBFOLDERS, L4_APPROVED_FOLDERS.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.config.core.registry_config import (
    CORE_SUBFOLDER_MAP,
    HEALING_CONFIG,
    L4_APPROVED_FOLDERS,
    SOVEREIGN_REGISTRY,
    VARIABLE_DEPTH_SUBFOLDERS,
)


class TestSovereignRegistry:
    def test_is_dict(self):
        assert isinstance(SOVEREIGN_REGISTRY, dict)

    def test_non_empty(self):
        assert len(SOVEREIGN_REGISTRY) > 0

    def test_agentic_core_present(self):
        assert "agentic_core" in SOVEREIGN_REGISTRY

    def test_entries_have_depth_and_subfolders(self):
        for name, entry in SOVEREIGN_REGISTRY.items():
            assert "depth" in entry, f"Missing 'depth' in {name}"
            assert "subfolders" in entry, f"Missing 'subfolders' in {name}"

    def test_depth_values_are_ints(self):
        for name, entry in SOVEREIGN_REGISTRY.items():
            assert isinstance(entry["depth"], int), f"depth not int for {name}"

    def test_subfolders_are_lists(self):
        for name, entry in SOVEREIGN_REGISTRY.items():
            assert isinstance(entry["subfolders"], list), f"subfolders not list for {name}"


class TestHealingConfig:
    def test_is_dict(self):
        assert isinstance(HEALING_CONFIG, dict)

    def test_max_rounds_present(self):
        assert "max_rounds" in HEALING_CONFIG
        assert isinstance(HEALING_CONFIG["max_rounds"], int)

    def test_max_per_file_present(self):
        assert "max_per_file" in HEALING_CONFIG
        assert HEALING_CONFIG["max_per_file"] > 0

    def test_global_budget_positive(self):
        assert HEALING_CONFIG["global_budget"] > 0

    def test_dust_threshold_positive(self):
        assert HEALING_CONFIG["dust_threshold"] > 0


class TestCoreSubfolderMap:
    def test_is_dict(self):
        assert isinstance(CORE_SUBFOLDER_MAP, dict)

    def test_l0_routing_present(self):
        assert "L0_routing" in CORE_SUBFOLDER_MAP

    def test_l5_safety_present(self):
        assert "L5_safety" in CORE_SUBFOLDER_MAP

    def test_values_are_lists(self):
        for k, v in CORE_SUBFOLDER_MAP.items():
            assert isinstance(v, list), f"value for {k} is not a list"


class TestVariableDepthSubfolders:
    def test_is_frozenset(self):
        assert isinstance(VARIABLE_DEPTH_SUBFOLDERS, frozenset)

    def test_contains_l5_safety(self):
        assert "L5_safety" in VARIABLE_DEPTH_SUBFOLDERS

    def test_contains_utils(self):
        assert "utils" in VARIABLE_DEPTH_SUBFOLDERS


class TestL4ApprovedFolders:
    def test_is_set_like(self):
        assert isinstance(L4_APPROVED_FOLDERS, (set, frozenset))

    def test_contains_enforcement_path(self):
        assert any("enforcement" in p for p in L4_APPROVED_FOLDERS)

    def test_all_entries_are_strings(self):
        for entry in L4_APPROVED_FOLDERS:
            assert isinstance(entry, str)
