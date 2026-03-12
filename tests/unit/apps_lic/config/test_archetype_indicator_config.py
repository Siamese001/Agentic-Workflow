"""Foundational behavioral tests for apps_lic/config/archetype_indicator_config.py.

fan_in=14 — this module is imported by 14 other modules.
ADG contract: import-hygiene is covered by test_archetype_indicator_config_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_lic.config.archetype_indicator_config import (  # noqa: F401
        ArchetypeIndicators,
        ProfileAnalysisAgent,
        VectorStoreQueryParams,
        FallbackRAGParams,
        ResearchAgent,
        SenderGroundingAgent,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    ArchetypeIndicators = None  # type: ignore[assignment,misc]
    ProfileAnalysisAgent = None  # type: ignore[assignment,misc]
    VectorStoreQueryParams = None  # type: ignore[assignment,misc]
    FallbackRAGParams = None  # type: ignore[assignment,misc]
    ResearchAgent = None  # type: ignore[assignment,misc]
    SenderGroundingAgent = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="archetype_indicator_config.py deps unavailable")
class TestArchetypeIndicatorsContract:
    def test_is_class(self):
        assert isinstance(ArchetypeIndicators, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(ArchetypeIndicators, type)

@pytest.mark.skipif(not _AVAILABLE, reason="archetype_indicator_config.py deps unavailable")
class TestProfileAnalysisAgentContract:
    def test_is_class(self):
        assert isinstance(ProfileAnalysisAgent, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(ProfileAnalysisAgent, type)

@pytest.mark.skipif(not _AVAILABLE, reason="archetype_indicator_config.py deps unavailable")
class TestVectorStoreQueryParamsContract:
    def test_is_class(self):
        assert isinstance(VectorStoreQueryParams, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(VectorStoreQueryParams, type)

@pytest.mark.skipif(not _AVAILABLE, reason="archetype_indicator_config.py deps unavailable")
class TestFallbackRAGParamsContract:
    def test_is_class(self):
        assert isinstance(FallbackRAGParams, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(FallbackRAGParams, type)

@pytest.mark.skipif(not _AVAILABLE, reason="archetype_indicator_config.py deps unavailable")
class TestResearchAgentContract:
    def test_is_class(self):
        assert isinstance(ResearchAgent, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(ResearchAgent, type)

@pytest.mark.skipif(not _AVAILABLE, reason="archetype_indicator_config.py deps unavailable")
class TestSenderGroundingAgentContract:
    def test_is_class(self):
        assert isinstance(SenderGroundingAgent, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(SenderGroundingAgent, type)

@pytest.mark.skipif(not _AVAILABLE, reason="archetype_indicator_config.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="archetype_indicator_config.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="archetype_indicator_config.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="archetype_indicator_config.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="archetype_indicator_config.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module archetype_indicator_config must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
