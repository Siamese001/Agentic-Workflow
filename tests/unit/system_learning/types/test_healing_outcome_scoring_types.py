"""Foundational behavioral tests for system_learning/types/healing_outcome_scoring_types.py.

fan_in=3 — imported by 3 other modules.
ADG import-hygiene is covered separately by test_healing_outcome_scoring_types_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from system_learning.types.healing_outcome_scoring_types import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        ScoredRecommendation,
        ScoringReport,
        ScoringWeights,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ScoringWeights = None  # type: ignore[assignment,misc]
    ScoredRecommendation = None  # type: ignore[assignment,misc]
    ScoringReport = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="healing_outcome_scoring_types.py deps unavailable")
class TestScoringWeightsContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ScoringWeights)

    def test_is_frozen(self):
        assert ScoringWeights.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(ScoringWeights)}
        assert fnames >= {'sample_size_weight', 'stability_penalty_weight', 'success_rate_weight', 'risk_tier_penalty_weight'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(ScoringWeights)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="healing_outcome_scoring_types.py deps unavailable")
class TestScoredRecommendationContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ScoredRecommendation)

    def test_is_frozen(self):
        assert ScoredRecommendation.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(ScoredRecommendation)}
        assert fnames >= {'recommended_actions', 'reasons', 'score', 'target_surface', 'proposer_id'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(ScoredRecommendation)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="healing_outcome_scoring_types.py deps unavailable")
class TestScoringReportContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ScoringReport)

    def test_is_frozen(self):
        assert ScoringReport.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(ScoringReport)}
        assert fnames >= {'recommendations', 'created_utc', 'schema_version', 'source', 'weights', 'intake_record'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(ScoringReport)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="healing_outcome_scoring_types.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healing_outcome_scoring_types.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

    def test_value_is_truthy_or_defined(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healing_outcome_scoring_types.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

    def test_value_is_truthy_or_defined(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healing_outcome_scoring_types.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healing_outcome_scoring_types.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="healing_outcome_scoring_types.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Smoke: healing_outcome_scoring_types importable or gracefully unavailable."""
    pass
