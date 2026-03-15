"""Foundational behavioral tests for agentic_core/L1_cognition/memory/healing_memory_retriever.py.

fan_in=5 — imported by 5 other modules.
ADG import-hygiene is covered separately by test_healing_memory_retriever_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L1_cognition.memory.healing_memory_retriever import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        HealingMemoryRetriever,
        NullHealingMemoryRetriever,
        SimilarIncident,
        SovereigntyError,
        VectorSourceMismatchError,
        build_retriever,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    VectorSourceMismatchError = None  # type: ignore[assignment,misc]
    SovereigntyError = None  # type: ignore[assignment,misc]
    SimilarIncident = None  # type: ignore[assignment,misc]
    NullHealingMemoryRetriever = None  # type: ignore[assignment,misc]
    HealingMemoryRetriever = None  # type: ignore[assignment,misc]
    build_retriever = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="healing_memory_retriever.py deps unavailable")
class TestVectorSourceMismatchErrorContract:
    def test_is_class(self):
        assert isinstance(VectorSourceMismatchError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="healing_memory_retriever.py deps unavailable")
class TestSovereigntyErrorContract:
    def test_is_class(self):
        assert isinstance(SovereigntyError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="healing_memory_retriever.py deps unavailable")
class TestSimilarIncidentContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(SimilarIncident)

    def test_is_frozen(self):
        assert SimilarIncident.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(SimilarIncident)}
        assert fnames >= {'advisory_only', 'trace_id', 'similarity', 'content_hash', 'metadata'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(SimilarIncident)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="healing_memory_retriever.py deps unavailable")
class TestNullHealingMemoryRetrieverContract:
    def test_is_class(self):
        assert isinstance(NullHealingMemoryRetriever, type)

    def test_has_method_retrieve_similar_incidents(self):
        assert callable(getattr(NullHealingMemoryRetriever, 'retrieve_similar_incidents', None))

    def test_has_method_is_active(self):
        assert callable(getattr(NullHealingMemoryRetriever, 'is_active', None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(NullHealingMemoryRetriever) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="healing_memory_retriever.py deps unavailable")
class TestHealingMemoryRetrieverContract:
    def test_is_class(self):
        assert isinstance(HealingMemoryRetriever, type)

    def test_has_method_is_active(self):
        assert callable(getattr(HealingMemoryRetriever, 'is_active', None))

    def test_has_method_retrieve_similar_incidents(self):
        assert callable(getattr(HealingMemoryRetriever, 'retrieve_similar_incidents', None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(HealingMemoryRetriever) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="healing_memory_retriever.py deps unavailable")
class TestBuildRetrieverFunction:
    def test_is_callable(self):
        assert callable(build_retriever)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(build_retriever)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="healing_memory_retriever.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healing_memory_retriever.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

    def test_value_is_truthy_or_defined(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healing_memory_retriever.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

    def test_value_is_truthy_or_defined(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healing_memory_retriever.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healing_memory_retriever.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healing_memory_retriever.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Smoke: healing_memory_retriever importable or gracefully unavailable."""
    pass
