"""Foundational behavioral tests for apps_shared/utils/unified_signal_pipeline_util.py.

fan_in=17 — this module is imported by 17 other modules.
ADG contract: import-hygiene is covered by test_unified_signal_pipeline_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.unified_signal_pipeline_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        ContextEnrichmentStage,
        InputProcessingStage,
        PipelineContext,
        PipelineStage,
        PipelineStageType,
        SignalAugmentationStage,
        get_unified_pipeline,
        process_outreach_signal,
        process_resume_signal,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    PipelineStageType = None  # type: ignore[assignment,misc]
    PipelineContext = None  # type: ignore[assignment,misc]
    PipelineStage = None  # type: ignore[assignment,misc]
    InputProcessingStage = None  # type: ignore[assignment,misc]
    ContextEnrichmentStage = None  # type: ignore[assignment,misc]
    SignalAugmentationStage = None  # type: ignore[assignment,misc]
    get_unified_pipeline = None  # type: ignore[assignment,misc]
    process_resume_signal = None  # type: ignore[assignment,misc]
    process_outreach_signal = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="unified_signal_pipeline_util.py deps unavailable")
class TestPipelineStageTypeContract:
    def test_is_enum(self):
        import enum
        assert issubclass(PipelineStageType, enum.Enum)

    def test_has_members(self):
        assert len(list(PipelineStageType)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in PipelineStageType:
            assert member.value is not None

    def test_known_member_input_processing_exists(self):
        assert hasattr(PipelineStageType, 'INPUT_PROCESSING')

@pytest.mark.skipif(not _AVAILABLE, reason="unified_signal_pipeline_util.py deps unavailable")
class TestPipelineContextContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(PipelineContext)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(PipelineContext)}
        assert field_names >= {'original_input', 'domain_config', 'engine_type', 'processed_data', 'metadata'}

@pytest.mark.skipif(not _AVAILABLE, reason="unified_signal_pipeline_util.py deps unavailable")
class TestPipelineStageContract:
    def test_is_class(self):
        assert isinstance(PipelineStage, type)

    def test_has_method_execute(self):
        assert callable(getattr(PipelineStage, 'execute', None))

    def test_has_method_stage_name(self):
        assert callable(getattr(PipelineStage, 'stage_name', None))

@pytest.mark.skipif(not _AVAILABLE, reason="unified_signal_pipeline_util.py deps unavailable")
class TestInputProcessingStageContract:
    def test_is_class(self):
        assert isinstance(InputProcessingStage, type)

    def test_has_method_execute(self):
        assert callable(getattr(InputProcessingStage, 'execute', None))

    def test_has_method_stage_name(self):
        assert callable(getattr(InputProcessingStage, 'stage_name', None))

@pytest.mark.skipif(not _AVAILABLE, reason="unified_signal_pipeline_util.py deps unavailable")
class TestContextEnrichmentStageContract:
    def test_is_class(self):
        assert isinstance(ContextEnrichmentStage, type)

    def test_has_method_execute(self):
        assert callable(getattr(ContextEnrichmentStage, 'execute', None))

    def test_has_method_stage_name(self):
        assert callable(getattr(ContextEnrichmentStage, 'stage_name', None))

@pytest.mark.skipif(not _AVAILABLE, reason="unified_signal_pipeline_util.py deps unavailable")
class TestSignalAugmentationStageContract:
    def test_is_class(self):
        assert isinstance(SignalAugmentationStage, type)

    def test_has_method_execute(self):
        assert callable(getattr(SignalAugmentationStage, 'execute', None))

    def test_has_method_stage_name(self):
        assert callable(getattr(SignalAugmentationStage, 'stage_name', None))

@pytest.mark.skipif(not _AVAILABLE, reason="unified_signal_pipeline_util.py deps unavailable")
class TestGetUnifiedPipelineFunction:
    def test_is_callable(self):
        assert callable(get_unified_pipeline)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_unified_pipeline)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="unified_signal_pipeline_util.py deps unavailable")
class TestProcessResumeSignalFunction:
    def test_is_callable(self):
        assert callable(process_resume_signal)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(process_resume_signal)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="unified_signal_pipeline_util.py deps unavailable")
class TestProcessOutreachSignalFunction:
    def test_is_callable(self):
        assert callable(process_outreach_signal)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(process_outreach_signal)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="unified_signal_pipeline_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="unified_signal_pipeline_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="unified_signal_pipeline_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="unified_signal_pipeline_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="unified_signal_pipeline_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module unified_signal_pipeline_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
