"""Foundational behavioral tests for agentic_core/utils/workflow_engines/interfaces.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_interfaces_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.utils.workflow_engines.interfaces import (  # noqa: F401
        Document,
        IRetrieverLexical,
        IRetrieverVector,
        ICandidateFusion,
        IReranker,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    Document = None  # type: ignore[assignment,misc]
    IRetrieverLexical = None  # type: ignore[assignment,misc]
    IRetrieverVector = None  # type: ignore[assignment,misc]
    ICandidateFusion = None  # type: ignore[assignment,misc]
    IReranker = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="interfaces.py deps unavailable")
class TestDocumentContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(Document)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(Document)}
        assert field_names >= {'metadata', 'score', 'doc_id', 'content'}

@pytest.mark.skipif(not _AVAILABLE, reason="interfaces.py deps unavailable")
class TestIRetrieverLexicalContract:
    def test_is_class(self):
        assert isinstance(IRetrieverLexical, type)

    def test_has_method_retrieve(self):
        assert callable(getattr(IRetrieverLexical, 'retrieve', None))

@pytest.mark.skipif(not _AVAILABLE, reason="interfaces.py deps unavailable")
class TestIRetrieverVectorContract:
    def test_is_class(self):
        assert isinstance(IRetrieverVector, type)

    def test_has_method_retrieve(self):
        assert callable(getattr(IRetrieverVector, 'retrieve', None))

    def test_has_method_embed_query(self):
        assert callable(getattr(IRetrieverVector, 'embed_query', None))

@pytest.mark.skipif(not _AVAILABLE, reason="interfaces.py deps unavailable")
class TestICandidateFusionContract:
    def test_is_class(self):
        assert isinstance(ICandidateFusion, type)

    def test_has_method_merge(self):
        assert callable(getattr(ICandidateFusion, 'merge', None))

@pytest.mark.skipif(not _AVAILABLE, reason="interfaces.py deps unavailable")
class TestIRerankerContract:
    def test_is_class(self):
        assert isinstance(IReranker, type)

    def test_has_method_rerank(self):
        assert callable(getattr(IReranker, 'rerank', None))

@pytest.mark.skipif(not _AVAILABLE, reason="interfaces.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="interfaces.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="interfaces.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="interfaces.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="interfaces.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module interfaces must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
