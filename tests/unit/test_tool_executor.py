"""
Phase 7 — Wave 2 Tests: ToolIntentExecutor (L2.2 sandbox-only) + ToolResult.
"""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.engines.tool_intent_executor import (
    ToolIntentExecutor,
    ToolResult,
)
from agentic_core.L2_execution.types.ml_write_intent_types import MLWriteIntentExecutor
from agentic_core.L2_execution.types.tool_intent_types import (
    ToolCapability,
    ToolViolation,
    build_tool_intent,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("test_tool_executor", "p4obs", "metric_1")
_emit_emits_metric_event("test_tool_executor", "p4obs", "metric_2")
_emit_emits_metric_event("test_tool_executor", "p4obs", "metric_3")
_emit_emits_metric_event("test_tool_executor", "p4obs", "metric_4")
_emit_emits_metric_event("test_tool_executor", "p4obs", "metric_5")
_emit_emits_metric_event("test_tool_executor", "p4obs", "metric_6")
_emit_records_incident_event("test_tool_executor", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_tool_executor", "p4obs", "anomaly")
_emit_writes_observability_log("test_tool_executor", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_tool_executor", "p4obs", "mon_state")
_emit_triggers_alert("test_tool_executor", "p4obs", "alert")
_emit_links_incident_trace("test_tool_executor", "p4obs", "trace_link")
_emit_captures_pattern("test_tool_executor", "p3lm", "pattern")
_emit_records_learning_event("test_tool_executor", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_tool_executor", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_tool_executor", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_tool_executor", "p3lm", "routing")
_emit_improves_agent_policy("test_tool_executor", "p3lm", "policy")
_emit_stores_learning_state("test_tool_executor", "p3lm", "state")
_emit_records_execution_trace("test_tool_executor", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_tool_executor", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_tool_executor", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_tool_executor", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_tool_executor", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_tool_executor", "env_read", "p2_env_1")
_emit_reads_environ("test_tool_executor", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_tool_executor", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_tool_executor", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_tool_executor")
_emit_applies_guardrail("p0", "test_tool_executor", "p0_governance")
_emit_reads_policy_state("p0", "test_tool_executor", "policy_binding")
_emit_snapshots_state("p0", "test_tool_executor", "state_snapshot")
_emit_pulls_context("p1", "test_tool_executor", "context_pull")
_emit_pulls_context("p1", "test_tool_executor", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_tool_executor", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_tool_executor", "uwg_term_secondary")
_emit_writes_through("p1", "test_tool_executor", "write_through")
_emit_writes_through("p1", "test_tool_executor", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_tool_executor", "safety_validation")
_emit_invokes_eval("p1", "test_tool_executor", "eval_call")
_emit_proposal_commits_routing("p1", "test_tool_executor", "routing_commit")
_emit_escalates_to_human("p1", "test_tool_executor", "human_escalation")
_emit_routes_through("p1", "test_tool_executor", "route_through")
_emit_checks_agent_registry("p1", "test_tool_executor", "agent_registry")
_emit_validates_agent_capability("p1", "test_tool_executor", "capability")
_emit_dispatches_execution_plan("p1", "test_tool_executor", "exec_plan")
_emit_agent_executes_agent("p1", "test_tool_executor", "sub_agent")
_emit_routes_to_agent("p1", "test_tool_executor", "target_agent")
_emit_verifies_policy("p1", "test_tool_executor", "policy_check")
_emit_observes_runtime_state("p1", "test_tool_executor", "runtime_state")
_emit_verifies_boundary("p1", "test_tool_executor", "boundary_check")
_emit_transcripts_response("p1", "test_tool_executor", "transcript")
_emit_hard_fails_untranscripted("p1", "test_tool_executor")
_emit_gated_by_confidence("p1", "test_tool_executor", "confidence_gate")
emit_replay_key("p0", "test_tool_executor")
emit_determinism_digest("p0", "test_tool_executor")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_tool_executor", "execution_auth")
_emit_validates_capability("p2", "test_tool_executor", "capability_check")
_emit_routes_to_capability("p2", "test_tool_executor", "capability_route")
_emit_writes_via_uwg("p2", "test_tool_executor", "uwg_write")
_emit_blocks_direct_write("p2", "test_tool_executor", "direct_write_block")
_emit_records_tool_invocation("p2", "test_tool_executor", "tool_invocation")
_emit_captures_execution_output("p2", "test_tool_executor", "exec_output")
_emit_dispatches_agent("p3", "test_tool_executor", "agent_dispatch")
_emit_coordinates_agents("p3", "test_tool_executor", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_tool_executor", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_tool_executor", "healing_outcome")
_emit_escalates_failure("p3", "test_tool_executor", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_tool_executor", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_tool_executor", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_tool_executor", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_tool_executor", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_tool_executor", "eval_metric")
_emit_stores_embedding("p4", "test_tool_executor", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_tool_executor", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_tool_executor", "exec_snapshot_link")

pytestmark = pytest.mark.unit_min_deps

_TS = "2026-02-21T00:00:00Z"


def _noop_fn(args: dict) -> dict:
    return {"output_summary": "ok", "success": True, "anchor_ids": []}


def _retrieval_fn(args: dict) -> dict:
    return {
        "output_summary": "retrieved 2 chunks",
        "success": True,
        "anchor_ids": ["chunk-B", "chunk-A"],
    }


def _failing_fn(args: dict) -> dict:
    return {"output_summary": "error: timeout", "success": False, "anchor_ids": []}


class TestToolIntentExecBlockedOutsideSandbox:
    def test_tool_intent_exec_blocked_outside_sandbox(self):
        """
        Core Wave 2 guarantee: mutating ToolIntent executed outside sandbox raises
        ToolViolation(code="TOOL_WRITE_OUTSIDE_SANDBOX").
        """
        intent = build_tool_intent(
            "redis_set",
            ToolCapability.MUTATING_EXTERNAL,
            {"key": "k", "value": "v"},
        )
        executor = ToolIntentExecutor()
        with pytest.raises(ToolViolation) as exc_info:
            executor.execute(intent, fn=_noop_fn)
        assert exc_info.value.code == "TOOL_WRITE_OUTSIDE_SANDBOX"

    def test_mutating_fs_blocked_outside_sandbox(self):
        intent = build_tool_intent(
            "file_write",
            ToolCapability.MUTATING_FS,
            {"path": "/tmp/out.txt", "content": "data"},
        )
        executor = ToolIntentExecutor()
        with pytest.raises(ToolViolation) as exc_info:
            executor.execute(intent, fn=_noop_fn)
        assert "TOOL_WRITE_OUTSIDE_SANDBOX" in str(exc_info.value)

    def test_mutating_statebus_blocked_outside_sandbox(self):
        intent = build_tool_intent(
            "event_emit",
            ToolCapability.MUTATING_STATEBUS,
            {"event": "done"},
        )
        executor = ToolIntentExecutor()
        with pytest.raises(ToolViolation) as exc_info:
            executor.execute(intent, fn=_noop_fn)
        assert exc_info.value.code == "TOOL_WRITE_OUTSIDE_SANDBOX"

    def test_violation_detail_contains_tool_name(self):
        intent = build_tool_intent(
            "pinecone_upsert",
            ToolCapability.MUTATING_EXTERNAL,
            {"vectors": []},
        )
        executor = ToolIntentExecutor()
        try:
            executor.execute(intent, fn=_noop_fn)
            pytest.fail("Expected ToolViolation")
        except ToolViolation as exc:  # guardian: allow-silent-swallower
            assert "pinecone_upsert" in exc.detail


class TestToolIntentExecAllowedInsideSandbox:
    def test_tool_intent_exec_allowed_inside_sandbox(self):
        """
        Core Wave 2 guarantee: mutating ToolIntent executed inside sandbox succeeds.
        """
        intent = build_tool_intent(
            "redis_set",
            ToolCapability.MUTATING_EXTERNAL,
            {"key": "k", "value": "v"},
        )
        executor = ToolIntentExecutor()
        with MLWriteIntentExecutor():
            result = executor.execute(intent, fn=_noop_fn)
        assert isinstance(result, ToolResult)
        assert result.success is True
        assert result.tool_name == "redis_set"

    def test_non_mutating_allowed_outside_sandbox(self):
        """NON_MUTATING tools (requires_commit=False) may execute anywhere."""
        intent = build_tool_intent(
            "file_read",
            ToolCapability.NON_MUTATING,
            {"path": "/tmp/f.txt"},
        )
        executor = ToolIntentExecutor()
        result = executor.execute(intent, fn=_noop_fn)
        assert result.success is True

    def test_mutating_fs_allowed_inside_sandbox(self):
        intent = build_tool_intent(
            "file_write",
            ToolCapability.MUTATING_FS,
            {"path": "/tmp/out.txt", "content": "data"},
        )
        executor = ToolIntentExecutor()
        with MLWriteIntentExecutor():
            result = executor.execute(intent, fn=_noop_fn)
        assert result.success is True

    def test_result_args_hash_matches_intent(self):
        intent = build_tool_intent(
            "file_read",
            ToolCapability.NON_MUTATING,
            {"path": "/tmp/f.txt"},
        )
        executor = ToolIntentExecutor()
        result = executor.execute(intent, fn=_noop_fn)
        assert result.args_hash == intent.args_hash

    def test_result_tool_name_matches_intent(self):
        intent = build_tool_intent(
            "ast_parse",
            ToolCapability.NON_MUTATING,
            {"code": "x = 1"},
        )
        executor = ToolIntentExecutor()
        result = executor.execute(intent, fn=_noop_fn)
        assert result.tool_name == "ast_parse"

    def test_result_anchor_ids_sorted(self):
        intent = build_tool_intent(
            "llm_call",
            ToolCapability.NON_MUTATING,
            {"prompt": "hello"},
        )
        executor = ToolIntentExecutor()
        result = executor.execute(intent, fn=_retrieval_fn)
        assert result.anchor_ids == sorted(result.anchor_ids)

    def test_failing_fn_produces_success_false(self):
        intent = build_tool_intent(
            "file_read",
            ToolCapability.NON_MUTATING,
            {"path": "/tmp/missing.txt"},
        )
        executor = ToolIntentExecutor()
        result = executor.execute(intent, fn=_failing_fn)
        assert result.success is False
        assert "error" in result.output_summary


class TestToolResultHashStable:
    def _make_result(self, **overrides) -> ToolResult:
        defaults: dict = {
            "schema_version": 1,
            "tool_name": "file_read",
            "args_hash": "a" * 64,
            "success": True,
            "output_summary": "ok",
            "anchor_ids": [],
        }
        defaults.update(overrides)
        return ToolResult(**defaults)

    def test_tool_result_hash_stable(self):
        """Same inputs produce the same result_hash."""
        r1 = self._make_result()
        r2 = self._make_result()
        assert r1.result_hash == r2.result_hash
        assert len(r1.result_hash) == 64

    def test_hash_changes_with_tool_name(self):
        r1 = self._make_result(tool_name="file_read")
        r2 = self._make_result(tool_name="ast_parse")
        assert r1.result_hash != r2.result_hash

    def test_hash_changes_with_success(self):
        r1 = self._make_result(success=True)
        r2 = self._make_result(success=False)
        assert r1.result_hash != r2.result_hash

    def test_hash_changes_with_output_summary(self):
        r1 = self._make_result(output_summary="ok")
        r2 = self._make_result(output_summary="error")
        assert r1.result_hash != r2.result_hash

    def test_hash_changes_with_anchor_ids(self):
        r1 = self._make_result(anchor_ids=[])
        r2 = self._make_result(anchor_ids=["chunk-A"])
        assert r1.result_hash != r2.result_hash

    def test_result_hash_excluded_from_canonical_bytes(self):
        r = self._make_result()
        assert b"result_hash" not in r.canonical_bytes()

    def test_canonical_bytes_deterministic(self):
        r1 = self._make_result()
        r2 = self._make_result()
        assert r1.canonical_bytes() == r2.canonical_bytes()

    def test_anchor_ids_sorted_in_canonical_bytes(self):
        r1 = self._make_result(anchor_ids=["chunk-Z", "chunk-A"])
        r2 = self._make_result(anchor_ids=["chunk-A", "chunk-Z"])
        assert r1.result_hash == r2.result_hash

    def test_to_dict_contains_all_fields(self):
        r = self._make_result()
        d = r.to_dict()
        for key in (
            "schema_version",
            "tool_name",
            "args_hash",
            "success",
            "output_summary",
            "anchor_ids",
            "result_hash",
        ):
            assert key in d


class TestToolResultValidation:
    def test_invalid_schema_version_raises(self):
        with pytest.raises(ValueError, match="schema_version"):
            ToolResult(
                schema_version=99,
                tool_name="file_read",
                args_hash="a" * 64,
                success=True,
                output_summary="ok",
                anchor_ids=[],
            )

    def test_empty_tool_name_raises(self):
        with pytest.raises(ValueError, match="tool_name"):
            ToolResult(
                schema_version=1,
                tool_name="",
                args_hash="a" * 64,
                success=True,
                output_summary="ok",
                anchor_ids=[],
            )

    def test_empty_args_hash_raises(self):
        with pytest.raises(ValueError, match="args_hash"):
            ToolResult(
                schema_version=1,
                tool_name="file_read",
                args_hash="",
                success=True,
                output_summary="ok",
                anchor_ids=[],
            )

    def test_non_list_anchor_ids_raises(self):
        with pytest.raises(TypeError, match="anchor_ids"):
            ToolResult(
                schema_version=1,
                tool_name="file_read",
                args_hash="a" * 64,
                success=True,
                output_summary="ok",
                anchor_ids="not-a-list",  # type: ignore[arg-type]
            )
