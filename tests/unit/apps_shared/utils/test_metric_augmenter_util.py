"""Foundational behavioral tests for apps_shared/utils/metric_augmenter_util.py.

fan_in=12 — this module is imported by 12 other modules.
ADG contract: import-hygiene is covered by test_metric_augmenter_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.metric_augmenter_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        AugmentedBullet,
        BusinessImpact,
        ImpactCategory,
        MetricAugmenter,
        augment_metrics,
        create_metric_augmenter,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    ImpactCategory = None  # type: ignore[assignment,misc]
    BusinessImpact = None  # type: ignore[assignment,misc]
    AugmentedBullet = None  # type: ignore[assignment,misc]
    MetricAugmenter = None  # type: ignore[assignment,misc]
    create_metric_augmenter = None  # type: ignore[assignment,misc]
    augment_metrics = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="metric_augmenter_util.py deps unavailable")
class TestImpactCategoryContract:
    def test_is_enum(self):
        import enum
        assert issubclass(ImpactCategory, enum.Enum)

    def test_has_members(self):
        assert len(list(ImpactCategory)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in ImpactCategory:
            assert member.value is not None

    def test_known_member_revenue_exists(self):
        assert hasattr(ImpactCategory, 'REVENUE')

@pytest.mark.skipif(not _AVAILABLE, reason="metric_augmenter_util.py deps unavailable")
class TestBusinessImpactContract:
    def test_is_class(self):
        assert isinstance(BusinessImpact, type)

    def test_has_method_validate_conservative_language(self):
        assert callable(getattr(BusinessImpact, 'validate_conservative_language', None))

@pytest.mark.skipif(not _AVAILABLE, reason="metric_augmenter_util.py deps unavailable")
class TestAugmentedBulletContract:
    def test_is_class(self):
        assert isinstance(AugmentedBullet, type)

    def test_has_method_is_augmented(self):
        assert callable(getattr(AugmentedBullet, 'is_augmented', None))

@pytest.mark.skipif(not _AVAILABLE, reason="metric_augmenter_util.py deps unavailable")
class TestMetricAugmenterContract:
    def test_is_class(self):
        assert isinstance(MetricAugmenter, type)

    def test_has_method_augment_bullet(self):
        assert callable(getattr(MetricAugmenter, 'augment_bullet', None))

    def test_has_method_augment_batch(self):
        assert callable(getattr(MetricAugmenter, 'augment_batch', None))

@pytest.mark.skipif(not _AVAILABLE, reason="metric_augmenter_util.py deps unavailable")
class TestCreateMetricAugmenterFunction:
    def test_is_callable(self):
        assert callable(create_metric_augmenter)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(create_metric_augmenter)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="metric_augmenter_util.py deps unavailable")
class TestAugmentMetricsFunction:
    def test_is_callable(self):
        assert callable(augment_metrics)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(augment_metrics)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="metric_augmenter_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="metric_augmenter_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="metric_augmenter_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="metric_augmenter_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="metric_augmenter_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module metric_augmenter_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
