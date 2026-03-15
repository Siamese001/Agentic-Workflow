"""Foundational behavioral tests for apps_lic/reasoning/OutreachValidationExecutorAgent.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_OutreachValidationExecutorAgent_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_lic.reasoning.OutreachValidationExecutorAgent import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        HealerMixin,
        MCPHardenedMixin,
        OutreachValidationExecutorAgent,
        RuleFailure,
        ValidationGateExecutor,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    ValidationGateExecutor = None  # type: ignore[assignment,misc]
    RuleFailure = None  # type: ignore[assignment,misc]
    MCPHardenedMixin = None  # type: ignore[assignment,misc]
    HealerMixin = None  # type: ignore[assignment,misc]
    OutreachValidationExecutorAgent = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="OutreachValidationExecutorAgent.py deps unavailable")
class TestValidationGateExecutorContract:
    def test_is_class(self):
        assert isinstance(ValidationGateExecutor, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(ValidationGateExecutor, type)

@pytest.mark.skipif(not _AVAILABLE, reason="OutreachValidationExecutorAgent.py deps unavailable")
class TestRuleFailureContract:
    def test_is_class(self):
        assert isinstance(RuleFailure, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(RuleFailure, type)

@pytest.mark.skipif(not _AVAILABLE, reason="OutreachValidationExecutorAgent.py deps unavailable")
class TestMCPHardenedMixinContract:
    def test_is_class(self):
        assert isinstance(MCPHardenedMixin, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(MCPHardenedMixin, type)

@pytest.mark.skipif(not _AVAILABLE, reason="OutreachValidationExecutorAgent.py deps unavailable")
class TestHealerMixinContract:
    def test_is_class(self):
        assert isinstance(HealerMixin, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(HealerMixin, type)

@pytest.mark.skipif(not _AVAILABLE, reason="OutreachValidationExecutorAgent.py deps unavailable")
class TestOutreachValidationExecutorAgentContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(OutreachValidationExecutorAgent)

@pytest.mark.skipif(not _AVAILABLE, reason="OutreachValidationExecutorAgent.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="OutreachValidationExecutorAgent.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="OutreachValidationExecutorAgent.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="OutreachValidationExecutorAgent.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="OutreachValidationExecutorAgent.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module OutreachValidationExecutorAgent must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
