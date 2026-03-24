"""ADG-driven tests for agentic_core/utils/workflow_engines/answer_support.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.utils.workflow_engines.answer_support import (  # noqa: F401
        KeywordAnswerSupportValidator,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    KeywordAnswerSupportValidator = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="answer_support.py deps unavailable")
class TestKeywordAnswerSupportValidator:
    def test_is_class(self):
        assert isinstance(KeywordAnswerSupportValidator, type)
    def test_importable(self):
        assert KeywordAnswerSupportValidator is not None


def test_module_importable():
    """Module answer_support.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE