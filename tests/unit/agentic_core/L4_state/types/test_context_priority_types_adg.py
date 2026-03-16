"""ADG contract tests for L4_state/types/context_priority_types.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_context_priority_types_adg")
_emit_applies_guardrail("p0", "test_context_priority_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_context_priority_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_context_priority_types_adg", "state_snapshot")
emit_replay_key("p0", "test_context_priority_types_adg")
emit_determinism_digest("p0", "test_context_priority_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
pytestmark = pytest.mark.unit
from agentic_core.L4_state.types.context_priority_types import ContextChunk, ContextPriority, ContextType


class TestContextPriority:
    def test_is_enum(self):
        import enum; assert issubclass(ContextPriority, enum.Enum)
    def test_has_critical(self):
        assert ContextPriority.CRITICAL.value == "critical"

class TestContextType:
    def test_is_enum(self):
        import enum; assert issubclass(ContextType, enum.Enum)

class TestContextChunk:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ContextChunk)
    def test_creates(self):
        c = ContextChunk(id="c1", content="hello", chunk_type=ContextType.EXAMPLE,
                         priority=ContextPriority.LOW, token_count=5)
        assert c.id == "c1"
        assert c.token_count == 5
