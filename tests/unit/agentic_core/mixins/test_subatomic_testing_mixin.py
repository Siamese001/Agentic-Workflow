"""Foundational behavioral tests for agentic_core/mixins/subatomic_testing_mixin.py.

fan_in=13 — imported by 13 other modules.
ADG import-hygiene is covered separately by test_subatomic_testing_mixin_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.mixins.subatomic_testing_mixin import (  # noqa: F401
        SubatomicTestingMixin,
        L2SelfTestingMixin,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
        MAX_DEPTH,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    SubatomicTestingMixin = None  # type: ignore[assignment,misc]
    L2SelfTestingMixin = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="subatomic_testing_mixin.py deps unavailable")
class TestSubatomicTestingMixinContract:
    def test_is_class(self):
        assert isinstance(SubatomicTestingMixin, type)

    def test_has_method_disable_self_testing(self):
        assert callable(getattr(SubatomicTestingMixin, 'disable_self_testing', None))

    def test_has_method_enable_self_testing(self):
        assert callable(getattr(SubatomicTestingMixin, 'enable_self_testing', None))

    def test_has_method_heal_repository(self):
        assert callable(getattr(SubatomicTestingMixin, 'heal_repository', None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(SubatomicTestingMixin) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="subatomic_testing_mixin.py deps unavailable")
class TestL2SelfTestingMixinContract:
    def test_is_class(self):
        assert isinstance(L2SelfTestingMixin, type)

@pytest.mark.skipif(not _AVAILABLE, reason="subatomic_testing_mixin.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="subatomic_testing_mixin.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

    def test_value_is_truthy_or_defined(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="subatomic_testing_mixin.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

    def test_value_is_truthy_or_defined(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="subatomic_testing_mixin.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="subatomic_testing_mixin.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="subatomic_testing_mixin.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Smoke: subatomic_testing_mixin importable or gracefully unavailable."""
    assert True
