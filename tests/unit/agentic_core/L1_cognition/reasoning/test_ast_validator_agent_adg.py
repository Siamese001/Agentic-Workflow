"""ADG-driven tests for L1 ASTValidatorAgent — fan_in=1."""
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_ast_validator_agent_adg")
# REMOVED: _emit_applies_guardrail("p0", "test_ast_validator_agent_adg", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_ast_validator_agent_adg", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_ast_validator_agent_adg", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_ast_validator_agent_adg")
# REMOVED: emit_determinism_digest("p0", "test_ast_validator_agent_adg")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_ast_validator_agent_adg", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_ast_validator_agent_adg", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_ast_validator_agent_adg", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_ast_validator_agent_adg", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_ast_validator_agent_adg", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_ast_validator_agent_adg", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_ast_validator_agent_adg", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_ast_validator_agent_adg", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_ast_validator_agent_adg", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_ast_validator_agent_adg", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_ast_validator_agent_adg", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_ast_validator_agent_adg", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_ast_validator_agent_adg", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_ast_validator_agent_adg", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_ast_validator_agent_adg", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_ast_validator_agent_adg", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_ast_validator_agent_adg", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_ast_validator_agent_adg", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_ast_validator_agent_adg", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_ast_validator_agent_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.reasoning.ASTValidatorAgent import (
    ASTValidatorAgent,
    ASTValidatorBase,
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

# REMOVED: _emit_emits_metric_event("test_ast_validator_agent_adg", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_ast_validator_agent_adg", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_ast_validator_agent_adg", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_ast_validator_agent_adg", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_ast_validator_agent_adg", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_ast_validator_agent_adg", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_ast_validator_agent_adg", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_ast_validator_agent_adg", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_ast_validator_agent_adg", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_ast_validator_agent_adg", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_ast_validator_agent_adg", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_ast_validator_agent_adg", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_ast_validator_agent_adg", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_ast_validator_agent_adg", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_ast_validator_agent_adg", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_ast_validator_agent_adg", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_ast_validator_agent_adg", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_ast_validator_agent_adg", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_ast_validator_agent_adg", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_ast_validator_agent_adg", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_ast_validator_agent_adg", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_ast_validator_agent_adg", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_ast_validator_agent_adg", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_ast_validator_agent_adg", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_ast_validator_agent_adg", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_ast_validator_agent_adg", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_ast_validator_agent_adg", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_ast_validator_agent_adg", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_ast_validator_agent_adg", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_ast_validator_agent_adg", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_ast_validator_agent_adg", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_ast_validator_agent_adg", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_ast_validator_agent_adg", "write_through")
# REMOVED: _emit_writes_through("p1", "test_ast_validator_agent_adg", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_ast_validator_agent_adg", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_ast_validator_agent_adg", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_ast_validator_agent_adg", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_ast_validator_agent_adg", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_ast_validator_agent_adg", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_ast_validator_agent_adg", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_ast_validator_agent_adg", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_ast_validator_agent_adg", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_ast_validator_agent_adg", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_ast_validator_agent_adg", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_ast_validator_agent_adg", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_ast_validator_agent_adg", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_ast_validator_agent_adg", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_ast_validator_agent_adg", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_ast_validator_agent_adg")
# REMOVED: _emit_gated_by_confidence("p1", "test_ast_validator_agent_adg", "confidence_gate")


class TestASTValidatorBase:
    def test_creates(self):
        base = ASTValidatorBase()
        assert base is not None

    def test_violations_start_empty(self):
        base = ASTValidatorBase()
        assert base.violations == []

    def test_in_type_checking_false(self):
        base = ASTValidatorBase()
        assert base.in_type_checking is False

    def test_report_adds_violation(self):
        import ast
        base = ASTValidatorBase()
        node = ast.parse("pass").body[0]
        base.report("test violation", node)
        assert len(base.violations) == 1
        assert base.violations[0]["message"] == "test violation"


class TestASTValidatorAgentInit:
    def test_creates(self):
        agent = ASTValidatorAgent()
        assert agent is not None

    def test_key_debugger_is_3(self):
        agent = ASTValidatorAgent()
        assert agent.KEY_DEBUGGER == 3

    def test_key_empty_except_is_4(self):
        agent = ASTValidatorAgent()
        assert agent.KEY_EMPTY_EXCEPT == 4

    def test_key_bare_except_is_5(self):
        agent = ASTValidatorAgent()
        assert agent.KEY_BARE_EXCEPT == 5

    def test_key_eval_exec_is_6(self):
        agent = ASTValidatorAgent()
        assert agent.KEY_EVAL_EXEC == 6

    def test_key_dangerous_builtins_is_42(self):
        agent = ASTValidatorAgent()
        assert agent.KEY_DANGEROUS_BUILTINS == 42

    def test_dangerous_builtins_set(self):
        agent = ASTValidatorAgent()
        assert "eval" not in agent.DANGEROUS_BUILTINS
        assert "globals" in agent.DANGEROUS_BUILTINS

    def test_forbidden_calls_set(self):
        agent = ASTValidatorAgent()
        assert "eval" in agent.FORBIDDEN_CALLS
        assert "exec" in agent.FORBIDDEN_CALLS

    def test_has_heal_repository(self):
        assert hasattr(ASTValidatorAgent, "heal_repository")


class TestASTValidatorAgentAPI:
    def setup_method(self):
        self.agent = ASTValidatorAgent()

    def test_has_heal(self):
        assert hasattr(self.agent, "heal")

    def test_has_heal_repository(self):
        assert hasattr(self.agent, "heal_repository")

    def test_base_violations_list(self):
        base = ASTValidatorBase()
        assert isinstance(base.violations, list)
