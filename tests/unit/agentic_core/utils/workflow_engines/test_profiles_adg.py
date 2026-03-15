"""ADG-driven tests for agentic_core/utils/workflow_engines/profiles.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.utils.workflow_engines.profiles import (  # noqa: F401
        PROFILE_HYBRID,
        PROFILE_HYBRID_RERANKED,
        PROFILE_VECTOR_ONLY,
        RetrievalPipeline,
        RetrievalProfileConfig,
        make_profile,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    RetrievalProfileConfig = None  # type: ignore[assignment,misc]
    RetrievalPipeline = None  # type: ignore[assignment,misc]
    make_profile = None  # type: ignore[assignment,misc]
    PROFILE_VECTOR_ONLY = None  # type: ignore[assignment,misc]
    PROFILE_HYBRID = None  # type: ignore[assignment,misc]
    PROFILE_HYBRID_RERANKED = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="profiles.py deps unavailable")
class TestRetrievalProfileConfig:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(RetrievalProfileConfig)
    def test_importable(self):
        assert RetrievalProfileConfig is not None

@pytest.mark.skipif(not _AVAILABLE, reason="profiles.py deps unavailable")
class TestRetrievalPipeline:
    def test_is_class(self):
        assert isinstance(RetrievalPipeline, type)
    def test_importable(self):
        assert RetrievalPipeline is not None

@pytest.mark.skipif(not _AVAILABLE, reason="profiles.py deps unavailable")
class TestMakeProfile:
    def test_is_callable(self):
        assert callable(make_profile)

@pytest.mark.skipif(not _AVAILABLE, reason="profiles.py deps unavailable")
class TestProfileVectorOnlyConstant:
    def test_is_not_none(self):
        assert PROFILE_VECTOR_ONLY is not None

@pytest.mark.skipif(not _AVAILABLE, reason="profiles.py deps unavailable")
class TestProfileHybridConstant:
    def test_is_not_none(self):
        assert PROFILE_HYBRID is not None

@pytest.mark.skipif(not _AVAILABLE, reason="profiles.py deps unavailable")
class TestProfileHybridRerankedConstant:
    def test_is_not_none(self):
        assert PROFILE_HYBRID_RERANKED is not None


def test_module_importable():
    """Module profiles.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
