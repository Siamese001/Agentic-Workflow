"""Tests for PTC ToolCall and ToolResult contract enforcement.

Phase 4: PTC ToolTranscript STDOUT-only verification.
Spec: Contract [3] PTC Tool Contracts, L2 [STDOUT RULE], Guarantee #24.
"""

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

_emit_records_execution_trace("p0", "evidence", "test_ptc_tool_contracts")
_emit_applies_guardrail("p0", "test_ptc_tool_contracts", "p0_governance")
_emit_reads_policy_state("p0", "test_ptc_tool_contracts", "policy_binding")
_emit_snapshots_state("p0", "test_ptc_tool_contracts", "state_snapshot")
emit_replay_key("p0", "test_ptc_tool_contracts")
emit_determinism_digest("p0", "test_ptc_tool_contracts")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_ptc_tool_contracts", "execution_auth")
_emit_validates_capability("p2", "test_ptc_tool_contracts", "capability_check")
_emit_routes_to_capability("p2", "test_ptc_tool_contracts", "capability_route")
_emit_writes_via_uwg("p2", "test_ptc_tool_contracts", "uwg_write")
_emit_blocks_direct_write("p2", "test_ptc_tool_contracts", "direct_write_block")
_emit_records_tool_invocation("p2", "test_ptc_tool_contracts", "tool_invocation")
_emit_captures_execution_output("p2", "test_ptc_tool_contracts", "exec_output")
_emit_dispatches_agent("p3", "test_ptc_tool_contracts", "agent_dispatch")
_emit_coordinates_agents("p3", "test_ptc_tool_contracts", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_ptc_tool_contracts", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_ptc_tool_contracts", "healing_outcome")
_emit_escalates_failure("p3", "test_ptc_tool_contracts", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_ptc_tool_contracts", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_ptc_tool_contracts", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_ptc_tool_contracts", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_ptc_tool_contracts", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_ptc_tool_contracts", "eval_metric")
_emit_stores_embedding("p4", "test_ptc_tool_contracts", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_ptc_tool_contracts", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_ptc_tool_contracts", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.types.ptc_tool_contracts_types import (
    ToolCall,
    ToolContractViolation,
    ToolResult,
)


class TestToolCall:
    def test_valid_tool_call(self):
        tc = ToolCall(id="call-001", tool_name="file_system.read", args={"path": "/tmp/x"})
        assert tc.id == "call-001"
        assert tc.tool_name == "file_system.read"

    def test_empty_id_raises(self):
        with pytest.raises(ToolContractViolation, match="id must be non-empty"):
            ToolCall(id="", tool_name="file_system.read")

    def test_empty_tool_name_raises(self):
        with pytest.raises(ToolContractViolation, match="tool_name must be non-empty"):
            ToolCall(id="call-001", tool_name="")


class TestToolResult:
    def test_exit_code_zero_succeeds(self):
        r = ToolResult(exit_code=0, stdout=b"output")
        assert r.exit_code == 0
        assert r.stdout == b"output"

    def test_exit_code_one_succeeds(self):
        r = ToolResult(exit_code=1, stdout=b"error output")
        assert r.exit_code == 1

    def test_exit_code_two_raises(self):
        with pytest.raises(ToolContractViolation, match="exit_code must be 0 or 1"):
            ToolResult(exit_code=2, stdout=b"")

    def test_exit_code_negative_raises(self):
        with pytest.raises(ToolContractViolation, match="exit_code must be 0 or 1"):
            ToolResult(exit_code=-1, stdout=b"")

    def test_exit_code_255_raises(self):
        with pytest.raises(ToolContractViolation, match="exit_code must be 0 or 1"):
            ToolResult(exit_code=255, stdout=b"")

    def test_stdout_within_cap_succeeds(self):
        r = ToolResult(exit_code=0, stdout=b"hello", stdout_bytes_cap=100)
        assert len(r.stdout) <= 100

    def test_stdout_over_cap_raises(self):
        with pytest.raises(ToolContractViolation, match="exceeds cap"):
            ToolResult(exit_code=0, stdout=b"x" * 200, stdout_bytes_cap=100)

    def test_stdout_exact_cap_succeeds(self):
        r = ToolResult(exit_code=0, stdout=b"x" * 100, stdout_bytes_cap=100)
        assert len(r.stdout) == 100

    def test_zero_cap_disables_cap_check(self):
        # cap=0 means no cap enforced
        r = ToolResult(exit_code=0, stdout=b"x" * 10000, stdout_bytes_cap=0)
        assert len(r.stdout) == 10000


class TestToolResultFromBudgetEnforcer:
    def test_valid_construction(self):
        r = ToolResult.from_budget_enforcer(exit_code=0, stdout_bytes=b"output", stdout_bytes_cap=1024)
        assert r.exit_code == 0
        assert r.stdout == b"output"

    def test_invalid_exit_code_raises(self):
        with pytest.raises(ToolContractViolation, match="exit_code must be 0 or 1"):
            ToolResult.from_budget_enforcer(exit_code=2, stdout_bytes=b"", stdout_bytes_cap=1024)

    def test_stdout_over_cap_raises(self):
        with pytest.raises(ToolContractViolation, match="exceeds cap"):
            ToolResult.from_budget_enforcer(exit_code=0, stdout_bytes=b"x" * 500, stdout_bytes_cap=10)

    def test_stdout_at_cap_succeeds(self):
        r = ToolResult.from_budget_enforcer(exit_code=0, stdout_bytes=b"x" * 10, stdout_bytes_cap=10)
        assert len(r.stdout) == 10
