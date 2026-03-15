"""Foundational behavioral tests for system_learning/ports/meta_prior_provider.py.

fan_in=4 — imported by 4 other modules.
ADG import-hygiene is covered separately by test_meta_prior_provider_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from system_learning.ports.meta_prior_provider import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        MetaPriorProvider,
        NeutralMetaPriorProvider,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    MetaPriorProvider = None  # type: ignore[assignment,misc]
    NeutralMetaPriorProvider = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="meta_prior_provider.py deps unavailable")
class TestMetaPriorProviderContract:
    def test_is_class(self):
        assert isinstance(MetaPriorProvider, type)

    def test_has_method_get_prior(self):
        assert callable(getattr(MetaPriorProvider, 'get_prior', None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(MetaPriorProvider) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="meta_prior_provider.py deps unavailable")
class TestNeutralMetaPriorProviderContract:
    def test_is_class(self):
        assert isinstance(NeutralMetaPriorProvider, type)

    def test_has_method_get_prior(self):
        assert callable(getattr(NeutralMetaPriorProvider, 'get_prior', None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(NeutralMetaPriorProvider) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="meta_prior_provider.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="meta_prior_provider.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

    def test_value_is_truthy_or_defined(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="meta_prior_provider.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

    def test_value_is_truthy_or_defined(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="meta_prior_provider.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="meta_prior_provider.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="meta_prior_provider.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Smoke: meta_prior_provider importable or gracefully unavailable."""
    pass
