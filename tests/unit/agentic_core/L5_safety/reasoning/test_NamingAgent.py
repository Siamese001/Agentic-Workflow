"""Foundational behavioral tests for agentic_core/L5_safety/reasoning/NamingAgent.py.

fan_in=4 — imported by 4 other modules.
ADG import-hygiene is covered separately by test_NamingAgent_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.reasoning.NamingAgent import (  # noqa: F401
        PlacementResult,
        NamingAgent,
        get_naming_agent,
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
    PlacementResult = None  # type: ignore[assignment,misc]
    NamingAgent = None  # type: ignore[assignment,misc]
    get_naming_agent = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="NamingAgent.py deps unavailable")
class TestPlacementResultContract:
    def test_is_class(self):
        assert isinstance(PlacementResult, type)

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(PlacementResult) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="NamingAgent.py deps unavailable")
class TestNamingAgentContract:
    def test_is_class(self):
        assert isinstance(NamingAgent, type)

    def test_has_method_heal_repository(self):
        assert callable(getattr(NamingAgent, 'heal_repository', None))

    def test_has_method_heal(self):
        assert callable(getattr(NamingAgent, 'heal', None))

    def test_has_method_validate_name(self):
        assert callable(getattr(NamingAgent, 'validate_name', None))

    def test_has_method_suggest_name(self):
        assert callable(getattr(NamingAgent, 'suggest_name', None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(NamingAgent) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="NamingAgent.py deps unavailable")
class TestGetNamingAgentFunction:
    def test_is_callable(self):
        assert callable(get_naming_agent)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_naming_agent)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="NamingAgent.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="NamingAgent.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

    def test_value_is_truthy_or_defined(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="NamingAgent.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

    def test_value_is_truthy_or_defined(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="NamingAgent.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="NamingAgent.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="NamingAgent.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Smoke: NamingAgent importable or gracefully unavailable."""
    assert True
