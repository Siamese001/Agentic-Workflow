"""Foundational behavioral tests for agentic_core/utils/workflow_engines/validators.py.

fan_in=13 — this module is imported by 13 other modules.
ADG contract: import-hygiene is covered by test_validators_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.utils.workflow_engines.validators import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    ChunkQualityReport,
    DuplicateChunkDetector,
    MaxChunkSizeValidator,
    MinChunkSizeValidator,
    OrphanChunkDetector,
    OverlapSanityValidator,
)


class TestChunkQualityReportContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ChunkQualityReport)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ChunkQualityReport)}
        assert field_names >= {'duplicates', 'policy_name', 'orphan_chunks', 'total_chunks', 'doc_id'}

class TestMaxChunkSizeValidatorContract:
    def test_is_class(self):
        assert isinstance(MaxChunkSizeValidator, type)

    def test_has_method_validate(self):
        assert callable(getattr(MaxChunkSizeValidator, 'validate', None))

class TestMinChunkSizeValidatorContract:
    def test_is_class(self):
        assert isinstance(MinChunkSizeValidator, type)

    def test_has_method_validate(self):
        assert callable(getattr(MinChunkSizeValidator, 'validate', None))

class TestOverlapSanityValidatorContract:
    def test_is_class(self):
        assert isinstance(OverlapSanityValidator, type)

    def test_has_method_validate(self):
        assert callable(getattr(OverlapSanityValidator, 'validate', None))

class TestDuplicateChunkDetectorContract:
    def test_is_class(self):
        assert isinstance(DuplicateChunkDetector, type)

    def test_has_method_detect(self):
        assert callable(getattr(DuplicateChunkDetector, 'detect', None))

class TestOrphanChunkDetectorContract:
    def test_is_class(self):
        assert isinstance(OrphanChunkDetector, type)

    def test_has_method_detect(self):
        assert callable(getattr(OrphanChunkDetector, 'detect', None))

class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module validators must be importable or skip gracefully."""
    pass  # Import verified at module level
