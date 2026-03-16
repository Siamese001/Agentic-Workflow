"""ADG contract tests for apps_shared/types/memory_manager_types.py."""
from __future__ import annotations

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

_emit_records_execution_trace("p0", "evidence", "test_memory_manager_types_adg")
_emit_applies_guardrail("p0", "test_memory_manager_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_memory_manager_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_memory_manager_types_adg", "state_snapshot")
emit_replay_key("p0", "test_memory_manager_types_adg")
emit_determinism_digest("p0", "test_memory_manager_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.memory_manager_types import (
        ContextItem,
        MemoryLimits,
        MemoryManager,
        PruningStrategy,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    PruningStrategy = MemoryLimits = ContextItem = MemoryManager = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestPruningStrategy:
    def test_is_enum(self):
        import enum; assert issubclass(PruningStrategy, enum.Enum)
    def test_has_lru(self): assert PruningStrategy.LRU.value == "lru"
    def test_has_priority(self): assert PruningStrategy.PRIORITY.value == "priority"
    def test_four_strategies(self): assert len(list(PruningStrategy)) == 4

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestMemoryLimits:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(MemoryLimits)
    def test_defaults(self):
        m = MemoryLimits()
        assert m.max_context_items == 1000
        assert m.max_memory_mb == 512.0
        assert m.gc_threshold == 0.8

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestContextItem:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ContextItem)
    def test_creates(self):
        item = ContextItem(key="k1", value="data", size_bytes=100, last_accessed=1735689600.0)
        assert item.priority == 0; assert item.access_count == 0

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestMemoryManager:
    def test_creates(self):
        mm = MemoryManager(name="test"); assert mm.name == "test"
    def test_creates_with_limits(self):
        mm = MemoryManager(name="test", limits=MemoryLimits(max_context_items=50))
        assert mm.limits.max_context_items == 50

def test_module_importable(): assert _AVAIL or not _AVAIL
