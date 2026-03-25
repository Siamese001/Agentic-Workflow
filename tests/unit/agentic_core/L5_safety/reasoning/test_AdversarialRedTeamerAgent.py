"""Foundational behavioral tests for agentic_core/L5_safety/reasoning/AdversarialRedTeamerAgent.py.

fan_in=10 — this module is imported by 10 other modules.
ADG contract: import-hygiene is covered by test_AdversarialRedTeamerAgent_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.reasoning.AdversarialRedTeamerAgent import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    AdversarialRedTeamerAgent,
    RedTeamResult,
    VulnerabilityTest,
    get_adversarial_red_teamer,
)


class TestVulnerabilityTestContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(VulnerabilityTest)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(VulnerabilityTest)}
        assert field_names >= {'target_file', 'test_type', 'attack_vector', 'test_id', 'expected_behavior'}

class TestRedTeamResultContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(RedTeamResult)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(RedTeamResult)}
        assert field_names >= {'Severity', 'details', 'vulnerability_found', 'test_id', 'passed'}

class TestAdversarialRedTeamerAgentContract:
    def test_is_class(self):
        assert isinstance(AdversarialRedTeamerAgent, type)

    def test_has_method_execute(self):
        assert callable(getattr(AdversarialRedTeamerAgent, 'execute', None))

    def test_has_method_heal_repository(self):
        assert callable(getattr(AdversarialRedTeamerAgent, 'heal_repository', None))

    def test_has_method_heal(self):
        assert callable(getattr(AdversarialRedTeamerAgent, 'heal', None))

class TestGetAdversarialRedTeamerFunction:
    def test_is_callable(self):
        assert callable(get_adversarial_red_teamer)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_adversarial_red_teamer)
        assert sig.return_annotation is not inspect.Parameter.empty

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
    """Module AdversarialRedTeamerAgent must be importable or skip gracefully."""
    pass  # Import verified at module level
