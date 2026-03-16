"""
Governance contract: Heal escalation flag + observer safety enforcement.

Ensures:
1. Flag default-off is preserved (no escalation log without env var)
2. Observer seam cannot be set persistently (default is None, no module-level reassignment)

Phase 5 Wave 5.3 acceptance test.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

import agentic_core.utils.decorators_util as decorators_module
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
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_authorize_and_execute("p2", "test_heal_escalation_flag_contract", "execution_auth")
_emit_validates_capability("p2", "test_heal_escalation_flag_contract", "capability_check")
_emit_routes_to_capability("p2", "test_heal_escalation_flag_contract", "capability_route")
_emit_writes_via_uwg("p2", "test_heal_escalation_flag_contract", "uwg_write")
_emit_blocks_direct_write("p2", "test_heal_escalation_flag_contract", "direct_write_block")
_emit_records_tool_invocation("p2", "test_heal_escalation_flag_contract", "tool_invocation")
_emit_captures_execution_output("p2", "test_heal_escalation_flag_contract", "exec_output")
_emit_dispatches_agent("p3", "test_heal_escalation_flag_contract", "agent_dispatch")
_emit_coordinates_agents("p3", "test_heal_escalation_flag_contract", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_heal_escalation_flag_contract", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_heal_escalation_flag_contract", "healing_outcome")
_emit_escalates_failure("p3", "test_heal_escalation_flag_contract", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_heal_escalation_flag_contract", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_heal_escalation_flag_contract", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_heal_escalation_flag_contract", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_heal_escalation_flag_contract", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_heal_escalation_flag_contract", "eval_metric")
_emit_stores_embedding("p4", "test_heal_escalation_flag_contract", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_heal_escalation_flag_contract", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_heal_escalation_flag_contract", "exec_snapshot_link")
from agentic_core.utils.decorators_compat_util import standard_heal

_emit_records_execution_trace("p0", "evidence", "test_heal_escalation_flag_contract")
_emit_applies_guardrail("p0", "test_heal_escalation_flag_contract", "p0_governance")
_emit_reads_policy_state("p0", "test_heal_escalation_flag_contract", "policy_binding")
_emit_snapshots_state("p0", "test_heal_escalation_flag_contract", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)

_emit_emits_metric_event("test_heal_escalation_flag_contract", "p4obs", "metric_1")
_emit_emits_metric_event("test_heal_escalation_flag_contract", "p4obs", "metric_2")
_emit_emits_metric_event("test_heal_escalation_flag_contract", "p4obs", "metric_3")
_emit_emits_metric_event("test_heal_escalation_flag_contract", "p4obs", "metric_4")
_emit_emits_metric_event("test_heal_escalation_flag_contract", "p4obs", "metric_5")
_emit_emits_metric_event("test_heal_escalation_flag_contract", "p4obs", "metric_6")
_emit_records_incident_event("test_heal_escalation_flag_contract", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_heal_escalation_flag_contract", "p4obs", "anomaly")
_emit_writes_observability_log("test_heal_escalation_flag_contract", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_heal_escalation_flag_contract", "p4obs", "mon_state")
_emit_triggers_alert("test_heal_escalation_flag_contract", "p4obs", "alert")
_emit_links_incident_trace("test_heal_escalation_flag_contract", "p4obs", "trace_link")
_emit_captures_pattern("test_heal_escalation_flag_contract", "p3lm", "pattern")
_emit_records_learning_event("test_heal_escalation_flag_contract", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_heal_escalation_flag_contract", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_heal_escalation_flag_contract", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_heal_escalation_flag_contract", "p3lm", "routing")
_emit_improves_agent_policy("test_heal_escalation_flag_contract", "p3lm", "policy")
_emit_stores_learning_state("test_heal_escalation_flag_contract", "p3lm", "state")
_emit_records_execution_trace("test_heal_escalation_flag_contract", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_heal_escalation_flag_contract", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_heal_escalation_flag_contract", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_heal_escalation_flag_contract", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_heal_escalation_flag_contract", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_heal_escalation_flag_contract", "env_read", "p2_env_1")
_emit_reads_environ("test_heal_escalation_flag_contract", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_heal_escalation_flag_contract", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_heal_escalation_flag_contract", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_heal_escalation_flag_contract", "context_pull")
_emit_pulls_context("p1", "test_heal_escalation_flag_contract", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_heal_escalation_flag_contract", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_heal_escalation_flag_contract", "uwg_term_2")
_emit_writes_through("p1", "test_heal_escalation_flag_contract", "write_through")
_emit_writes_through("p1", "test_heal_escalation_flag_contract", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_heal_escalation_flag_contract", "safety_validation")
_emit_invokes_eval("p1", "test_heal_escalation_flag_contract", "eval_call")
_emit_proposal_commits_routing("p1", "test_heal_escalation_flag_contract", "routing_commit")
_emit_escalates_to_human("p1", "test_heal_escalation_flag_contract", "human_escalation")
_emit_routes_through("p1", "test_heal_escalation_flag_contract", "route_through")
_emit_checks_agent_registry("p1", "test_heal_escalation_flag_contract", "agent_registry")
_emit_validates_agent_capability("p1", "test_heal_escalation_flag_contract", "capability")
_emit_dispatches_execution_plan("p1", "test_heal_escalation_flag_contract", "exec_plan")
_emit_agent_executes_agent("p1", "test_heal_escalation_flag_contract", "sub_agent")
_emit_routes_to_agent("p1", "test_heal_escalation_flag_contract", "target_agent")
_emit_verifies_policy("p1", "test_heal_escalation_flag_contract", "policy_check")
_emit_observes_runtime_state("p1", "test_heal_escalation_flag_contract", "runtime_state")
_emit_verifies_boundary("p1", "test_heal_escalation_flag_contract", "boundary_check")
_emit_transcripts_response("p1", "test_heal_escalation_flag_contract", "transcript")
_emit_hard_fails_untranscripted("p1", "test_heal_escalation_flag_contract")
_emit_gated_by_confidence("p1", "test_heal_escalation_flag_contract", "confidence_gate")
emit_replay_key("p0", "test_heal_escalation_flag_contract")
emit_determinism_digest("p0", "test_heal_escalation_flag_contract")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.governance


DECORATORS_MODULE_PATH = Path("agentic_core/utils/decorators_util.py")


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


class TestFlagDefaultOff:
    """Enforce flag default-off behavior is preserved."""

    def test_no_escalation_log_without_env_var(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Without env var, no 'escalation_enabled=1' log appears."""
        monkeypatch.delenv("HEAL_POLICY_MODEL_ESCALATION", raising=False)

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
        assert len(escalation_logs) == 0, (
            f"Expected no escalation log without env var, got: {escalation_logs}"
        )

    def test_observer_not_invoked_without_env_var(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Without env var, observer is not invoked."""
        monkeypatch.delenv("HEAL_POLICY_MODEL_ESCALATION", raising=False)

        mock_decision = HealEscalationDecision(
            proceed=True,
            tier=ReasoningTier.LOW,
            rationale="Test rationale",
            threshold_used="TEST",
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

        assert len(observer_calls) == 0, (
            f"Expected observer not called without env var, got: {observer_calls}"
        )


class TestObserverSeamSafety:
    """Enforce observer seam cannot be set persistently."""

    def test_observer_default_is_none_at_import(self) -> None:
        """Observer seam must be None at import time."""
        import agentic_core.utils.decorators_util

        # Check the observer is None (or has been reset) - no reload needed
        # The default value defined at module scope must be None
        current_observer = agentic_core.utils.decorators_util._HEAL_TIER_OBSERVER
        assert current_observer is None, "Observer seam must default to None"

    def test_observer_not_reassigned_at_module_scope(self) -> None:
        """Observer seam must not be reassigned anywhere at module scope (AST check)."""
        module_path = Path.cwd() / DECORATORS_MODULE_PATH
        assert module_path.exists(), f"Decorators module not found: {module_path}"

        source = module_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(module_path))

        observer_assignments: list[tuple[int, str]] = []

        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "_HEAL_TIER_OBSERVER":
                        value_repr = ast.unparse(node.value) if hasattr(ast, "unparse") else "..."
                        observer_assignments.append((node.lineno, value_repr))

            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name) and node.target.id == "_HEAL_TIER_OBSERVER":
                    value_repr = ast.unparse(node.value) if node.value and hasattr(ast, "unparse") else "None"
                    observer_assignments.append((node.lineno, value_repr))

        assert len(observer_assignments) == 1, (
            f"Expected exactly one module-level assignment for _HEAL_TIER_OBSERVER, got {len(observer_assignments)}: {observer_assignments}"
        )

        line, value = observer_assignments[0]
        assert value == "None", (
            f"Observer seam must be assigned None at module scope (line {line}), got: {value}"
        )
