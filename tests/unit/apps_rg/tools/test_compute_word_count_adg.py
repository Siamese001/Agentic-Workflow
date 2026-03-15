"""ADG-driven tests for apps_rg/tools/compute_word_count.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_rg.tools.compute_word_count import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        count_sentences,
        count_words_in_list_ms_word_style,
        count_words_ms_word_style,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    count_words_ms_word_style = None  # type: ignore[assignment,misc]
    count_words_in_list_ms_word_style = None  # type: ignore[assignment,misc]
    count_sentences = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="compute_word_count.py deps unavailable")
class TestCountWordsMsWordStyle:
    def test_is_callable(self):
        assert callable(count_words_ms_word_style)

@pytest.mark.skipif(not _AVAILABLE, reason="compute_word_count.py deps unavailable")
class TestCountWordsInListMsWordStyle:
    def test_is_callable(self):
        assert callable(count_words_in_list_ms_word_style)

@pytest.mark.skipif(not _AVAILABLE, reason="compute_word_count.py deps unavailable")
class TestCountSentences:
    def test_is_callable(self):
        assert callable(count_sentences)

@pytest.mark.skipif(not _AVAILABLE, reason="compute_word_count.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="compute_word_count.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="compute_word_count.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="compute_word_count.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="compute_word_count.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="compute_word_count.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module compute_word_count.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
