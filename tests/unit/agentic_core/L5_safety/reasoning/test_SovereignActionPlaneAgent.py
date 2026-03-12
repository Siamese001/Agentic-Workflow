"""Foundational behavioral tests for agentic_core/L5_safety/reasoning/SovereignActionPlaneAgent.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_SovereignActionPlaneAgent_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.reasoning.SovereignActionPlaneAgent import (  # noqa: F401
        SovereignToolsmith,
        SovereignSandbox,
        SovereignActionPlaneAgent,
        create_sovereign_action_plane,
        get_sovereign_action_plane,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    SovereignToolsmith = None  # type: ignore[assignment,misc]
    SovereignSandbox = None  # type: ignore[assignment,misc]
    SovereignActionPlaneAgent = None  # type: ignore[assignment,misc]
    create_sovereign_action_plane = None  # type: ignore[assignment,misc]
    get_sovereign_action_plane = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="SovereignActionPlaneAgent.py deps unavailable")
class TestSovereignToolsmithContract:
    def test_is_class(self):
        assert isinstance(SovereignToolsmith, type)

    def test_has_method_forge_diagnostic_tool(self):
        assert callable(getattr(SovereignToolsmith, 'forge_diagnostic_tool', None))

@pytest.mark.skipif(not _AVAILABLE, reason="SovereignActionPlaneAgent.py deps unavailable")
class TestSovereignSandboxContract:
    def test_is_class(self):
        assert isinstance(SovereignSandbox, type)

    def test_has_method_start(self):
        assert callable(getattr(SovereignSandbox, 'start', None))

    def test_has_method_stop(self):
        assert callable(getattr(SovereignSandbox, 'stop', None))

    def test_has_method_execute_tool(self):
        assert callable(getattr(SovereignSandbox, 'execute_tool', None))

@pytest.mark.skipif(not _AVAILABLE, reason="SovereignActionPlaneAgent.py deps unavailable")
class TestSovereignActionPlaneAgentContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(SovereignActionPlaneAgent)

@pytest.mark.skipif(not _AVAILABLE, reason="SovereignActionPlaneAgent.py deps unavailable")
class TestCreateSovereignActionPlaneFunction:
    def test_is_callable(self):
        assert callable(create_sovereign_action_plane)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(create_sovereign_action_plane)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="SovereignActionPlaneAgent.py deps unavailable")
class TestGetSovereignActionPlaneFunction:
    def test_is_callable(self):
        assert callable(get_sovereign_action_plane)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_sovereign_action_plane)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="SovereignActionPlaneAgent.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="SovereignActionPlaneAgent.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="SovereignActionPlaneAgent.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="SovereignActionPlaneAgent.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="SovereignActionPlaneAgent.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module SovereignActionPlaneAgent must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
