"""ADG-driven tests for agentic_core/L0_routing/scripts/execution_context.py — fan_in=2.

Contract tests: ConfigSurface, ExecutionContext, BaseRefiner.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L0_routing.scripts.execution_context import (
    BaseRefiner,
    ConfigSurface,
    ExecutionContext,
)


class TestConfigSurface:
    def test_creates_valid(self):
        cs = ConfigSurface(
            threshold_configs={"threshold": 0.85},
            tier_constants={"X": 0.75, "Y": 0.40},
            tool_budget_caps={"max_tool_calls": 100},
            freshness_windows={"ttl": 3600},
        )
        assert cs.threshold_configs["threshold"] == 0.85

    def test_is_frozen(self):
        cs = ConfigSurface(
            threshold_configs={},
            tier_constants={},
            tool_budget_caps={},
            freshness_windows={},
        )
        with pytest.raises(Exception):
            cs.threshold_configs = {"new": 0.5}  # frozen

    def test_compute_hash_returns_hex_string(self):
        cs = ConfigSurface(
            threshold_configs={"t": 0.9},
            tier_constants={"x": 0.5},
            tool_budget_caps={"max": 10},
            freshness_windows={"ttl": 100},
        )
        h = cs.compute_hash()
        assert isinstance(h, str)
        assert len(h) == 64

    def test_compute_hash_deterministic(self):
        cs1 = ConfigSurface(
            threshold_configs={"t": 0.9},
            tier_constants={},
            tool_budget_caps={},
            freshness_windows={},
        )
        cs2 = ConfigSurface(
            threshold_configs={"t": 0.9},
            tier_constants={},
            tool_budget_caps={},
            freshness_windows={},
        )
        assert cs1.compute_hash() == cs2.compute_hash()

    def test_different_configs_different_hash(self):
        cs1 = ConfigSurface(
            threshold_configs={"t": 0.9},
            tier_constants={},
            tool_budget_caps={},
            freshness_windows={},
        )
        cs2 = ConfigSurface(
            threshold_configs={"t": 0.8},
            tier_constants={},
            tool_budget_caps={},
            freshness_windows={},
        )
        assert cs1.compute_hash() != cs2.compute_hash()


class TestExecutionContext:
    def test_creates_with_defaults(self):
        ctx = ExecutionContext()
        assert ctx.mission_id == ""
        assert ctx.step_id == ""
        assert ctx.replay_mode is False
        assert ctx.safety_status == "PENDING"

    def test_to_dict_has_required_keys(self):
        ctx = ExecutionContext(mission_id="m1", step_id="s1")
        d = ctx.to_dict()
        for key in ("mission_id", "step_id", "timestamp", "replay_mode", "safety_status"):
            assert key in d

    def test_to_dict_mission_id(self):
        ctx = ExecutionContext(mission_id="mission_abc")
        assert ctx.to_dict()["mission_id"] == "mission_abc"

    def test_set_config_surface_updates_hash(self):
        ctx = ExecutionContext()
        assert ctx.config_surface_hash is None
        cs = ConfigSurface(
            threshold_configs={"t": 0.9},
            tier_constants={},
            tool_budget_caps={},
            freshness_windows={},
        )
        ctx.set_config_surface(cs)
        assert ctx.config_surface_hash is not None
        assert len(ctx.config_surface_hash) == 64

    def test_trace_id_default_none(self):
        ctx = ExecutionContext()
        assert ctx.trace_id is None

    def test_active_policy_hash_default_none(self):
        ctx = ExecutionContext()
        assert ctx.active_policy_hash is None


class TestBaseRefiner:
    def test_creates_without_config(self):
        r = BaseRefiner()
        assert r.config == {}
        assert r.weights == {}

    def test_creates_with_config(self):
        r = BaseRefiner(config={"weights": {"score": 2.0}})
        assert r.weights == {"score": 2.0}

    def test_refine_applies_weights(self):
        r = BaseRefiner()
        result = r.refine({"score": 10.0}, weights={"score": 2.0})
        assert result["score"] == 20.0

    def test_refine_no_weights_returns_copy(self):
        r = BaseRefiner()
        data = {"value": 42}
        result = r.refine(data)
        assert result["value"] == 42
        assert result is not data  # copy, not same object

    def test_refine_skips_non_numeric(self):
        r = BaseRefiner()
        result = r.refine({"name": "foo", "score": 10.0}, weights={"score": 3.0, "name": 2.0})
        assert result["name"] == "foo"  # string not multiplied
        assert result["score"] == pytest.approx(30.0)
