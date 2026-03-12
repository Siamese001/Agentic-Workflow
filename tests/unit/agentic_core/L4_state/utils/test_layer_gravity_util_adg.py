"""ADG-driven tests for agentic_core/L4_state/utils/layer_gravity_util.py — fan_in=2.

Contract tests: LAYER_ORDER, GRAVITY_RULES, and gravity utility functions.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L4_state.utils.layer_gravity_util import (
    GRAVITY_RULES,
    LAYER_ORDER,
    extract_layer_from_module,
    extract_layer_from_path,
    get_allowed_layers,
    get_layer_order,
    is_gravity_violation,
)


class TestLayerOrder:
    def test_all_seven_layers_present(self):
        for i, layer in enumerate(["L0", "L1", "L2", "L3", "L4", "L5", "L6"]):
            assert layer in LAYER_ORDER
            assert LAYER_ORDER[layer] == i

    def test_l0_lowest(self):
        assert LAYER_ORDER["L0"] == 0

    def test_l6_highest(self):
        assert LAYER_ORDER["L6"] == 6


class TestGravityRules:
    def test_l0_only_allows_l0(self):
        assert GRAVITY_RULES["L0"] == {"L0"}

    def test_l3_allows_l0_through_l3(self):
        assert GRAVITY_RULES["L3"] == {"L0", "L1", "L2", "L3"}

    def test_l6_allows_all_layers(self):
        assert GRAVITY_RULES["L6"] == {"L0", "L1", "L2", "L3", "L4", "L5", "L6"}

    def test_each_layer_includes_itself(self):
        for layer in LAYER_ORDER:
            assert layer in GRAVITY_RULES[layer]


class TestExtractLayerFromPath:
    def test_l5_path(self):
        assert extract_layer_from_path("agentic_core/L5_safety/reasoning/Agent.py") == "L5"

    def test_l2_path(self):
        assert extract_layer_from_path("agentic_core/L2_execution/types/foo.py") == "L2"

    def test_app_path_returns_none(self):
        assert extract_layer_from_path("apps_rg/engines/tool.py") is None

    def test_backslash_path(self):
        assert extract_layer_from_path("agentic_core\\L3_orchestration\\foo.py") == "L3"

    def test_root_file_no_layer(self):
        assert extract_layer_from_path("setup.py") is None


class TestExtractLayerFromModule:
    def test_l3_module(self):
        assert extract_layer_from_module("agentic_core.L3_orchestration.reasoning") == "L3"

    def test_l1_module(self):
        assert extract_layer_from_module("agentic_core.L1_cognition.types") == "L1"

    def test_non_layer_module_returns_none(self):
        assert extract_layer_from_module("apps_shared.common_utils") is None


class TestIsGravityViolation:
    def test_upward_import_is_violation(self):
        assert is_gravity_violation("L3", "L5") is True

    def test_downward_import_is_ok(self):
        assert is_gravity_violation("L5", "L3") is False

    def test_same_layer_is_ok(self):
        assert is_gravity_violation("L3", "L3") is False

    def test_l0_importing_l1_is_violation(self):
        assert is_gravity_violation("L0", "L1") is True

    def test_l6_importing_l0_is_ok(self):
        assert is_gravity_violation("L6", "L0") is False


class TestGetAllowedLayers:
    def test_l3_returns_correct_set(self):
        assert get_allowed_layers("L3") == {"L0", "L1", "L2", "L3"}

    def test_unknown_layer_returns_empty(self):
        assert get_allowed_layers("L99") == set()

    def test_l0_returns_only_l0(self):
        assert get_allowed_layers("L0") == {"L0"}


class TestGetLayerOrder:
    def test_l3_returns_3(self):
        assert get_layer_order("L3") == 3

    def test_l0_returns_0(self):
        assert get_layer_order("L0") == 0

    def test_invalid_returns_negative_1(self):
        assert get_layer_order("invalid") == -1
