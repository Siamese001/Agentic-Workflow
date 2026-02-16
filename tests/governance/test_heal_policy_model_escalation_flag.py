"""
Governance test: Heal policy model escalation flag contract.

Proves:
A) Default-off: Without env var, no "escalation_enabled=1" log appears and observer not invoked.
B) Enabled: With env var set to "1", log contains escalation message and observer is called.

Phase 4 acceptance test.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from unittest.mock import patch

import pytest

import agentic_core.utils.decorators_util as decorators_module
from agentic_core.L5_safety.types.heal_policy_types import (
    HealEscalationDecision,
    ReasoningTier,
)
from agentic_core.utils.decorators_compat_util import standard_heal

pytestmark = pytest.mark.governance


@dataclass
class DummyHealer:
    """Minimal healer class for testing standard_heal decorator."""

    name: str = "DummyHealer"

    @standard_heal
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        _call_path: set[str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Minimal heal_repository that returns a simple dict."""
        return {
            "violations_found": 2,
            "violations_fixed": 1,
            "status": "PASS",
        }


class TestEscalationFlagDefaultOff:
    """Prove default-off behavior when env var is not set."""

    def test_no_escalation_log_when_disabled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Without env var, no 'escalation_enabled=1' log appears."""
        monkeypatch.delenv("HEAL_POLICY_MODEL_ESCALATION", raising=False)

        mock_decision = HealEscalationDecision(
            tier=ReasoningTier.LOW,
            threshold_used="TEST",
            rationale="Test rationale",
        )

        captured_messages: list[str] = []

        def capture_debug(msg: str, *args: Any, **kwargs: Any) -> None:
            captured_messages.append(msg)

        with (
            patch(
                "agentic_core.utils.decorators_util.decide_reasoning_tier",
                return_value=mock_decision,
            ),
            patch(
                "agentic_core.utils.decorators_util.Logger.debug",
                side_effect=capture_debug,
            ),
        ):
            healer = DummyHealer()
            healer.heal_repository(dry_run=True)

        escalation_logs = [m for m in captured_messages if "escalation_enabled=1" in m]
        assert len(escalation_logs) == 0, f"Expected no escalation log, got: {escalation_logs}"

    def test_observer_not_invoked_when_disabled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Without env var, observer is not invoked."""
        monkeypatch.delenv("HEAL_POLICY_MODEL_ESCALATION", raising=False)

        mock_decision = HealEscalationDecision(
            tier=ReasoningTier.LOW,
            threshold_used="TEST",
            rationale="Test rationale",
        )

        observer_calls: list[ReasoningTier] = []

        def spy_observer(tier: ReasoningTier) -> None:
            observer_calls.append(tier)

        with (
            patch(
                "agentic_core.utils.decorators_util.decide_reasoning_tier",
                return_value=mock_decision,
            ),
            patch.object(decorators_module, "_HEAL_TIER_OBSERVER", spy_observer),
        ):
            healer = DummyHealer()
            healer.heal_repository(dry_run=True)

        assert len(observer_calls) == 0, f"Expected observer not called, got: {observer_calls}"


class TestEscalationFlagEnabled:
    """Prove enabled behavior when env var is set to '1'."""

    def test_escalation_log_when_enabled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """With env var set to '1', log contains escalation message."""
        monkeypatch.setenv("HEAL_POLICY_MODEL_ESCALATION", "1")

        mock_decision = HealEscalationDecision(
            tier=ReasoningTier.LOW,
            threshold_used="TEST",
            rationale="Test rationale",
        )

        captured_messages: list[str] = []

        def capture_debug(msg: str, *args: Any, **kwargs: Any) -> None:
            captured_messages.append(msg)

        with (
            patch(
                "agentic_core.utils.decorators_util.decide_reasoning_tier",
                return_value=mock_decision,
            ),
            patch(
                "agentic_core.utils.decorators_util.Logger.debug",
                side_effect=capture_debug,
            ),
        ):
            healer = DummyHealer()
            healer.heal_repository(dry_run=True)

        escalation_logs = [m for m in captured_messages if "escalation_enabled=1" in m]
        assert len(escalation_logs) == 1, f"Expected exactly one escalation log, got: {escalation_logs}"
        assert "selected_tier=LOW" in escalation_logs[0]

    def test_observer_invoked_when_enabled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """With env var set to '1', observer is called exactly once with correct tier."""
        monkeypatch.setenv("HEAL_POLICY_MODEL_ESCALATION", "1")

        mock_decision = HealEscalationDecision(
            tier=ReasoningTier.LOW,
            threshold_used="TEST",
            rationale="Test rationale",
        )

        observer_calls: list[ReasoningTier] = []

        def spy_observer(tier: ReasoningTier) -> None:
            observer_calls.append(tier)

        with (
            patch(
                "agentic_core.utils.decorators_util.decide_reasoning_tier",
                return_value=mock_decision,
            ),
            patch.object(decorators_module, "_HEAL_TIER_OBSERVER", spy_observer),
        ):
            healer = DummyHealer()
            healer.heal_repository(dry_run=True)

        assert len(observer_calls) == 1, f"Expected observer called once, got: {observer_calls}"
        assert observer_calls[0] == ReasoningTier.LOW
