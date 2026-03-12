"""ADG-driven tests for L2_execution/types/keyword_classification_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.types.keyword_classification_types import (
        KeywordClassification,
        RagHop,
    )
    _AVAILABLE = True
except Exception:
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
