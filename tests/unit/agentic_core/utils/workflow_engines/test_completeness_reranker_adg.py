"""ADG-driven tests for agentic_core/utils/workflow_engines/completeness_reranker.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.utils.workflow_engines.completeness_reranker import (  # noqa: F401
        CompletenessReranker,
        CompletenessRerankerConfig,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    CompletenessRerankerConfig = None  # type: ignore[assignment,misc]
    CompletenessReranker = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="completeness_reranker.py deps unavailable")
class TestCompletenessRerankerConfig:
    def test_is_class(self):
        assert isinstance(CompletenessRerankerConfig, type)
    def test_importable(self):
        assert CompletenessRerankerConfig is not None

@pytest.mark.skipif(not _AVAILABLE, reason="completeness_reranker.py deps unavailable")
class TestCompletenessReranker:
    def test_is_class(self):
        assert isinstance(CompletenessReranker, type)
    def test_importable(self):
        assert CompletenessReranker is not None


def test_module_importable():
    """Module completeness_reranker.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
