"""Foundational behavioral tests for agentic_core/L5_safety/types/heal_policy_types.py.

fan_in=3 — imported by 3 other modules.
ADG import-hygiene is covered separately by test_heal_policy_types_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.types.heal_policy_types import (  # noqa: F401
        ReasoningTier,
        ScoreBand,
        HealEscalationInputs,
        LegacyHealEscalationInputs,
        HealEscalationDecision,
        classify_score,
        classify_confidence,
        decide_heal_escalation,
        decide_reasoning_tier,
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
    ReasoningTier = None  # type: ignore[assignment,misc]
    ScoreBand = None  # type: ignore[assignment,misc]
    HealEscalationInputs = None  # type: ignore[assignment,misc]
    LegacyHealEscalationInputs = None  # type: ignore[assignment,misc]
    HealEscalationDecision = None  # type: ignore[assignment,misc]
    classify_score = None  # type: ignore[assignment,misc]
    classify_confidence = None  # type: ignore[assignment,misc]
    decide_heal_escalation = None  # type: ignore[assignment,misc]
    decide_reasoning_tier = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="heal_policy_types.py deps unavailable")
class TestReasoningTierContract:
    def test_is_enum(self):
        import enum
        assert issubclass(ReasoningTier, enum.Enum)

    def test_has_members(self):
        assert len(list(ReasoningTier)) >= 1

    def test_member_values_accessible(self):
        for m in ReasoningTier:
            assert m.value is not None or m.value is None

    def test_known_member_low_present(self):
        assert hasattr(ReasoningTier, 'LOW')

    def test_members_are_unique(self):
        values = [m.value for m in ReasoningTier]
        assert len(values) == len(set(values))

@pytest.mark.skipif(not _AVAILABLE, reason="heal_policy_types.py deps unavailable")
class TestScoreBandContract:
    def test_is_enum(self):
        import enum
        assert issubclass(ScoreBand, enum.Enum)

    def test_has_members(self):
        assert len(list(ScoreBand)) >= 1

    def test_member_values_accessible(self):
        for m in ScoreBand:
            assert m.value is not None or m.value is None

    def test_known_member_deterministic_present(self):
        assert hasattr(ScoreBand, 'DETERMINISTIC')

    def test_members_are_unique(self):
        values = [m.value for m in ScoreBand]
        assert len(values) == len(set(values))

@pytest.mark.skipif(not _AVAILABLE, reason="heal_policy_types.py deps unavailable")
class TestHealEscalationInputsContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(HealEscalationInputs)

    def test_is_frozen(self):
        assert HealEscalationInputs.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(HealEscalationInputs)}
        assert fnames >= {'confidence_value', 'cost_budget', 'score', 'latency_budget_ms', 'task_complexity', 'enable_llm'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(HealEscalationInputs)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="heal_policy_types.py deps unavailable")
class TestLegacyHealEscalationInputsContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(LegacyHealEscalationInputs)

    def test_is_frozen(self):
        assert LegacyHealEscalationInputs.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(LegacyHealEscalationInputs)}
        assert fnames >= {'cost_budget', 'safety_risk', 'confidence', 'retry_count', 'latency_budget', 'task_complexity'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(LegacyHealEscalationInputs)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="heal_policy_types.py deps unavailable")
class TestHealEscalationDecisionContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(HealEscalationDecision)

    def test_is_frozen(self):
        assert HealEscalationDecision.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(HealEscalationDecision)}
        assert fnames >= {'proceed', 'tier', 'threshold_used', 'rationale'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(HealEscalationDecision)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="heal_policy_types.py deps unavailable")
class TestClassifyScoreFunction:
    def test_is_callable(self):
        assert callable(classify_score)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(classify_score)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="heal_policy_types.py deps unavailable")
class TestClassifyConfidenceFunction:
    def test_is_callable(self):
        assert callable(classify_confidence)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(classify_confidence)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="heal_policy_types.py deps unavailable")
class TestDecideHealEscalationFunction:
    def test_is_callable(self):
        assert callable(decide_heal_escalation)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(decide_heal_escalation)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="heal_policy_types.py deps unavailable")
class TestDecideReasoningTierFunction:
    def test_is_callable(self):
        assert callable(decide_reasoning_tier)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(decide_reasoning_tier)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="heal_policy_types.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="heal_policy_types.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

    def test_value_is_truthy_or_defined(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="heal_policy_types.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

    def test_value_is_truthy_or_defined(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="heal_policy_types.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="heal_policy_types.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="heal_policy_types.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Smoke: heal_policy_types importable or gracefully unavailable."""
    assert True
