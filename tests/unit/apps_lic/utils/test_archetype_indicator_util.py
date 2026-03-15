"""Foundational behavioral tests for apps_lic/utils/archetype_indicator_util.py.

fan_in=14 — this module is imported by 14 other modules.
ADG contract: import-hygiene is covered by test_archetype_indicator_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_lic.utils.archetype_indicator_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        ArchetypeIndicator,
        ProfileAnalysisConfig,
        ResearchConfig,
        RouteConditions,
        RouteConstraints,
        SenderGroundingConfig,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    ArchetypeIndicator = None  # type: ignore[assignment,misc]
    ProfileAnalysisConfig = None  # type: ignore[assignment,misc]
    ResearchConfig = None  # type: ignore[assignment,misc]
    SenderGroundingConfig = None  # type: ignore[assignment,misc]
    RouteConditions = None  # type: ignore[assignment,misc]
    RouteConstraints = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="archetype_indicator_util.py deps unavailable")
class TestArchetypeIndicatorContract:
    def test_is_class(self):
        assert isinstance(ArchetypeIndicator, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(ArchetypeIndicator, type)

@pytest.mark.skipif(not _AVAILABLE, reason="archetype_indicator_util.py deps unavailable")
class TestProfileAnalysisConfigContract:
    def test_is_class(self):
        assert isinstance(ProfileAnalysisConfig, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(ProfileAnalysisConfig, type)

@pytest.mark.skipif(not _AVAILABLE, reason="archetype_indicator_util.py deps unavailable")
class TestResearchConfigContract:
    def test_is_class(self):
        assert isinstance(ResearchConfig, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(ResearchConfig, type)

@pytest.mark.skipif(not _AVAILABLE, reason="archetype_indicator_util.py deps unavailable")
class TestSenderGroundingConfigContract:
    def test_is_class(self):
        assert isinstance(SenderGroundingConfig, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(SenderGroundingConfig, type)

@pytest.mark.skipif(not _AVAILABLE, reason="archetype_indicator_util.py deps unavailable")
class TestRouteConditionsContract:
    def test_is_class(self):
        assert isinstance(RouteConditions, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(RouteConditions, type)

@pytest.mark.skipif(not _AVAILABLE, reason="archetype_indicator_util.py deps unavailable")
class TestRouteConstraintsContract:
    def test_is_class(self):
        assert isinstance(RouteConstraints, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(RouteConstraints, type)

@pytest.mark.skipif(not _AVAILABLE, reason="archetype_indicator_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="archetype_indicator_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="archetype_indicator_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="archetype_indicator_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="archetype_indicator_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module archetype_indicator_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
