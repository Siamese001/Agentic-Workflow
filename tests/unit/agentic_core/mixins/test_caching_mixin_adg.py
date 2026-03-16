"""ADG-driven tests for agentic_core/mixins/caching_mixin.py — fan_in=2.

Contract tests: CacheEntry, CacheConfig, CachingMixin API.
"""
from __future__ import annotations

import time

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_caching_mixin_adg")
_emit_applies_guardrail("p0", "test_caching_mixin_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_caching_mixin_adg", "policy_binding")
_emit_snapshots_state("p0", "test_caching_mixin_adg", "state_snapshot")
emit_replay_key("p0", "test_caching_mixin_adg")
emit_determinism_digest("p0", "test_caching_mixin_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_caching_mixin_adg", "execution_auth")
_emit_validates_capability("p2", "test_caching_mixin_adg", "capability_check")
_emit_routes_to_capability("p2", "test_caching_mixin_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_caching_mixin_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_caching_mixin_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_caching_mixin_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_caching_mixin_adg", "exec_output")
_emit_dispatches_agent("p3", "test_caching_mixin_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_caching_mixin_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_caching_mixin_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_caching_mixin_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_caching_mixin_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_caching_mixin_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_caching_mixin_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_caching_mixin_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_caching_mixin_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_caching_mixin_adg", "eval_metric")
_emit_stores_embedding("p4", "test_caching_mixin_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_caching_mixin_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_caching_mixin_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.mixins.caching_mixin import CacheConfig, CacheEntry, CachingMixin


class TestCacheEntry:
    def test_creates_with_value(self):
        entry = CacheEntry(value=42)
        assert entry.value == 42

    def test_default_ttl(self):
        entry = CacheEntry(value="x")
        assert entry.ttl_seconds == 300.0

    def test_default_hits_zero(self):
        entry = CacheEntry(value="x")
        assert entry.hits == 0

    def test_fresh_entry_not_expired(self):
        entry = CacheEntry(value="x", ttl_seconds=3600.0)
        assert entry.is_expired() is False

    def test_expired_entry_is_expired(self):
        entry = CacheEntry(value="x", created_at=time.time() - 1000, ttl_seconds=1.0)
        assert entry.is_expired() is True

    def test_created_at_is_float(self):
        entry = CacheEntry(value="x")
        assert isinstance(entry.created_at, float)


class TestCacheConfig:
    def test_defaults(self):
        cfg = CacheConfig()
        assert cfg.enabled is True
        assert cfg.max_size == 1000
        assert cfg.default_ttl == 300.0

    def test_custom_config(self):
        cfg = CacheConfig(enabled=False, max_size=50, default_ttl=60.0)
        assert cfg.enabled is False
        assert cfg.max_size == 50
        assert cfg.default_ttl == 60.0


class TestCachingMixinInterface:
    def test_class_importable(self):
        assert callable(CachingMixin)

    def test_has_cache_get(self):
        assert hasattr(CachingMixin, "cache_get")

    def test_has_cache_set(self):
        assert hasattr(CachingMixin, "cache_set")

    def test_has_cache_invalidate(self):
        assert hasattr(CachingMixin, "cache_invalidate")

    def test_has_cached_decorator(self):
        assert hasattr(CachingMixin, "cached")

    def test_instance_cache_get_miss_returns_tuple(self):
        class MyComponent(CachingMixin):
            pass
        comp = MyComponent()
        found, value = comp.cache_get("nonexistent_key_xyz")
        assert found is False
        assert value is None

    def test_instance_cache_set_and_get(self):
        class MyComponent(CachingMixin):
            pass
        comp = MyComponent()
        comp.cache_set("my_key", {"data": 42})
        found, value = comp.cache_get("my_key")
        assert found is True
        assert value == {"data": 42}

    def test_instance_cache_invalidate(self):
        class MyComponent(CachingMixin):
            pass
        comp = MyComponent()
        comp.cache_set("my_key", "value")
        comp.cache_invalidate("my_key")
        found, value = comp.cache_get("my_key")
        assert found is False
