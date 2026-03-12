"""ADG-driven tests for L1_cognition/types/result_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.types.result_types import (
    DraftResult,
    QaResult,
    StrategyResultStrategy,
)


class TestStrategyResultStrategy:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(StrategyResultStrategy)

    def test_creates(self):
        s = StrategyResultStrategy(_strategy="react", _confidence=0.9)
        assert s._strategy == "react"
        assert s._confidence == 0.9


class TestDraftResult:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(DraftResult)

    def test_creates(self):
        dr = DraftResult(_sections=["intro", "body"], _content="hello world")
        assert dr._content == "hello world"
        assert len(dr._sections) == 2


class TestQaResult:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(QaResult)

    def test_creates(self):
        qa = QaResult(_findings="no issues found", confidence=0.95)
        assert qa._findings == "no issues found"
        assert qa.confidence == 0.95
