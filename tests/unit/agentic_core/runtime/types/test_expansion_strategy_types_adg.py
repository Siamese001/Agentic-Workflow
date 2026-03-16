"""ADG contract tests for runtime/types/expansion_strategy_types.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_expansion_strategy_types_adg")
_emit_applies_guardrail("p0", "test_expansion_strategy_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_expansion_strategy_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_expansion_strategy_types_adg", "state_snapshot")
emit_replay_key("p0", "test_expansion_strategy_types_adg")
emit_determinism_digest("p0", "test_expansion_strategy_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
pytestmark = pytest.mark.unit
from agentic_core.runtime.types.expansion_strategy_types import (
    ExpansionStrategy,
    HyDeDocument,
    HyDeProcessor,
    HyDeResult,
)


class TestExpansionStrategy:
    def test_is_enum(self):
        import enum; assert issubclass(ExpansionStrategy, enum.Enum)
    def test_has_hybrid(self): assert ExpansionStrategy.HYBRID.value == "hybrid"
    def test_four_strategies(self): assert len(list(ExpansionStrategy)) == 4

class TestHyDeDocument:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(HyDeDocument)
    def test_creates(self):
        d = HyDeDocument(content="long enough content here for sure",
                         Archetype="Executive", industry="Tech",
                         strategy=ExpansionStrategy.HYBRID, word_count=15)
        assert d.is_valid is True
    def test_invalid_short_content(self):
        d = HyDeDocument(content="x", Archetype="E", industry="T",
                         strategy=ExpansionStrategy.HYBRID, word_count=1)
        assert d.is_valid is False

class TestHyDeProcessor:
    def test_creates(self): p = HyDeProcessor(); assert p.fallback_enabled is True
    def test_expand_query_stub(self):
        p = HyDeProcessor()
        r = p.expand_query("find me a job", "Executive")
        assert isinstance(r, HyDeResult); assert r.fallback_used is True
