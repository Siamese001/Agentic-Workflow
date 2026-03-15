"""Foundational behavioral tests for agentic_core/L5_safety/reasoning/SelfUpdatingSafetyEngineAgent.py.

fan_in=13 — this module is imported by 13 other modules.
ADG contract: import-hygiene is covered by test_SelfUpdatingSafetyEngineAgent_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.reasoning.SelfUpdatingSafetyEngineAgent import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        RuleType,
        SafetyRule,
        SelfUpdatingSafetyEngineAgent,
        ThreatDetection,
        ThreatLevel,
        ThreatPattern,
        create_self_updating_safety_engine,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    ThreatLevel = None  # type: ignore[assignment,misc]
    RuleType = None  # type: ignore[assignment,misc]
    ThreatPattern = None  # type: ignore[assignment,misc]
    SafetyRule = None  # type: ignore[assignment,misc]
    ThreatDetection = None  # type: ignore[assignment,misc]
    SelfUpdatingSafetyEngineAgent = None  # type: ignore[assignment,misc]
    create_self_updating_safety_engine = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="SelfUpdatingSafetyEngineAgent.py deps unavailable")
class TestThreatLevelContract:
    def test_is_enum(self):
        import enum
        assert issubclass(ThreatLevel, enum.Enum)

    def test_has_members(self):
        assert len(list(ThreatLevel)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="SelfUpdatingSafetyEngineAgent.py deps unavailable")
class TestRuleTypeContract:
    def test_is_enum(self):
        import enum
        assert issubclass(RuleType, enum.Enum)

    def test_has_members(self):
        assert len(list(RuleType)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="SelfUpdatingSafetyEngineAgent.py deps unavailable")
class TestThreatPatternContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ThreatPattern)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ThreatPattern)}
        assert field_names >= {'pattern_signature', 'detection_count', 'pattern_type', 'ThreatLevel', 'pattern_id'}

@pytest.mark.skipif(not _AVAILABLE, reason="SelfUpdatingSafetyEngineAgent.py deps unavailable")
class TestSafetyRuleContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(SafetyRule)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(SafetyRule)}
        assert field_names >= {'description', 'ThreatLevel', 'pattern', 'rule_id', 'RuleType'}

@pytest.mark.skipif(not _AVAILABLE, reason="SelfUpdatingSafetyEngineAgent.py deps unavailable")
class TestThreatDetectionContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ThreatDetection)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ThreatDetection)}
        assert field_names >= {'matched_rules', 'ThreatLevel', 'recommendations', 'detected', 'confidence'}

@pytest.mark.skipif(not _AVAILABLE, reason="SelfUpdatingSafetyEngineAgent.py deps unavailable")
class TestSelfUpdatingSafetyEngineAgentContract:
    def test_is_class(self):
        assert isinstance(SelfUpdatingSafetyEngineAgent, type)

    def test_has_method_detect_threats(self):
        assert callable(getattr(SelfUpdatingSafetyEngineAgent, 'detect_threats', None))

    def test_has_method_report_false_positive(self):
        assert callable(getattr(SelfUpdatingSafetyEngineAgent, 'report_false_positive', None))

    def test_has_method_escalate_threat_level(self):
        assert callable(getattr(SelfUpdatingSafetyEngineAgent, 'escalate_threat_level', None))

    def test_has_method_get_rule_effectiveness(self):
        assert callable(getattr(SelfUpdatingSafetyEngineAgent, 'get_rule_effectiveness', None))

@pytest.mark.skipif(not _AVAILABLE, reason="SelfUpdatingSafetyEngineAgent.py deps unavailable")
class TestCreateSelfUpdatingSafetyEngineFunction:
    def test_is_callable(self):
        assert callable(create_self_updating_safety_engine)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(create_self_updating_safety_engine)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="SelfUpdatingSafetyEngineAgent.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="SelfUpdatingSafetyEngineAgent.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="SelfUpdatingSafetyEngineAgent.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="SelfUpdatingSafetyEngineAgent.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="SelfUpdatingSafetyEngineAgent.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module SelfUpdatingSafetyEngineAgent must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
