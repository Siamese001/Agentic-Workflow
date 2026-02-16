"""
Governance test: Heal model routing enabled-path contract.

Proves:
1. Default-off: Without env var, router seam NOT invoked, no "routed_model=" log
2. Enabled + LOW: With env var, router invoked with LOW tier, logs "routed_model=local_low"
3. Enabled + HIGH: With env var, router invoked with HIGH tier, logs "routed_model=local_high"

Phase 6 Wave 6.3 acceptance test.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from unittest.mock import patch

import pytest

import agentic_core.utils.decorators_util as decorators_module
from agentic_core.L5_safety.types.heal_model_map import map_tier_to_model_id
from agentic_core.L5_safety.types.heal_policy_types import (
    HealEscalationDecision,
    ReasoningTier,
)
from agentic_core.utils.decorators import standard_heal

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


class TestModelRoutingDefaultOff:
    """Prove default-off behavior when env var is not set."""

    def test_router_seam_not_invoked_when_disabled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Without env var, router seam is NOT invoked."""
        monkeypatch.delenv("HEAL_POLICY_MODEL_ESCALATION", raising=False)

        mock_decision = HealEscalationDecision(
            tier=ReasoningTier.LOW,
            threshold_used="TEST",
            rationale="Test rationale",
        )

        router_calls: list[ReasoningTier] = []

        def spy_router(tier: ReasoningTier) -> str:
            router_calls.append(tier)
            return map_tier_to_model_id(tier)

        with (
            patch(
                "agentic_core.utils.decorators_util.decide_reasoning_tier",
                return_value=mock_decision,
            ),
            patch.object(decorators_module, "_HEAL_MODEL_ROUTER", spy_router),
        ):
            healer = DummyHealer()
            healer.heal_repository(dry_run=True)

        assert len(router_calls) == 0, (
            f"Expected router seam not invoked without env var, got: {router_calls}"
        )

    def test_no_routed_model_log_when_disabled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Without env var, no 'routed_model=' log appears."""
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

        routed_model_logs = [m for m in captured_messages if "routed_model=" in m]
        assert len(routed_model_logs) == 0, (
            f"Expected no routed_model log without env var, got: {routed_model_logs}"
        )


class TestModelRoutingEnabledLow:
    """Prove enabled behavior with LOW tier."""

    def test_router_invoked_with_low_tier(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """With env var set, router invoked exactly once with LOW tier."""
        monkeypatch.setenv("HEAL_POLICY_MODEL_ESCALATION", "1")

        mock_decision = HealEscalationDecision(
            tier=ReasoningTier.LOW,
            threshold_used="TEST",
            rationale="Test rationale",
        )

        router_calls: list[ReasoningTier] = []

        def spy_router(tier: ReasoningTier) -> str:
            router_calls.append(tier)
            return map_tier_to_model_id(tier)

        with (
            patch(
                "agentic_core.utils.decorators_util.decide_reasoning_tier",
                return_value=mock_decision,
            ),
            patch.object(decorators_module, "_HEAL_MODEL_ROUTER", spy_router),
        ):
            healer = DummyHealer()
            healer.heal_repository(dry_run=True)

        assert len(router_calls) == 1, f"Expected router invoked once, got: {router_calls}"
        assert router_calls[0] == ReasoningTier.LOW

    def test_routed_model_log_contains_local_low(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """With env var set and LOW tier, log contains 'routed_model=local_low'."""
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
            patch.object(decorators_module, "_HEAL_MODEL_ROUTER", map_tier_to_model_id),
            patch(
                "agentic_core.utils.decorators_util.Logger.debug",
                side_effect=capture_debug,
            ),
        ):
            healer = DummyHealer()
            healer.heal_repository(dry_run=True)

        routed_model_logs = [m for m in captured_messages if "routed_model=" in m]
        assert len(routed_model_logs) == 1, f"Expected exactly one routed_model log, got: {routed_model_logs}"
        assert "routed_model=local_low" in routed_model_logs[0]


class TestModelRoutingEnabledHigh:
    """Prove enabled behavior with HIGH tier."""

    def test_router_invoked_with_high_tier(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """With env var set, router invoked exactly once with HIGH tier."""
        monkeypatch.setenv("HEAL_POLICY_MODEL_ESCALATION", "1")

        mock_decision = HealEscalationDecision(
            tier=ReasoningTier.HIGH,
            threshold_used="TEST",
            rationale="Test rationale",
        )

        router_calls: list[ReasoningTier] = []

        def spy_router(tier: ReasoningTier) -> str:
            router_calls.append(tier)
            return map_tier_to_model_id(tier)

        with (
            patch(
                "agentic_core.utils.decorators_util.decide_reasoning_tier",
                return_value=mock_decision,
            ),
            patch.object(decorators_module, "_HEAL_MODEL_ROUTER", spy_router),
        ):
            healer = DummyHealer()
            healer.heal_repository(dry_run=True)

        assert len(router_calls) == 1, f"Expected router invoked once, got: {router_calls}"
        assert router_calls[0] == ReasoningTier.HIGH

    def test_routed_model_log_contains_local_high(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """With env var set and HIGH tier, log contains 'routed_model=local_high'."""
        monkeypatch.setenv("HEAL_POLICY_MODEL_ESCALATION", "1")

        mock_decision = HealEscalationDecision(
            tier=ReasoningTier.HIGH,
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
            patch.object(decorators_module, "_HEAL_MODEL_ROUTER", map_tier_to_model_id),
            patch(
                "agentic_core.utils.decorators_util.Logger.debug",
                side_effect=capture_debug,
            ),
        ):
            healer = DummyHealer()
            healer.heal_repository(dry_run=True)

        routed_model_logs = [m for m in captured_messages if "routed_model=" in m]
        assert len(routed_model_logs) == 1, f"Expected exactly one routed_model log, got: {routed_model_logs}"
        assert "routed_model=local_high" in routed_model_logs[0]
