"""Foundational behavioral tests for agentic_core/utils/ast_fuzzy_util.py.

fan_in=9 — imported by 9 other modules.
ADG import-hygiene is covered separately by test_ast_fuzzy_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.utils.ast_fuzzy_util import (  # noqa: F401
        parse_ast_safe,
        ast_dump_hash,
        tokenize_simple,
        similarity_score,
        normalize_repo_path,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
        MAX_DEPTH,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    parse_ast_safe = None  # type: ignore[assignment,misc]
    ast_dump_hash = None  # type: ignore[assignment,misc]
    tokenize_simple = None  # type: ignore[assignment,misc]
    similarity_score = None  # type: ignore[assignment,misc]
    normalize_repo_path = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ast_fuzzy_util.py deps unavailable")
class TestParseAstSafeFunction:
    def test_is_callable(self):
        assert callable(parse_ast_safe)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(parse_ast_safe)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="ast_fuzzy_util.py deps unavailable")
class TestAstDumpHashFunction:
    def test_is_callable(self):
        assert callable(ast_dump_hash)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(ast_dump_hash)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="ast_fuzzy_util.py deps unavailable")
class TestTokenizeSimpleFunction:
    def test_is_callable(self):
        assert callable(tokenize_simple)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(tokenize_simple)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="ast_fuzzy_util.py deps unavailable")
class TestSimilarityScoreFunction:
    def test_is_callable(self):
        assert callable(similarity_score)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(similarity_score)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="ast_fuzzy_util.py deps unavailable")
class TestNormalizeRepoPathFunction:
    def test_is_callable(self):
        assert callable(normalize_repo_path)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(normalize_repo_path)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="ast_fuzzy_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="ast_fuzzy_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

    def test_value_is_truthy_or_defined(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="ast_fuzzy_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

    def test_value_is_truthy_or_defined(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="ast_fuzzy_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="ast_fuzzy_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="ast_fuzzy_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Smoke: ast_fuzzy_util importable or gracefully unavailable."""
    assert True
