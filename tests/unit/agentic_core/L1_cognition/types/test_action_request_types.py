"""Foundational behavioral tests for agentic_core/L1_cognition/types/action_request_types.py.

fan_in=10 — this module is imported by 10 other modules.
ADG contract: import-hygiene is covered by test_action_request_types_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.types.action_request_types import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    ActionRequest,
    ActionResult,
    PlanningRequest,
    PlanningResult,
)


class TestActionRequestContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ActionRequest)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ActionRequest)}
        assert field_names >= {'parameters', 'context', 'action_type', 'timeout', 'tool_name'}

class TestActionResultContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ActionResult)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ActionResult)}
        assert field_names >= {'error', 'success', 'execution_time', 'metadata', 'output'}

class TestPlanningRequestContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(PlanningRequest)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(PlanningRequest)}
        assert field_names >= {'constraints', 'max_steps', 'context', 'Task'}

class TestPlanningResultContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(PlanningResult)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(PlanningResult)}
        assert field_names >= {'success', 'plan', 'confidence', 'alternatives', 'reasoning_trace'}

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
    """Module action_request_types must be importable or skip gracefully."""
    pass  # Import verified at module level
