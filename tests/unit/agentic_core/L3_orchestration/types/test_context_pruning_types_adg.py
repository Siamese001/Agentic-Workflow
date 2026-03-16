"""ADG contract tests for L3_orchestration/types/context_pruning_types.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_context_pruning_types_adg")
_emit_applies_guardrail("p0", "test_context_pruning_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_context_pruning_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_context_pruning_types_adg", "state_snapshot")
emit_replay_key("p0", "test_context_pruning_types_adg")
emit_determinism_digest("p0", "test_context_pruning_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
pytestmark = pytest.mark.unit
from agentic_core.L3_orchestration.types.context_pruning_types import (
    CRITICAL_DNA_KEYS,
    ContextPruningStrategy,
    PruningMetrics,
)


class TestCriticalDnaKeys:
    def test_is_frozenset(self): assert isinstance(CRITICAL_DNA_KEYS, frozenset)
    def test_contains_original_goal(self): assert "original_goal" in CRITICAL_DNA_KEYS

class TestPruningMetrics:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(PruningMetrics)
    def test_defaults_zero(self): m = PruningMetrics(); assert m.total_prunes == 0

class TestContextPruningStrategy:
    def test_creates(self): s = ContextPruningStrategy(); assert s is not None
    def test_no_prune_needed(self):
        s = ContextPruningStrategy()
        assert s.should_prune({"a": 1}) is False
