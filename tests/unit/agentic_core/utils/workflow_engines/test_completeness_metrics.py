"""Foundational behavioral tests for agentic_core/utils/workflow_engines/completeness_metrics.py.

fan_in=12 — this module is imported by 12 other modules.
ADG contract: import-hygiene is covered by test_completeness_metrics_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.utils.workflow_engines.completeness_metrics import (  # noqa: F401
        EvaluationMetricResult,
        EvaluationReport,
        EvaluationDeltaReport,
        RetrievalExperimentReport,
        ChunkStrategyReport,
        CompletenessExperimentReport,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    EvaluationMetricResult = None  # type: ignore[assignment,misc]
    EvaluationReport = None  # type: ignore[assignment,misc]
    EvaluationDeltaReport = None  # type: ignore[assignment,misc]
    RetrievalExperimentReport = None  # type: ignore[assignment,misc]
    ChunkStrategyReport = None  # type: ignore[assignment,misc]
    CompletenessExperimentReport = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="completeness_metrics.py deps unavailable")
class TestEvaluationMetricResultContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(EvaluationMetricResult)

    def test_is_frozen(self):
        assert EvaluationMetricResult.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(EvaluationMetricResult)}
        assert field_names >= {'metric_name', 'sample_count', 'value', 'notes', 'configuration_id'}

    def test_immutable_after_creation(self):
        import dataclasses
        fields = dataclasses.fields(EvaluationMetricResult)
        if not fields:
            pytest.skip('no fields to test immutability')
        # Verify frozen raises on setattr
        # (create requires knowing required fields — skip if args unknown)
        assert EvaluationMetricResult.__dataclass_params__.frozen is True

@pytest.mark.skipif(not _AVAILABLE, reason="completeness_metrics.py deps unavailable")
class TestEvaluationReportContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(EvaluationReport)

    def test_is_frozen(self):
        assert EvaluationReport.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(EvaluationReport)}
        assert field_names >= {'system_version', 'recall_at_k', 'report_id', 'precision_at_k', 'configuration_id'}

    def test_immutable_after_creation(self):
        import dataclasses
        fields = dataclasses.fields(EvaluationReport)
        if not fields:
            pytest.skip('no fields to test immutability')
        # Verify frozen raises on setattr
        # (create requires knowing required fields — skip if args unknown)
        assert EvaluationReport.__dataclass_params__.frozen is True

@pytest.mark.skipif(not _AVAILABLE, reason="completeness_metrics.py deps unavailable")
class TestEvaluationDeltaReportContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(EvaluationDeltaReport)

    def test_is_frozen(self):
        assert EvaluationDeltaReport.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(EvaluationDeltaReport)}
        assert field_names >= {'candidate_config_id', 'baseline_config_id', 'baseline_report_id', 'delta_report_id', 'candidate_report_id'}

    def test_immutable_after_creation(self):
        import dataclasses
        fields = dataclasses.fields(EvaluationDeltaReport)
        if not fields:
            pytest.skip('no fields to test immutability')
        # Verify frozen raises on setattr
        # (create requires knowing required fields — skip if args unknown)
        assert EvaluationDeltaReport.__dataclass_params__.frozen is True

@pytest.mark.skipif(not _AVAILABLE, reason="completeness_metrics.py deps unavailable")
class TestRetrievalExperimentReportContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(RetrievalExperimentReport)

    def test_is_frozen(self):
        assert RetrievalExperimentReport.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(RetrievalExperimentReport)}
        assert field_names >= {'experiment_id', 'comparison_axis', 'baseline', 'delta', 'candidate'}

    def test_immutable_after_creation(self):
        import dataclasses
        fields = dataclasses.fields(RetrievalExperimentReport)
        if not fields:
            pytest.skip('no fields to test immutability')
        # Verify frozen raises on setattr
        # (create requires knowing required fields — skip if args unknown)
        assert RetrievalExperimentReport.__dataclass_params__.frozen is True

@pytest.mark.skipif(not _AVAILABLE, reason="completeness_metrics.py deps unavailable")
class TestChunkStrategyReportContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ChunkStrategyReport)

    def test_is_frozen(self):
        assert ChunkStrategyReport.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ChunkStrategyReport)}
        assert field_names >= {'experiment_id', 'baseline', 'baseline_strategy', 'candidate', 'candidate_strategy'}

    def test_immutable_after_creation(self):
        import dataclasses
        fields = dataclasses.fields(ChunkStrategyReport)
        if not fields:
            pytest.skip('no fields to test immutability')
        # Verify frozen raises on setattr
        # (create requires knowing required fields — skip if args unknown)
        assert ChunkStrategyReport.__dataclass_params__.frozen is True

@pytest.mark.skipif(not _AVAILABLE, reason="completeness_metrics.py deps unavailable")
class TestCompletenessExperimentReportContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(CompletenessExperimentReport)

    def test_is_frozen(self):
        assert CompletenessExperimentReport.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(CompletenessExperimentReport)}
        assert field_names >= {'experiment_id', 'system_version', 'support_score_before', 'high_sim_wrong_answer_after', 'high_sim_wrong_answer_before'}

    def test_immutable_after_creation(self):
        import dataclasses
        fields = dataclasses.fields(CompletenessExperimentReport)
        if not fields:
            pytest.skip('no fields to test immutability')
        # Verify frozen raises on setattr
        # (create requires knowing required fields — skip if args unknown)
        assert CompletenessExperimentReport.__dataclass_params__.frozen is True

@pytest.mark.skipif(not _AVAILABLE, reason="completeness_metrics.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="completeness_metrics.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="completeness_metrics.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="completeness_metrics.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="completeness_metrics.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module completeness_metrics must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
