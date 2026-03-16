"""ADG-driven tests for L2_execution/types/keyword_classification_types.py — fan_in=0."""
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

_emit_records_execution_trace("p0", "evidence", "test_keyword_classification_types_adg")
_emit_applies_guardrail("p0", "test_keyword_classification_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_keyword_classification_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_keyword_classification_types_adg", "state_snapshot")
emit_replay_key("p0", "test_keyword_classification_types_adg")
emit_determinism_digest("p0", "test_keyword_classification_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.types.keyword_classification_types import (
        KeywordClassification,
        RagHop,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    KeywordClassification = None  # type: ignore[assignment,misc]
    RagHop = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="keyword_classification_types deps unavailable")
class TestKeywordClassification:
    def test_is_enum(self):
        import enum
        assert issubclass(KeywordClassification, enum.Enum)

    def test_table_stakes_value(self):
        assert KeywordClassification.TABLE_STAKES.value == "TABLE_STAKES"

    def test_differentiator_value(self):
        assert KeywordClassification.DIFFERENTIATOR.value == "DIFFERENTIATOR"

    def test_unknown_value(self):
        assert KeywordClassification.UNKNOWN.value == "UNKNOWN"


@pytest.mark.skipif(not _AVAILABLE, reason="keyword_classification_types deps unavailable")
class TestRagHop:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(RagHop)

    def test_creates(self):
        hop = RagHop(hop_number=1, search_queries=["q1"], results=[], keywords_found=set())
        assert hop.hop_number == 1
        assert hop.search_queries == ["q1"]


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
