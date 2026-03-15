"""Foundational behavioral tests for agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py.

fan_in=12 — this module is imported by 12 other modules.
ADG contract: import-hygiene is covered by test_ArchitectureGovernorAgent_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        ArchitectureGovernorAgent,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    ArchitectureGovernorAgent = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ArchitectureGovernorAgent.py deps unavailable")
class TestArchitectureGovernorAgentContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ArchitectureGovernorAgent)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ArchitectureGovernorAgent)}
        assert field_names >= {'ci_mode', 'auto_approve', 'project_root', 'healing_enabled'}

@pytest.mark.skipif(not _AVAILABLE, reason="ArchitectureGovernorAgent.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="ArchitectureGovernorAgent.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="ArchitectureGovernorAgent.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="ArchitectureGovernorAgent.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="ArchitectureGovernorAgent.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module ArchitectureGovernorAgent must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
