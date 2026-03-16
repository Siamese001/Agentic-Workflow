"""ADG-driven tests for mixins/performance_mixin.py — fan_in=1."""
from __future__ import annotations

import time

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_performance_mixin_adg")
_emit_applies_guardrail("p0", "test_performance_mixin_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_performance_mixin_adg", "policy_binding")
_emit_snapshots_state("p0", "test_performance_mixin_adg", "state_snapshot")
emit_replay_key("p0", "test_performance_mixin_adg")
emit_determinism_digest("p0", "test_performance_mixin_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.mixins.performance_mixin import CacheEntry, PerformanceMixin


class TestCacheEntry:
    def test_creates(self):
        entry = CacheEntry(value={"result": True})
        assert entry.value == {"result": True}

    def test_not_expired_fresh(self):
        entry = CacheEntry(value="test", ttl_seconds=60.0)
        assert entry.is_expired() is False

    def test_expired_old(self):
        entry = CacheEntry(value="test", created_at=time.time() - 400, ttl_seconds=300.0)
        assert entry.is_expired() is True

    def test_hits_default_zero(self):
        entry = CacheEntry(value="v")
        assert entry.hits == 0


class TestPerformanceMixin:
    def test_importable(self):
        assert callable(PerformanceMixin)

    def test_has_cache_get(self):
        assert hasattr(PerformanceMixin, "cache_get")

    def test_has_cache_set(self):
        assert hasattr(PerformanceMixin, "cache_set")
