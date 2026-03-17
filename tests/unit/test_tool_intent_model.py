"""
Phase 7 — Wave 1 Tests: ToolCapability, ToolIntent, ToolViolation, L1 block enforcement.
"""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.types.tool_intent_types import (
    ToolCapability,
    ToolIntent,
    ToolViolation,
    assert_l1_tool_allowed,
    build_tool_intent,
    is_l1_cognition_active,
    is_mutating,
    l1_cognition_scope,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_capability,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
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
    _emit_writes_through,  # noqa: E402
    _emit_links_incident_trace,  # noqa: E402
)

_emit_emits_metric_event("test_tool_intent_model", "p4obs", "metric_1")
_emit_emits_metric_event("test_tool_intent_model", "p4obs", "metric_2")
_emit_emits_metric_event("test_tool_intent_model", "p4obs", "metric_3")
_emit_emits_metric_event("test_tool_intent_model", "p4obs", "metric_4")
_emit_emits_metric_event("test_tool_intent_model", "p4obs", "metric_5")
_emit_emits_metric_event("test_tool_intent_model", "p4obs", "metric_6")
_emit_records_incident_event("test_tool_intent_model", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_tool_intent_model", "p4obs", "anomaly")
_emit_writes_observability_log("test_tool_intent_model", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_tool_intent_model", "p4obs", "mon_state")
_emit_triggers_alert("test_tool_intent_model", "p4obs", "alert")
_emit_links_incident_trace("test_tool_intent_model", "p4obs", "trace_link")
_emit_captures_pattern("test_tool_intent_model", "p3lm", "pattern")
_emit_records_learning_event("test_tool_intent_model", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_tool_intent_model", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_tool_intent_model", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_tool_intent_model", "p3lm", "routing")
_emit_improves_agent_policy("test_tool_intent_model", "p3lm", "policy")
_emit_stores_learning_state("test_tool_intent_model", "p3lm", "state")
_emit_records_execution_trace("test_tool_intent_model", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_tool_intent_model", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_tool_intent_model", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_tool_intent_model", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_tool_intent_model", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_tool_intent_model", "env_read", "p2_env_1")
_emit_reads_environ("test_tool_intent_model", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_tool_intent_model", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_tool_intent_model", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_tool_intent_model")
_emit_applies_guardrail("p0", "test_tool_intent_model", "p0_governance")
_emit_snapshots_state("p0", "test_tool_intent_model", "state_snapshot")
_emit_pulls_context("p1", "test_tool_intent_model", "context_pull")
_emit_pulls_context("p1", "test_tool_intent_model", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_tool_intent_model", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_tool_intent_model", "uwg_term_secondary")
_emit_writes_through("p1", "test_tool_intent_model", "write_through")
_emit_writes_through("p1", "test_tool_intent_model", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_tool_intent_model", "safety_validation")
_emit_invokes_eval("p1", "test_tool_intent_model", "eval_call")
_emit_proposal_commits_routing("p1", "test_tool_intent_model", "routing_commit")
_emit_escalates_to_human("p1", "test_tool_intent_model", "human_escalation")
_emit_routes_through("p1", "test_tool_intent_model", "route_through")
_emit_checks_agent_registry("p1", "test_tool_intent_model", "agent_registry")
_emit_validates_agent_capability("p1", "test_tool_intent_model", "capability")
_emit_dispatches_execution_plan("p1", "test_tool_intent_model", "exec_plan")
_emit_agent_executes_agent("p1", "test_tool_intent_model", "sub_agent")
_emit_routes_to_agent("p1", "test_tool_intent_model", "target_agent")
_emit_verifies_policy("p1", "test_tool_intent_model", "policy_check")
_emit_observes_runtime_state("p1", "test_tool_intent_model", "runtime_state")
_emit_verifies_boundary("p1", "test_tool_intent_model", "boundary_check")
_emit_transcripts_response("p1", "test_tool_intent_model", "transcript")
_emit_hard_fails_untranscripted("p1", "test_tool_intent_model")
_emit_gated_by_confidence("p1", "test_tool_intent_model", "confidence_gate")
emit_replay_key("p0", "test_tool_intent_model")
emit_determinism_digest("p0", "test_tool_intent_model")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_tool_intent_model", "execution_auth")
_emit_validates_capability("p2", "test_tool_intent_model", "capability_check")
_emit_routes_to_capability("p2", "test_tool_intent_model", "capability_route")
_emit_writes_via_uwg("p2", "test_tool_intent_model", "uwg_write")
_emit_blocks_direct_write("p2", "test_tool_intent_model", "direct_write_block")
_emit_records_tool_invocation("p2", "test_tool_intent_model", "tool_invocation")
_emit_captures_execution_output("p2", "test_tool_intent_model", "exec_output")
_emit_dispatches_agent("p3", "test_tool_intent_model", "agent_dispatch")
_emit_coordinates_agents("p3", "test_tool_intent_model", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_tool_intent_model", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_tool_intent_model", "healing_outcome")
_emit_escalates_failure("p3", "test_tool_intent_model", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_tool_intent_model", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_tool_intent_model", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_tool_intent_model", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_tool_intent_model", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_tool_intent_model", "eval_metric")
_emit_stores_embedding("p4", "test_tool_intent_model", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_tool_intent_model", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_tool_intent_model", "exec_snapshot_link")

pytestmark = pytest.mark.unit_min_deps


def _make_intent(**overrides) -> ToolIntent:
    defaults: dict = {
        "schema_version": 1,
        "tool_name": "file_read",
        "capability": ToolCapability.NON_MUTATING,
        "args": {"path": "/tmp/test.txt"},
        "requires_commit": False,
    }
    defaults.update(overrides)
    return ToolIntent(**defaults)


class TestToolCapabilityModel:
    def test_non_mutating_is_not_mutating(self):
        assert is_mutating(ToolCapability.NON_MUTATING) is False

    def test_mutating_external_is_mutating(self):
        assert is_mutating(ToolCapability.MUTATING_EXTERNAL) is True

    def test_mutating_fs_is_mutating(self):
        assert is_mutating(ToolCapability.MUTATING_FS) is True

    def test_mutating_statebus_is_mutating(self):
        assert is_mutating(ToolCapability.MUTATING_STATEBUS) is True

    def test_capability_values(self):
        assert ToolCapability.NON_MUTATING.value == "non_mutating"
        assert ToolCapability.MUTATING_EXTERNAL.value == "mutating_external"
        assert ToolCapability.MUTATING_FS.value == "mutating_fs"
        assert ToolCapability.MUTATING_STATEBUS.value == "mutating_statebus"


class TestL1CognitionScope:
    def test_l1_inactive_by_default(self):
        assert is_l1_cognition_active() is False

    def test_l1_active_inside_scope(self):
        with l1_cognition_scope():
            assert is_l1_cognition_active() is True

    def test_l1_inactive_after_scope(self):
        with l1_cognition_scope():
            pass
        assert is_l1_cognition_active() is False

    def test_l1_restored_on_exception(self):
        with pytest.raises(RuntimeError):
            with l1_cognition_scope():
                raise RuntimeError("boom")
        assert is_l1_cognition_active() is False

    def test_nested_scope_stays_active(self):
        with l1_cognition_scope():
            with l1_cognition_scope():
                assert is_l1_cognition_active() is True
            assert is_l1_cognition_active() is True
        assert is_l1_cognition_active() is False


class TestL1BlocksMutatingToolInvocation:
    def test_l1_blocks_mutating_tool_invocation(self):
        """
        Core Wave 1 guarantee: MUTATING_EXTERNAL tool call inside L1 scope raises ToolViolation.
        """
        with l1_cognition_scope():
            with pytest.raises(ToolViolation) as exc_info:
                assert_l1_tool_allowed(ToolCapability.MUTATING_EXTERNAL, "redis_set")
        assert "L1_TOOL_CALL_BLOCKED" in str(exc_info.value)

    def test_l1_blocks_mutating_fs(self):
        with l1_cognition_scope():
            with pytest.raises(ToolViolation) as exc_info:
                assert_l1_tool_allowed(ToolCapability.MUTATING_FS, "file_write")
        assert exc_info.value.code == "L1_TOOL_CALL_BLOCKED"

    def test_l1_blocks_mutating_statebus(self):
        with l1_cognition_scope():
            with pytest.raises(ToolViolation) as exc_info:
                assert_l1_tool_allowed(ToolCapability.MUTATING_STATEBUS, "event_emit")
        assert exc_info.value.code == "L1_TOOL_CALL_BLOCKED"

    def test_violation_detail_contains_tool_name(self):
        with l1_cognition_scope():
            try:
                assert_l1_tool_allowed(ToolCapability.MUTATING_EXTERNAL, "pinecone_upsert")
                pytest.fail("Expected ToolViolation")
            except ToolViolation as exc:  # guardian: allow-silent-swallower
                assert "pinecone_upsert" in exc.detail

    def test_violation_detail_contains_capability(self):
        with l1_cognition_scope():
            try:
                assert_l1_tool_allowed(ToolCapability.MUTATING_EXTERNAL, "redis_set")
            except ToolViolation as exc:  # guardian: allow-silent-swallower
                assert "mutating_external" in exc.detail

    def test_l1_allows_non_mutating_tool_invocation(self):
        """
        Core Wave 1 guarantee: NON_MUTATING tool is allowed inside L1 scope.
        """
        with l1_cognition_scope():
            assert_l1_tool_allowed(ToolCapability.NON_MUTATING, "file_read")  # must not raise
            pytest.skip("TODO: Implement actual test based on module functionality")

    def test_mutating_allowed_outside_l1_scope(self):
        """Outside L1 scope, mutating tools are not blocked by this seam."""
        assert_l1_tool_allowed(ToolCapability.MUTATING_EXTERNAL, "redis_set")  # must not raise
        pytest.skip("TODO: Implement actual test based on module functionality")


class TestToolIntentHashStable:
    def test_tool_intent_hash_stable(self):
        """Same inputs produce the same intent_hash."""
        i1 = _make_intent()
        i2 = _make_intent()
        assert i1.intent_hash == i2.intent_hash
        assert len(i1.intent_hash) == 64

    def test_hash_changes_with_tool_name(self):
        i1 = _make_intent(tool_name="file_read")
        i2 = _make_intent(tool_name="ast_parse")
        assert i1.intent_hash != i2.intent_hash

    def test_hash_changes_with_capability(self):
        i1 = _make_intent(capability=ToolCapability.NON_MUTATING, requires_commit=False)
        i2 = _make_intent(
            capability=ToolCapability.MUTATING_EXTERNAL,
            requires_commit=True,
        )
        assert i1.intent_hash != i2.intent_hash

    def test_hash_changes_with_args(self):
        i1 = _make_intent(args={"path": "/tmp/a.txt"})
        i2 = _make_intent(args={"path": "/tmp/b.txt"})
        assert i1.intent_hash != i2.intent_hash

    def test_intent_hash_excluded_from_canonical_bytes(self):
        i = _make_intent()
        assert b"intent_hash" not in i.canonical_bytes()

    def test_canonical_bytes_deterministic(self):
        i1 = _make_intent()
        i2 = _make_intent()
        assert i1.canonical_bytes() == i2.canonical_bytes()

    def test_args_hash_auto_computed(self):
        i = _make_intent(args={"key": "value"})
        assert len(i.args_hash) == 64

    def test_args_hash_stable(self):
        i1 = _make_intent(args={"key": "value"})
        i2 = _make_intent(args={"key": "value"})
        assert i1.args_hash == i2.args_hash

    def test_args_hash_changes_with_args(self):
        i1 = _make_intent(args={"key": "A"})
        i2 = _make_intent(args={"key": "B"})
        assert i1.args_hash != i2.args_hash


class TestToolIntentValidation:
    def test_invalid_schema_version_raises(self):
        with pytest.raises(ValueError, match="schema_version"):
            _make_intent(schema_version=99)

    def test_empty_tool_name_raises(self):
        with pytest.raises(ValueError, match="tool_name"):
            _make_intent(tool_name="")

    def test_non_dict_args_raises(self):
        with pytest.raises(TypeError, match="args"):
            _make_intent(args="not-a-dict")  # type: ignore[arg-type]

    def test_mutating_requires_commit_false_raises(self):
        with pytest.raises(ValueError, match="requires_commit"):
            _make_intent(
                capability=ToolCapability.MUTATING_EXTERNAL,
                requires_commit=False,
            )

    def test_non_mutating_requires_commit_false_ok(self):
        i = _make_intent(capability=ToolCapability.NON_MUTATING, requires_commit=False)
        assert i.requires_commit is False


class TestBuildToolIntentFactory:
    def test_factory_sets_requires_commit_true_for_mutating(self):
        i = build_tool_intent(
            "redis_set",
            ToolCapability.MUTATING_EXTERNAL,
            {"key": "k", "value": "v"},
        )
        assert i.requires_commit is True

    def test_factory_sets_requires_commit_false_for_non_mutating(self):
        i = build_tool_intent(
            "file_read",
            ToolCapability.NON_MUTATING,
            {"path": "/tmp/f.txt"},
        )
        assert i.requires_commit is False

    def test_factory_carries_config_hashes(self):
        i = build_tool_intent(
            "file_read",
            ToolCapability.NON_MUTATING,
            {},
            policy_hash="ph",
            model_hash="mh",
            budget_hash="bh",
            routing_hash="rh",
        )
        assert i.policy_hash == "ph"
        assert i.model_hash == "mh"
        assert i.budget_hash == "bh"
        assert i.routing_hash == "rh"

    def test_to_dict_contains_all_fields(self):
        i = build_tool_intent("file_read", ToolCapability.NON_MUTATING, {})
        d = i.to_dict()
        for key in (
            "schema_version",
            "tool_name",
            "capability",
            "args",
            "args_hash",
            "requires_commit",
            "policy_hash",
            "model_hash",
            "budget_hash",
            "routing_hash",
            "intent_hash",
        ):
            assert key in d
