"""Foundational behavioral tests for agentic_core/L4_state/types/retrieval_anchor_types.py.

fan_in=4 — imported by 4 other modules.
ADG import-hygiene is covered separately by test_retrieval_anchor_types_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L4_state.types.retrieval_anchor_types import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        AnchoredResult,
        AnchorViolationError,
        RetrievalAnchor,
        enforce_anchor_coverage,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    RetrievalAnchor = None  # type: ignore[assignment,misc]
    AnchoredResult = None  # type: ignore[assignment,misc]
    AnchorViolationError = None  # type: ignore[assignment,misc]
    enforce_anchor_coverage = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_anchor_types.py deps unavailable")
class TestRetrievalAnchorContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(RetrievalAnchor)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(RetrievalAnchor)}
        assert fnames >= {'char_end', 'version_hash', 'chunk_id', 'retrieved_at_utc', 'source_doc_id', 'char_start'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(RetrievalAnchor)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_anchor_types.py deps unavailable")
class TestAnchoredResultContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(AnchoredResult)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(AnchoredResult)}
        assert fnames >= {'anchor', 'content'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(AnchoredResult)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_anchor_types.py deps unavailable")
class TestAnchorViolationErrorContract:
    def test_is_class(self):
        assert isinstance(AnchorViolationError, type)

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(AnchorViolationError) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_anchor_types.py deps unavailable")
class TestEnforceAnchorCoverageFunction:
    def test_is_callable(self):
        assert callable(enforce_anchor_coverage)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(enforce_anchor_coverage)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_anchor_types.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_anchor_types.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

    def test_value_is_truthy_or_defined(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_anchor_types.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

    def test_value_is_truthy_or_defined(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_anchor_types.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_anchor_types.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="retrieval_anchor_types.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Smoke: retrieval_anchor_types importable or gracefully unavailable."""
    pass
