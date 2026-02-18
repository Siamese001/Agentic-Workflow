"""Wave 7.3: Governance test for heal routed model ID propagation.

Tests that when HEAL_POLICY_MODEL_ESCALATION is enabled:
- routed_model_id is propagated into heal_repository via _heal_routed_model_id kwarg
- When disabled, the kwarg is not present
- Logging confirms routed_model propagation
"""

import os
from unittest.mock import patch

import pytest

from agentic_core.utils.decorators_util import standard_heal

pytestmark = pytest.mark.governance


class DummyHealer:
    """Dummy agent with @standard_heal decorated heal_repository."""

    @standard_heal
    def heal_repository(self, **kwargs):
        """Capture kwargs for assertion."""
        self._captured_kwargs = kwargs
        return {"status": "PASS", "violations_found": 0}


def test_heal_routed_model_id_disabled():
    """When HEAL_POLICY_MODEL_ESCALATION is unset, _heal_routed_model_id not in kwargs."""
    from agentic_core.L5_safety.types.heal_policy_types import (
        HealEscalationDecision,
        ReasoningTier,
    )

    mock_decision = HealEscalationDecision(
        proceed=True,
        tier=ReasoningTier.LOW,
        rationale="Test",
        threshold_used="TEST",
    )

    # Ensure flag is disabled
    with patch.dict(os.environ, {}, clear=False):
        if "HEAL_POLICY_MODEL_ESCALATION" in os.environ:
            del os.environ["HEAL_POLICY_MODEL_ESCALATION"]

        with patch(
            "agentic_core.utils.decorators_util.decide_heal_escalation",
            return_value=mock_decision,
        ):
            healer = DummyHealer()
            result = healer.heal_repository(dry_run=True, execute=False)

            assert result["status"] == "PASS"
            assert "_heal_routed_model_id" not in healer._captured_kwargs


def test_heal_routed_model_id_enabled_with_router():
    """When enabled and router returns model_id, kwarg contains that model_id."""
    from agentic_core.L5_safety.types.heal_policy_types import ReasoningTier

    # Mock the router to return a specific model_id
    def mock_router(tier: ReasoningTier) -> str:
        return "local_high"

    with patch.dict(os.environ, {"HEAL_POLICY_MODEL_ESCALATION": "1"}):
        with patch("agentic_core.utils.decorators_util._HEAL_MODEL_ROUTER", mock_router):
            healer = DummyHealer()
            result = healer.heal_repository(dry_run=True, execute=False)

            assert result["status"] == "PASS"
            assert "_heal_routed_model_id" in healer._captured_kwargs
            assert healer._captured_kwargs["_heal_routed_model_id"] == "local_high"


def test_heal_routed_model_id_enabled_no_router():
    """When enabled but router is None, _heal_routed_model_id is None."""
    with patch.dict(os.environ, {"HEAL_POLICY_MODEL_ESCALATION": "1"}):
        with patch("agentic_core.utils.decorators_util._HEAL_MODEL_ROUTER", None):
            healer = DummyHealer()
            result = healer.heal_repository(dry_run=True, execute=False)

            assert result["status"] == "PASS"
            assert "_heal_routed_model_id" in healer._captured_kwargs
            assert healer._captured_kwargs["_heal_routed_model_id"] is None


def test_heal_routed_model_id_logging_enabled():
    """When enabled, routed_model log line is emitted."""
    from agentic_core.L5_safety.types.heal_policy_types import ReasoningTier

    def mock_router(tier: ReasoningTier) -> str:
        return "local_high"

    with patch.dict(os.environ, {"HEAL_POLICY_MODEL_ESCALATION": "1"}):
        with patch("agentic_core.utils.decorators_util._HEAL_MODEL_ROUTER", mock_router):
            with patch("agentic_core.utils.decorators_util.Logger") as mock_logger:
                healer = DummyHealer()
                result = healer.heal_repository(dry_run=True, execute=False)

                assert result["status"] == "PASS"

                # Check that routed_model log was emitted
                debug_calls = list(mock_logger.debug.call_args_list)
                routed_model_logs = [call for call in debug_calls if "routed_model=" in str(call)]
                assert len(routed_model_logs) >= 1, "Expected at least one routed_model log"


def test_heal_routed_model_id_disabled_no_logging():
    """When disabled, routed_model log is not emitted."""
    from agentic_core.L5_safety.types.heal_policy_types import (
        HealEscalationDecision,
        ReasoningTier,
    )

    mock_decision = HealEscalationDecision(
        proceed=True,
        tier=ReasoningTier.LOW,
        rationale="Test",
        threshold_used="TEST",
    )

    with patch.dict(os.environ, {}, clear=False):
        if "HEAL_POLICY_MODEL_ESCALATION" in os.environ:
            del os.environ["HEAL_POLICY_MODEL_ESCALATION"]

        with patch(
            "agentic_core.utils.decorators_util.decide_heal_escalation",
            return_value=mock_decision,
        ):
            with patch("agentic_core.utils.decorators_util.Logger") as mock_logger:
                healer = DummyHealer()
                result = healer.heal_repository(dry_run=True, execute=False)

                assert result["status"] == "PASS"

                # Check that routed_model log was NOT emitted
                debug_calls = list(mock_logger.debug.call_args_list)
                routed_model_logs = [call for call in debug_calls if "routed_model=" in str(call)]
                assert len(routed_model_logs) == 0
