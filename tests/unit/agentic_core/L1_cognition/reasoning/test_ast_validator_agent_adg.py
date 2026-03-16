"""ADG-driven tests for L1 ASTValidatorAgent — fan_in=1."""
from __future__ import annotations

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

_emit_records_execution_trace("p0", "evidence", "test_ast_validator_agent_adg")
_emit_applies_guardrail("p0", "test_ast_validator_agent_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_ast_validator_agent_adg", "policy_binding")
_emit_snapshots_state("p0", "test_ast_validator_agent_adg", "state_snapshot")
emit_replay_key("p0", "test_ast_validator_agent_adg")
emit_determinism_digest("p0", "test_ast_validator_agent_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_ast_validator_agent_adg", "execution_auth")
_emit_validates_capability("p2", "test_ast_validator_agent_adg", "capability_check")
_emit_routes_to_capability("p2", "test_ast_validator_agent_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_ast_validator_agent_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_ast_validator_agent_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_ast_validator_agent_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_ast_validator_agent_adg", "exec_output")
_emit_dispatches_agent("p3", "test_ast_validator_agent_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_ast_validator_agent_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_ast_validator_agent_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_ast_validator_agent_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_ast_validator_agent_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_ast_validator_agent_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_ast_validator_agent_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_ast_validator_agent_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_ast_validator_agent_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_ast_validator_agent_adg", "eval_metric")
_emit_stores_embedding("p4", "test_ast_validator_agent_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_ast_validator_agent_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_ast_validator_agent_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.reasoning.ASTValidatorAgent import (
    ASTValidatorAgent,
    ASTValidatorBase,
)


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
