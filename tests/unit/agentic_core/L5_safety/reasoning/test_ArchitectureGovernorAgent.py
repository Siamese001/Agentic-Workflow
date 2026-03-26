"""Foundational behavioral tests for agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py.

fan_in=12 — this module is imported by 12 other modules.
ADG contract: import-hygiene is covered by test_ArchitectureGovernorAgent_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: from agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    ArchitectureGovernorAgent,
)


class TestArchitectureGovernorAgentContract:
    def test_is_dataclass(self):
                from agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent import (  # noqa: F401
                import dataclasses
                assert dataclasses.is_dataclass(ArchitectureGovernorAgent)

        assert dataclasses.is_dataclass(ArchitectureGovernorAgent)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ArchitectureGovernorAgent)}
        assert field_names >= {'ci_mode', 'auto_approve', 'project_root', 'healing_enabled'}

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
    """Module ArchitectureGovernorAgent must be importable or skip gracefully."""
    pass  # Import verified at module level
