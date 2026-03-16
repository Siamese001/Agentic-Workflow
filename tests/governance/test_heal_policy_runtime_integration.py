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
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "test_heal_policy_runtime_integration", "execution_auth")
_emit_validates_capability("p2", "test_heal_policy_runtime_integration", "capability_check")
_emit_routes_to_capability("p2", "test_heal_policy_runtime_integration", "capability_route")
_emit_writes_via_uwg("p2", "test_heal_policy_runtime_integration", "uwg_write")
_emit_blocks_direct_write("p2", "test_heal_policy_runtime_integration", "direct_write_block")
_emit_records_tool_invocation("p2", "test_heal_policy_runtime_integration", "tool_invocation")
_emit_captures_execution_output("p2", "test_heal_policy_runtime_integration", "exec_output")
_emit_dispatches_agent("p3", "test_heal_policy_runtime_integration", "agent_dispatch")
_emit_coordinates_agents("p3", "test_heal_policy_runtime_integration", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_heal_policy_runtime_integration", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_heal_policy_runtime_integration", "healing_outcome")
_emit_escalates_failure("p3", "test_heal_policy_runtime_integration", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_heal_policy_runtime_integration", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_heal_policy_runtime_integration", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_heal_policy_runtime_integration", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_heal_policy_runtime_integration", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_heal_policy_runtime_integration", "eval_metric")
_emit_stores_embedding("p4", "test_heal_policy_runtime_integration", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_heal_policy_runtime_integration", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_heal_policy_runtime_integration", "exec_snapshot_link")
from agentic_core.utils.decorators_compat_util import standard_heal

_emit_records_execution_trace("p0", "evidence", "test_heal_policy_runtime_integration")
_emit_applies_guardrail("p0", "test_heal_policy_runtime_integration", "p0_governance")
_emit_reads_policy_state("p0", "test_heal_policy_runtime_integration", "policy_binding")
_emit_snapshots_state("p0", "test_heal_policy_runtime_integration", "state_snapshot")
emit_replay_key("p0", "test_heal_policy_runtime_integration")
emit_determinism_digest("p0", "test_heal_policy_runtime_integration")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
            proceed=True,
            tier=ReasoningTier.LOW,
            rationale="Test rationale",
            threshold_used="TEST",
        )

        with patch(
            "agentic_core.utils.decorators_util.decide_heal_escalation",
            return_value=mock_decision,
        ) as mock_decide:
            healer = DummyHealer()
            healer.heal_repository(dry_run=True)

            mock_decide.assert_called_once()

    def test_policy_decision_is_logged(self) -> None:
        """Assert Logger.debug receives the policy decision log line."""
        mock_decision = HealEscalationDecision(
            proceed=True,
            tier=ReasoningTier.LOW,
            rationale="Test rationale",
            threshold_used="TEST",
        )

        captured_messages: list[str] = []

        def capture_debug(msg: str, *args: Any, **kwargs: Any) -> None:
            captured_messages.append(msg)

        with (
            patch(
                "agentic_core.utils.decorators_util.decide_heal_escalation",
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
            proceed=True,
            tier=ReasoningTier.LOW,
            rationale="Test rationale",
            threshold_used="TEST",
        )

        with patch(
            "agentic_core.utils.decorators_util.decide_heal_escalation",
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
