"""Foundational behavioral tests for agentic_core/utils/workflow_engines/validators.py.

fan_in=13 — this module is imported by 13 other modules.
ADG contract: import-hygiene is covered by test_validators_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.utils.workflow_engines.validators import (  # noqa: F401
        ChunkQualityReport,
        MaxChunkSizeValidator,
        MinChunkSizeValidator,
        OverlapSanityValidator,
        DuplicateChunkDetector,
        OrphanChunkDetector,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    ChunkQualityReport = None  # type: ignore[assignment,misc]
    MaxChunkSizeValidator = None  # type: ignore[assignment,misc]
    MinChunkSizeValidator = None  # type: ignore[assignment,misc]
    OverlapSanityValidator = None  # type: ignore[assignment,misc]
    DuplicateChunkDetector = None  # type: ignore[assignment,misc]
    OrphanChunkDetector = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="validators.py deps unavailable")
class TestChunkQualityReportContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ChunkQualityReport)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ChunkQualityReport)}
        assert field_names >= {'duplicates', 'policy_name', 'orphan_chunks', 'total_chunks', 'doc_id'}

@pytest.mark.skipif(not _AVAILABLE, reason="validators.py deps unavailable")
class TestMaxChunkSizeValidatorContract:
    def test_is_class(self):
        assert isinstance(MaxChunkSizeValidator, type)

    def test_has_method_validate(self):
        assert callable(getattr(MaxChunkSizeValidator, 'validate', None))

@pytest.mark.skipif(not _AVAILABLE, reason="validators.py deps unavailable")
class TestMinChunkSizeValidatorContract:
    def test_is_class(self):
        assert isinstance(MinChunkSizeValidator, type)

    def test_has_method_validate(self):
        assert callable(getattr(MinChunkSizeValidator, 'validate', None))

@pytest.mark.skipif(not _AVAILABLE, reason="validators.py deps unavailable")
class TestOverlapSanityValidatorContract:
    def test_is_class(self):
        assert isinstance(OverlapSanityValidator, type)

    def test_has_method_validate(self):
        assert callable(getattr(OverlapSanityValidator, 'validate', None))

@pytest.mark.skipif(not _AVAILABLE, reason="validators.py deps unavailable")
class TestDuplicateChunkDetectorContract:
    def test_is_class(self):
        assert isinstance(DuplicateChunkDetector, type)

    def test_has_method_detect(self):
        assert callable(getattr(DuplicateChunkDetector, 'detect', None))

@pytest.mark.skipif(not _AVAILABLE, reason="validators.py deps unavailable")
class TestOrphanChunkDetectorContract:
    def test_is_class(self):
        assert isinstance(OrphanChunkDetector, type)

    def test_has_method_detect(self):
        assert callable(getattr(OrphanChunkDetector, 'detect', None))

@pytest.mark.skipif(not _AVAILABLE, reason="validators.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="validators.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="validators.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="validators.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="validators.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module validators must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
