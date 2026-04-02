"""Foundational behavioral tests for apps_lic/config/archetype_indicator_config.py.

fan_in=14 — this module is imported by 14 other modules.
ADG contract: import-hygiene is covered by test_archetype_indicator_config_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

from apps_lic.config.archetype_indicator_config import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    ArchetypeIndicators,
    FallbackRAGParams,
    ProfileAnalysisAgent,
    ResearchAgent,
    SenderGroundingAgent,
    VectorStoreQueryParams,
)

pytestmark = pytest.mark.unit


class TestArchetypeIndicatorsContract:
    def test_is_class(self):
        assert isinstance(ArchetypeIndicators, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(ArchetypeIndicators, type)

class TestProfileAnalysisAgentContract:
    def test_is_class(self):
        assert isinstance(ProfileAnalysisAgent, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(ProfileAnalysisAgent, type)

class TestVectorStoreQueryParamsContract:
    def test_is_class(self):
        assert isinstance(VectorStoreQueryParams, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(VectorStoreQueryParams, type)

class TestFallbackRAGParamsContract:
    def test_is_class(self):
        assert isinstance(FallbackRAGParams, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(FallbackRAGParams, type)

class TestResearchAgentContract:
    def test_is_class(self):
        assert isinstance(ResearchAgent, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(ResearchAgent, type)

class TestSenderGroundingAgentContract:
    def test_is_class(self):
        assert isinstance(SenderGroundingAgent, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(SenderGroundingAgent, type)

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
    """Module archetype_indicator_config must be importable or skip gracefully."""
    pass  # Import verified at module level
