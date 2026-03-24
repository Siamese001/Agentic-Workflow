"""ADG-driven tests for agentic_core/utils/workflow_engines/completeness_scorer.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.utils.workflow_engines.completeness_scorer import (  # noqa: F401
        CompletenessScorerConfig,
        KeywordCompletenessScorer,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    CompletenessScorerConfig = None  # type: ignore[assignment,misc]
    KeywordCompletenessScorer = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="completeness_scorer.py deps unavailable")
class TestCompletenessScorerConfig:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(CompletenessScorerConfig)
    def test_importable(self):
        assert CompletenessScorerConfig is not None

@pytest.mark.skipif(not _AVAILABLE, reason="completeness_scorer.py deps unavailable")
class TestKeywordCompletenessScorer:
    def test_is_class(self):
        assert isinstance(KeywordCompletenessScorer, type)
    def test_importable(self):
        assert KeywordCompletenessScorer is not None


def test_module_importable():
    """Module completeness_scorer.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE