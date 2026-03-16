"""
Test for remediation_dispatcher exception handling fix.

Covers:
- Healer exceptions are caught and converted to HealCheckResult with FAILED status
- No dead/unreachable code after raise (result is properly constructed)
- LLM escalation is triggered when needs_llm_escalation=True
"""

from unittest.mock import patch

import pytest

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

_emit_records_execution_trace("p0", "evidence", "test_remediation_dispatcher_exception_handling")
_emit_applies_guardrail("p0", "test_remediation_dispatcher_exception_handling", "p0_governance")
_emit_reads_policy_state("p0", "test_remediation_dispatcher_exception_handling", "policy_binding")
_emit_snapshots_state("p0", "test_remediation_dispatcher_exception_handling", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_remediation_dispatcher_exception_handling", "p4obs", "metric_1")
_emit_emits_metric_event("test_remediation_dispatcher_exception_handling", "p4obs", "metric_2")
_emit_emits_metric_event("test_remediation_dispatcher_exception_handling", "p4obs", "metric_3")
_emit_emits_metric_event("test_remediation_dispatcher_exception_handling", "p4obs", "metric_4")
_emit_emits_metric_event("test_remediation_dispatcher_exception_handling", "p4obs", "metric_5")
_emit_emits_metric_event("test_remediation_dispatcher_exception_handling", "p4obs", "metric_6")
_emit_records_incident_event("test_remediation_dispatcher_exception_handling", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_remediation_dispatcher_exception_handling", "p4obs", "anomaly")
_emit_writes_observability_log("test_remediation_dispatcher_exception_handling", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_remediation_dispatcher_exception_handling", "p4obs", "mon_state")
_emit_triggers_alert("test_remediation_dispatcher_exception_handling", "p4obs", "alert")
_emit_links_incident_trace("test_remediation_dispatcher_exception_handling", "p4obs", "trace_link")
_emit_captures_pattern("test_remediation_dispatcher_exception_handling", "p3lm", "pattern")
_emit_records_learning_event("test_remediation_dispatcher_exception_handling", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_remediation_dispatcher_exception_handling", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_remediation_dispatcher_exception_handling", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_remediation_dispatcher_exception_handling", "p3lm", "routing")
_emit_improves_agent_policy("test_remediation_dispatcher_exception_handling", "p3lm", "policy")
_emit_stores_learning_state("test_remediation_dispatcher_exception_handling", "p3lm", "state")
_emit_records_execution_trace("test_remediation_dispatcher_exception_handling", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_remediation_dispatcher_exception_handling", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_remediation_dispatcher_exception_handling", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_remediation_dispatcher_exception_handling", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_remediation_dispatcher_exception_handling", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_remediation_dispatcher_exception_handling", "env_read", "p2_env_1")
_emit_reads_environ("test_remediation_dispatcher_exception_handling", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_remediation_dispatcher_exception_handling", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_remediation_dispatcher_exception_handling", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_remediation_dispatcher_exception_handling", "context_pull")
_emit_pulls_context("p1", "test_remediation_dispatcher_exception_handling", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_remediation_dispatcher_exception_handling", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_remediation_dispatcher_exception_handling", "uwg_term_2")
_emit_writes_through("p1", "test_remediation_dispatcher_exception_handling", "write_through")
_emit_writes_through("p1", "test_remediation_dispatcher_exception_handling", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_remediation_dispatcher_exception_handling", "safety_validation")
_emit_invokes_eval("p1", "test_remediation_dispatcher_exception_handling", "eval_call")
_emit_proposal_commits_routing("p1", "test_remediation_dispatcher_exception_handling", "routing_commit")
emit_replay_key("p0", "test_remediation_dispatcher_exception_handling")
emit_determinism_digest("p0", "test_remediation_dispatcher_exception_handling")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_remediation_dispatcher_exception_handling", "execution_auth")
_emit_validates_capability("p2", "test_remediation_dispatcher_exception_handling", "capability_check")
_emit_routes_to_capability("p2", "test_remediation_dispatcher_exception_handling", "capability_route")
_emit_writes_via_uwg("p2", "test_remediation_dispatcher_exception_handling", "uwg_write")
_emit_blocks_direct_write("p2", "test_remediation_dispatcher_exception_handling", "direct_write_block")
_emit_records_tool_invocation("p2", "test_remediation_dispatcher_exception_handling", "tool_invocation")
_emit_captures_execution_output("p2", "test_remediation_dispatcher_exception_handling", "exec_output")
_emit_dispatches_agent("p3", "test_remediation_dispatcher_exception_handling", "agent_dispatch")
_emit_coordinates_agents("p3", "test_remediation_dispatcher_exception_handling", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_remediation_dispatcher_exception_handling", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_remediation_dispatcher_exception_handling", "healing_outcome")
_emit_escalates_failure("p3", "test_remediation_dispatcher_exception_handling", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_remediation_dispatcher_exception_handling", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_remediation_dispatcher_exception_handling", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_remediation_dispatcher_exception_handling", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_remediation_dispatcher_exception_handling", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_remediation_dispatcher_exception_handling", "eval_metric")
_emit_stores_embedding("p4", "test_remediation_dispatcher_exception_handling", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_remediation_dispatcher_exception_handling", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_remediation_dispatcher_exception_handling", "exec_snapshot_link")


class TestHealerExceptionHandling:
    """Test that healer exceptions are properly caught and converted to FAILED results."""

    def test_healer_exception_caught_and_converted_to_failed_result(self):
        """When healer raises exception, should catch it and return HealCheckResult with FAILED status."""
        from agentic_core.L2_execution.scripts.remediation_dispatcher import (
            HealCheckResult,
            HealStatus,
            _invoke_healer,
        )

        # Mock a healer that raises an exception
        def failing_healer(check_dict, repo_root=None, apply=False):
            raise ValueError("Healer internal error")

        check_id = "test_check"
        check_dict = {"check_id": check_id, "violations": []}
        repo_root = "/fake/repo"

        # Mock the HEALER_REGISTRY
        with patch(
            "agentic_core.L2_execution.scripts.remediation_dispatcher.HEALER_REGISTRY",
            {check_id: failing_healer},
        ):
            result = _invoke_healer(
                check_id=check_id,
                check_dict=check_dict,
                repo_root=repo_root,
                apply=False,
                retry_count=0,
                tier_invoker=None,
            )

            # Should return a HealCheckResult with FAILED status
            assert isinstance(result, HealCheckResult)
            assert result.status == HealStatus.FAILED
            assert "ValueError" in result.notes
            assert "Healer internal error" in result.notes
            assert result.needs_llm_escalation is True
            assert result.escalation_hint == "failure_type=healer_error"

    def test_healer_exception_triggers_llm_escalation_when_in_allowlist(self):
        """When healer raises exception and check_id is in allowlist, should trigger LLM escalation."""
        from agentic_core.L2_execution.scripts.remediation_dispatcher import (
            _invoke_healer,
        )

        def failing_healer(check_dict, repo_root=None, apply=False):
            raise RuntimeError("Healer crashed")

        check_id = "test_check_in_allowlist"
        check_dict = {"check_id": check_id, "violations": []}

        # Mock both HEALER_REGISTRY and HEALER_ESCALATION_ALLOWLIST
        with patch(
            "agentic_core.L2_execution.scripts.remediation_dispatcher.HEALER_REGISTRY",
            {check_id: failing_healer},
        ):
            with patch(
                "agentic_core.L2_execution.scripts.remediation_dispatcher.HEALER_ESCALATION_ALLOWLIST",
                frozenset([check_id]),
            ):
                # Mock _tier_escalate to verify it's called
                with patch(
                    "agentic_core.L2_execution.scripts.remediation_dispatcher._tier_escalate",
                    return_value="escalation_note",
                ) as mock_escalate:
                    result = _invoke_healer(
                        check_id=check_id,
                        check_dict=check_dict,
                        repo_root="/fake/repo",
                        apply=False,
                        retry_count=0,
                        tier_invoker=None,
                    )

                    # Should have called _tier_escalate
                    assert mock_escalate.called
                    # Result should include escalation note
                    assert "escalation_note" in result.notes

    def test_healer_success_does_not_trigger_exception_path(self):
        """When healer succeeds, should return its result without exception handling."""
        from agentic_core.L2_execution.scripts.remediation_dispatcher import (
            HealCheckResult,
            HealStatus,
            _invoke_healer,
        )

        def successful_healer(check_dict, repo_root=None, apply=False):
            return HealCheckResult(
                check_id="test_check",
                status=HealStatus.HEALED,
                changes_made=("fixed_file.py",),
                rollback_info=None,
                notes="All good",
                needs_llm_escalation=False,
                escalation_hint=None,
            )

        check_id = "test_check"
        check_dict = {"check_id": check_id, "violations": []}

        with patch(
            "agentic_core.L2_execution.scripts.remediation_dispatcher.HEALER_REGISTRY",
            {check_id: successful_healer},
        ):
            result = _invoke_healer(
                check_id=check_id,
                check_dict=check_dict,
                repo_root="/fake/repo",
                apply=False,
                retry_count=0,
                tier_invoker=None,
            )

            # Should return the healer's success result unchanged
            assert result.status == HealStatus.HEALED
            assert result.notes == "All good"
            assert result.needs_llm_escalation is False


class TestNoDeadCodeAfterRaise:
    """Verify that the dead code after raise has been removed."""

    def test_exception_handler_constructs_result_not_unreachable_code(self):
        """The except block should construct HealCheckResult, not have dead code after raise."""
        import inspect

        from agentic_core.L2_execution.scripts.remediation_dispatcher import _invoke_healer

        # Get the source code of the function
        source = inspect.getsource(_invoke_healer)

        # The fixed version should NOT have "raise  # Re-raise after logging/handling"
        # followed by unreachable result construction
        assert "raise  # Re-raise after logging/handling" not in source

        # Should have proper exception handling that constructs result
        assert "except Exception as exc:" in source
        assert "result = HealCheckResult(" in source


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
