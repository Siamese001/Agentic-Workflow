"""
Governance test: Heal policy runtime integration contract.

Proves that decide_reasoning_tier() is invoked inside standard_heal wrapper
and the decision is logged, without changing execution behavior.

Phase 3 acceptance test.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from unittest.mock import patch

import pytest

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


class TestHealPolicyRuntimeIntegration:
    """Prove policy decision is computed and logged without behavior change."""

    def test_decide_reasoning_tier_is_invoked(self) -> None:
        """Assert decide_reasoning_tier() is called exactly once per wrapper invocation."""
        mock_decision = HealEscalationDecision(
            tier=ReasoningTier.LOW,
            threshold_used="TEST",
            rationale="Test rationale",
        )

        with patch(
            "agentic_core.utils.decorators_util.decide_reasoning_tier",
            return_value=mock_decision,
        ) as mock_decide:
            healer = DummyHealer()
            healer.heal_repository(dry_run=True)

            mock_decide.assert_called_once()

    def test_policy_decision_is_logged(self) -> None:
        """Assert Logger.debug receives the policy decision log line."""
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

        policy_logs = [m for m in captured_messages if "[heal_policy]" in m]
        assert len(policy_logs) == 1, f"Expected exactly one policy log, got: {policy_logs}"
        assert "tier=LOW" in policy_logs[0]
        assert "threshold=TEST" in policy_logs[0]

    def test_output_unchanged_by_policy_integration(self) -> None:
        """Assert returned normalized dict matches baseline behavior."""
        mock_decision = HealEscalationDecision(
            tier=ReasoningTier.LOW,
            threshold_used="TEST",
            rationale="Test rationale",
        )

        with patch(
            "agentic_core.utils.decorators_util.decide_reasoning_tier",
            return_value=mock_decision,
        ):
            healer = DummyHealer()
            result = healer.heal_repository(dry_run=True)

        assert isinstance(result, dict)
        assert "status" in result
        assert "violations_found" in result
        assert "violations_fixed" in result
        assert result["violations_found"] == 2
        assert result["violations_fixed"] == 1
        assert result["status"] == "PASS"
