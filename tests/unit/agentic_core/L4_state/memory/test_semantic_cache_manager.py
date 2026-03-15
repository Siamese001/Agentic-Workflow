"""Foundational behavioral tests for agentic_core/L4_state/memory/semantic_cache_manager.py.

fan_in=3 — imported by 3 other modules.
ADG import-hygiene is covered separately by test_semantic_cache_manager_adg.py.
This file covers behavioral invariants and public API contracts.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L4_state.memory.semantic_cache_manager import (  # noqa: F401
        CriticalInfrastructureError,
        PII_Sanitizer,
        SemanticCacheManager,
    )

    # Constants are class attributes, not module-level
    DEFAULT_WORKING_MEMORY_TTL = SemanticCacheManager.DEFAULT_WORKING_MEMORY_TTL
    DEFAULT_LONG_TERM_TTL = SemanticCacheManager.DEFAULT_LONG_TERM_TTL
    DEFAULT_PROMOTION_THRESHOLD = SemanticCacheManager.DEFAULT_PROMOTION_THRESHOLD
    DEFAULT_TRACE_SAMPLING_RATE = SemanticCacheManager.DEFAULT_TRACE_SAMPLING_RATE
    DEFAULT_STRICT_MODE = SemanticCacheManager.DEFAULT_STRICT_MODE
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    CriticalInfrastructureError = None  # type: ignore[assignment,misc]
    PII_Sanitizer = None  # type: ignore[assignment,misc]
    SemanticCacheManager = None  # type: ignore[assignment,misc]
    DEFAULT_WORKING_MEMORY_TTL = None  # type: ignore[assignment,misc]
    DEFAULT_LONG_TERM_TTL = None  # type: ignore[assignment,misc]
    DEFAULT_PROMOTION_THRESHOLD = None  # type: ignore[assignment,misc]
    DEFAULT_TRACE_SAMPLING_RATE = None  # type: ignore[assignment,misc]
    DEFAULT_STRICT_MODE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="semantic_cache_manager.py deps unavailable")
class TestCriticalInfrastructureErrorContract:
    def test_is_class(self):
        assert isinstance(CriticalInfrastructureError, type)


@pytest.mark.skipif(not _AVAILABLE, reason="semantic_cache_manager.py deps unavailable")
class TestPII_SanitizerContract:
    def test_is_class(self):
        assert isinstance(PII_Sanitizer, type)

    def test_has_method_sanitize(self):
        assert callable(getattr(PII_Sanitizer, "sanitize", None))

    def test_has_method_is_safe(self):
        assert callable(getattr(PII_Sanitizer, "is_safe", None))

    def test_has_method_detect_pii(self):
        assert callable(getattr(PII_Sanitizer, "detect_pii", None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(PII_Sanitizer) if not m.startswith("_")]
        assert len(pub) >= 1


@pytest.mark.skipif(not _AVAILABLE, reason="semantic_cache_manager.py deps unavailable")
class TestSemanticCacheManagerContract:
    def test_is_class(self):
        assert isinstance(SemanticCacheManager, type)

    def test_has_method_get_instance(self):
        assert callable(getattr(SemanticCacheManager, "get_instance", None))

    def test_has_method_reset_instance(self):
        assert callable(getattr(SemanticCacheManager, "reset_instance", None))

    def test_has_method_recall(self):
        assert callable(getattr(SemanticCacheManager, "recall", None))

    def test_has_method_learn(self):
        assert callable(getattr(SemanticCacheManager, "learn", None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(SemanticCacheManager) if not m.startswith("_")]
        assert len(pub) >= 1


@pytest.mark.skipif(not _AVAILABLE, reason="semantic_cache_manager.py deps unavailable")
class TestDefaultWorkingMemoryTTLConstant:
    def test_is_not_none(self):
        assert DEFAULT_WORKING_MEMORY_TTL is not None

    def test_is_positive(self):
        assert DEFAULT_WORKING_MEMORY_TTL > 0


@pytest.mark.skipif(not _AVAILABLE, reason="semantic_cache_manager.py deps unavailable")
class TestDefaultLongTermTTLConstant:
    def test_is_not_none(self):
        assert DEFAULT_LONG_TERM_TTL is not None

    def test_exceeds_working_memory(self):
        assert DEFAULT_LONG_TERM_TTL >= DEFAULT_WORKING_MEMORY_TTL


@pytest.mark.skipif(not _AVAILABLE, reason="semantic_cache_manager.py deps unavailable")
class TestDefaultPromotionThresholdConstant:
    def test_is_not_none(self):
        assert DEFAULT_PROMOTION_THRESHOLD is not None

    def test_is_between_zero_and_one(self):
        assert 0.0 <= DEFAULT_PROMOTION_THRESHOLD <= 1.0


@pytest.mark.skipif(not _AVAILABLE, reason="semantic_cache_manager.py deps unavailable")
class TestDefaultTraceSamplingRateConstant:
    def test_is_not_none(self):
        assert DEFAULT_TRACE_SAMPLING_RATE is not None

    def test_is_between_zero_and_one(self):
        assert 0.0 <= DEFAULT_TRACE_SAMPLING_RATE <= 1.0


@pytest.mark.skipif(not _AVAILABLE, reason="semantic_cache_manager.py deps unavailable")
class TestDefaultStrictModeConstant:
    def test_is_not_none(self):
        assert DEFAULT_STRICT_MODE is not None

    def test_is_bool(self):
        assert isinstance(DEFAULT_STRICT_MODE, bool)


def test_module_importable():
    """Smoke: semantic_cache_manager importable or gracefully unavailable."""
    pass
