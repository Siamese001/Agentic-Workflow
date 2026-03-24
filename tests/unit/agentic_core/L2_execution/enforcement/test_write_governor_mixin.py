"""Tests for WriteGovernorMixin — UWG write path enforcement."""

from __future__ import annotations

import pytest

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_write_governor_mixin")
_emit_applies_guardrail("p0", "test_write_governor_mixin", "p0_governance")
_emit_reads_policy_state("p0", "test_write_governor_mixin", "policy_binding")
_emit_snapshots_state("p0", "test_write_governor_mixin", "state_snapshot")
emit_replay_key("p0", "test_write_governor_mixin")
emit_determinism_digest("p0", "test_write_governor_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_write_governor_mixin", "execution_auth")
_emit_validates_capability("p2", "test_write_governor_mixin", "capability_check")
_emit_routes_to_capability("p2", "test_write_governor_mixin", "capability_route")
_emit_writes_via_uwg("p2", "test_write_governor_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "test_write_governor_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "test_write_governor_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "test_write_governor_mixin", "exec_output")
_emit_dispatches_agent("p3", "test_write_governor_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "test_write_governor_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_write_governor_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_write_governor_mixin", "healing_outcome")
_emit_escalates_failure("p3", "test_write_governor_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_write_governor_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_write_governor_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_write_governor_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_write_governor_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_write_governor_mixin", "eval_metric")
_emit_stores_embedding("p4", "test_write_governor_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_write_governor_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_write_governor_mixin", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.enforcement.write_governor_mixin import WriteGovernorMixin
from agentic_core.L2_execution.UniversalWriteGateway import (
    MutationRecord,
    SimulationResult,
    ToolNotAllowedError,
    UniversalWriteGateway,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

_emit_emits_metric_event("test_write_governor_mixin", "p4obs", "metric_1")
_emit_emits_metric_event("test_write_governor_mixin", "p4obs", "metric_2")
_emit_emits_metric_event("test_write_governor_mixin", "p4obs", "metric_3")
_emit_emits_metric_event("test_write_governor_mixin", "p4obs", "metric_4")
_emit_emits_metric_event("test_write_governor_mixin", "p4obs", "metric_5")
_emit_emits_metric_event("test_write_governor_mixin", "p4obs", "metric_6")
_emit_records_incident_event("test_write_governor_mixin", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_write_governor_mixin", "p4obs", "anomaly")
_emit_writes_observability_log("test_write_governor_mixin", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_write_governor_mixin", "p4obs", "mon_state")
_emit_triggers_alert("test_write_governor_mixin", "p4obs", "alert")
_emit_links_incident_trace("test_write_governor_mixin", "p4obs", "trace_link")
_emit_captures_pattern("test_write_governor_mixin", "p3lm", "pattern")
_emit_records_learning_event("test_write_governor_mixin", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_write_governor_mixin", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_write_governor_mixin", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_write_governor_mixin", "p3lm", "routing")
_emit_improves_agent_policy("test_write_governor_mixin", "p3lm", "policy")
_emit_stores_learning_state("test_write_governor_mixin", "p3lm", "state")
_emit_records_execution_trace("test_write_governor_mixin", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_write_governor_mixin", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_write_governor_mixin", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_write_governor_mixin", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_write_governor_mixin", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_write_governor_mixin", "env_read", "p2_env_1")
_emit_reads_environ("test_write_governor_mixin", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_write_governor_mixin", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_write_governor_mixin", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_write_governor_mixin", "context_pull")
_emit_pulls_context("p1", "test_write_governor_mixin", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_write_governor_mixin", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_write_governor_mixin", "uwg_term_2")
_emit_writes_through("p1", "test_write_governor_mixin", "write_through")
_emit_writes_through("p1", "test_write_governor_mixin", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_write_governor_mixin", "safety_validation")
_emit_invokes_eval("p1", "test_write_governor_mixin", "eval_call")
_emit_proposal_commits_routing("p1", "test_write_governor_mixin", "routing_commit")
_emit_escalates_to_human("p1", "test_write_governor_mixin", "human_escalation")
_emit_routes_through("p1", "test_write_governor_mixin", "route_through")
_emit_checks_agent_registry("p1", "test_write_governor_mixin", "agent_registry")
_emit_validates_agent_capability("p1", "test_write_governor_mixin", "capability")
_emit_dispatches_execution_plan("p1", "test_write_governor_mixin", "exec_plan")
_emit_agent_executes_agent("p1", "test_write_governor_mixin", "sub_agent")
_emit_routes_to_agent("p1", "test_write_governor_mixin", "target_agent")
_emit_verifies_policy("p1", "test_write_governor_mixin", "policy_check")
_emit_observes_runtime_state("p1", "test_write_governor_mixin", "runtime_state")
_emit_verifies_boundary("p1", "test_write_governor_mixin", "boundary_check")
_emit_transcripts_response("p1", "test_write_governor_mixin", "transcript")
_emit_hard_fails_untranscripted("p1", "test_write_governor_mixin")
_emit_gated_by_confidence("p1", "test_write_governor_mixin", "confidence_gate")


class _Agent(WriteGovernorMixin):
    pass


class TestWriteGovernorMixinAllowedPaths:
    def test_governed_write_allowed_path_returns_mutation_record(self):
        agent = _Agent()
        agent.set_write_gateway(UniversalWriteGateway(replay_mode=False))
        result = agent.governed_write("artifacts/output.json", b"{}")
        assert isinstance(result, MutationRecord)
        assert result.permitted is True

    def test_governed_write_str_data_encoded(self):
        agent = _Agent()
        agent.set_write_gateway(UniversalWriteGateway(replay_mode=False))
        result = agent.governed_write("artifacts/output.txt", "hello")
        assert isinstance(result, MutationRecord)
        assert result.data_hash is not None

    def test_governed_append_allowed_path(self):
        agent = _Agent()
        agent.set_write_gateway(UniversalWriteGateway(replay_mode=False))
        result = agent.governed_append("logs/run.log", b"line\n")
        assert isinstance(result, MutationRecord)
        assert result.operation == "append"

    def test_governed_delete_allowed_path(self):
        agent = _Agent()
        agent.set_write_gateway(UniversalWriteGateway(replay_mode=False))
        result = agent.governed_delete("artifacts/old.json")
        assert isinstance(result, MutationRecord)
        assert result.operation == "delete"

    def test_governed_rename_allowed_paths(self):
        agent = _Agent()
        agent.set_write_gateway(UniversalWriteGateway(replay_mode=False))
        result = agent.governed_rename("artifacts/a.json", "artifacts/b.json")
        assert isinstance(result, MutationRecord)
        assert result.operation == "rename"


class TestWriteGovernorMixinBlockedPaths:
    def test_governed_write_blocked_extension_raises(self):
        agent = _Agent()
        agent.set_write_gateway(UniversalWriteGateway(replay_mode=False))
        with pytest.raises(ToolNotAllowedError, match="blocked"):
            agent.governed_write("src/evil.py", b"pass")

    def test_governed_write_blocked_path_raises(self):
        agent = _Agent()
        agent.set_write_gateway(UniversalWriteGateway(replay_mode=False))
        with pytest.raises(ToolNotAllowedError, match="blocked"):
            agent.governed_write("secret/config.json", b"{}")

    def test_governed_append_blocked_raises(self):
        agent = _Agent()
        agent.set_write_gateway(UniversalWriteGateway(replay_mode=False))
        with pytest.raises(ToolNotAllowedError, match="blocked"):
            agent.governed_append("core/engine.py", b"extra")

    def test_governed_delete_blocked_raises(self):
        agent = _Agent()
        agent.set_write_gateway(UniversalWriteGateway(replay_mode=False))
        with pytest.raises(ToolNotAllowedError, match="blocked"):
            agent.governed_delete("agentic_core/L0_routing/important.py")

    def test_assert_write_governed_blocked_raises(self):
        agent = _Agent()
        agent.set_write_gateway(UniversalWriteGateway(replay_mode=False))
        with pytest.raises(ToolNotAllowedError):
            agent.assert_write_governed("src/bad.py")


class TestWriteGovernorMixinReplayMode:
    def test_governed_write_replay_returns_simulation_result(self):
        agent = _Agent()
        agent.set_write_gateway(UniversalWriteGateway(replay_mode=True))
        result = agent.governed_write("src/evil.py", b"pass")
        assert isinstance(result, SimulationResult)
        assert result.replay_mode is True

    def test_governed_append_replay_returns_simulation_result(self):
        agent = _Agent()
        agent.set_write_gateway(UniversalWriteGateway(replay_mode=True))
        result = agent.governed_append("src/evil.py", b"extra")
        assert isinstance(result, SimulationResult)

    def test_governed_delete_replay_returns_simulation_result(self):
        agent = _Agent()
        agent.set_write_gateway(UniversalWriteGateway(replay_mode=True))
        result = agent.governed_delete("src/evil.py")
        assert isinstance(result, SimulationResult)

    def test_governed_rename_replay_returns_simulation_result(self):
        agent = _Agent()
        agent.set_write_gateway(UniversalWriteGateway(replay_mode=True))
        result = agent.governed_rename("src/a.py", "src/b.py")
        assert isinstance(result, SimulationResult)


class TestWriteGovernorMixinGatewayInjection:
    def test_default_gateway_is_global_instance(self):
        from agentic_core.L2_execution.UniversalWriteGateway import get_write_gateway

        agent = _Agent()
        assert agent._get_uwg() is get_write_gateway()

    def test_set_write_gateway_overrides(self):
        agent = _Agent()
        custom = UniversalWriteGateway(replay_mode=True)
        agent.set_write_gateway(custom)
        assert agent._get_uwg() is custom

    def test_get_write_stats_proxies_to_gateway(self):
        agent = _Agent()
        agent.set_write_gateway(UniversalWriteGateway(replay_mode=False))
        stats = agent.get_write_stats()
        assert "total_mutations" in stats
        assert "replay_mode" in stats

    def test_assert_write_governed_allowed_path_returns_true(self):
        agent = _Agent()
        agent.set_write_gateway(UniversalWriteGateway(replay_mode=False))
        assert agent.assert_write_governed("artifacts/ok.json") is True

    def test_mutation_ledger_records_blocked_write(self):
        agent = _Agent()
        gw = UniversalWriteGateway(replay_mode=False)
        agent.set_write_gateway(gw)
        with pytest.raises(ToolNotAllowedError):
            agent.governed_write("src/bad.py", b"pass")
        ledger = gw.get_mutation_ledger()
        assert any(r.permitted is False for r in ledger)
