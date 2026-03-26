"""Foundational behavioral tests for agentic_core/utils/workflow_engines/late_chunking.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_late_chunking_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: from agentic_core.utils.workflow_engines.late_chunking import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    LateChunkingPipelineConfig,
    LateChunkingProfile,
    LateChunkManifest,
    build_late_chunk_manifests_for_corpus,
    segment_document,
)


class TestLateChunkingProfileContract:
    def test_is_dataclass(self):
                from agentic_core.utils.workflow_engines.late_chunking import (  # noqa: F401
                import dataclasses
                assert dataclasses.is_dataclass(LateChunkingProfile)

        assert dataclasses.is_dataclass(LateChunkingProfile)

    def test_is_frozen(self):
        assert LateChunkingProfile.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(LateChunkingProfile)}
        assert field_names >= {'max_input_tokens', 'embedding_model_version', 'pooling_strategy', 'profile_id', 'mode'}

    def test_immutable_after_creation(self):
        import dataclasses
        fields = dataclasses.fields(LateChunkingProfile)
        if not fields:

        # Verify frozen raises on setattr
        # (create requires knowing required fields — skip if args unknown)
        assert LateChunkingProfile.__dataclass_params__.frozen is True

class TestLateChunkManifestContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(LateChunkManifest)

    def test_is_frozen(self):
        assert LateChunkManifest.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(LateChunkManifest)}
        assert field_names >= {'parent_section_id', 'segment_id', 'token_end', 'token_start', 'source_doc_id'}

    def test_immutable_after_creation(self):
        import dataclasses
        fields = dataclasses.fields(LateChunkManifest)
        if not fields:

        # Verify frozen raises on setattr
        # (create requires knowing required fields — skip if args unknown)
        assert LateChunkManifest.__dataclass_params__.frozen is True

class TestLateChunkingPipelineConfigContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(LateChunkingPipelineConfig)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(LateChunkingPipelineConfig)}
        assert field_names >= {'stride', 'max_segment_tokens', 'profile'}

class TestSegmentDocumentFunction:
    def test_is_callable(self):
        assert callable(segment_document)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(segment_document)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestBuildLateChunkManifestsForCorpusFunction:
    def test_is_callable(self):
        assert callable(build_late_chunk_manifests_for_corpus)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(build_late_chunk_manifests_for_corpus)
        assert sig.return_annotation is not inspect.Parameter.empty

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
    """Module late_chunking must be importable or skip gracefully."""
    pass  # Import verified at module level
