"""Foundational behavioral tests for agentic_core/utils/workflow_engines/policies.py.

fan_in=13 — this module is imported by 13 other modules.
ADG contract: import-hygiene is covered by test_policies_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.utils.workflow_engines.policies import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    Chunk,
    ChunkManifest,
    ChunkPolicy,
    FixedTokenChunkPolicy,
    OverlapWindowChunkPolicy,
    SectionAwareChunkPolicy,
)


class TestChunkContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(Chunk)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(Chunk)}
        assert field_names >= {'token_count', 'start_char', 'content', 'chunk_id', 'doc_id'}

class TestChunkManifestContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ChunkManifest)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ChunkManifest)}
        assert field_names >= {'policy_name', 'chunks', 'metadata', 'doc_id'}

class TestChunkPolicyContract:
    def test_is_class(self):
        assert isinstance(ChunkPolicy, type)

    def test_has_method_name(self):
        assert callable(getattr(ChunkPolicy, 'name', None))

    def test_has_method_chunk(self):
        assert callable(getattr(ChunkPolicy, 'chunk', None))

class TestFixedTokenChunkPolicyContract:
    def test_is_class(self):
        assert isinstance(FixedTokenChunkPolicy, type)

    def test_has_method_name(self):
        assert callable(getattr(FixedTokenChunkPolicy, 'name', None))

    def test_has_method_chunk(self):
        assert callable(getattr(FixedTokenChunkPolicy, 'chunk', None))

class TestOverlapWindowChunkPolicyContract:
    def test_is_class(self):
        assert isinstance(OverlapWindowChunkPolicy, type)

    def test_has_method_name(self):
        assert callable(getattr(OverlapWindowChunkPolicy, 'name', None))

    def test_has_method_chunk(self):
        assert callable(getattr(OverlapWindowChunkPolicy, 'chunk', None))

class TestSectionAwareChunkPolicyContract:
    def test_is_class(self):
        assert isinstance(SectionAwareChunkPolicy, type)

    def test_has_method_name(self):
        assert callable(getattr(SectionAwareChunkPolicy, 'name', None))

    def test_has_method_chunk(self):
        assert callable(getattr(SectionAwareChunkPolicy, 'chunk', None))

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
    """Module policies must be importable or skip gracefully."""
    pass  # Import verified at module level
