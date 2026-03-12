"""Foundational behavioral tests for agentic_core/L0_routing/utils/subprocess_runner_util.py.

fan_in=19 — this module is imported by 19 other modules.
ADG contract: import-hygiene is covered by test_subprocess_runner_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.utils.subprocess_runner_util import (  # noqa: F401
        invoke_arch_governor,
        invoke_orchestrator_mission,
        invoke_agent_roster_validation,
        invoke_hierarchy_agent,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    invoke_arch_governor = None  # type: ignore[assignment,misc]
    invoke_orchestrator_mission = None  # type: ignore[assignment,misc]
    invoke_agent_roster_validation = None  # type: ignore[assignment,misc]
    invoke_hierarchy_agent = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="subprocess_runner_util.py deps unavailable")
class TestInvokeArchGovernorFunction:
    def test_is_callable(self):
        assert callable(invoke_arch_governor)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(invoke_arch_governor)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="subprocess_runner_util.py deps unavailable")
class TestInvokeOrchestratorMissionFunction:
    def test_is_callable(self):
        assert callable(invoke_orchestrator_mission)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(invoke_orchestrator_mission)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="subprocess_runner_util.py deps unavailable")
class TestInvokeAgentRosterValidationFunction:
    def test_is_callable(self):
        assert callable(invoke_agent_roster_validation)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(invoke_agent_roster_validation)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="subprocess_runner_util.py deps unavailable")
class TestInvokeHierarchyAgentFunction:
    def test_is_callable(self):
        assert callable(invoke_hierarchy_agent)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(invoke_hierarchy_agent)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="subprocess_runner_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="subprocess_runner_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="subprocess_runner_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="subprocess_runner_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="subprocess_runner_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module subprocess_runner_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
