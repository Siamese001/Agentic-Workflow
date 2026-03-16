"""Tests for StructuredAgentOutput schema enforcement.

Phase 6: apps_* schema emission compliance.
Spec: AgentOutputContract [7], Guarantee #12.
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

_emit_records_execution_trace("p0", "evidence", "test_structured_agent_output")
_emit_applies_guardrail("p0", "test_structured_agent_output", "p0_governance")
_emit_reads_policy_state("p0", "test_structured_agent_output", "policy_binding")
_emit_snapshots_state("p0", "test_structured_agent_output", "state_snapshot")
emit_replay_key("p0", "test_structured_agent_output")
emit_determinism_digest("p0", "test_structured_agent_output")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_structured_agent_output", "execution_auth")
_emit_validates_capability("p2", "test_structured_agent_output", "capability_check")
_emit_routes_to_capability("p2", "test_structured_agent_output", "capability_route")
_emit_writes_via_uwg("p2", "test_structured_agent_output", "uwg_write")
_emit_blocks_direct_write("p2", "test_structured_agent_output", "direct_write_block")
_emit_records_tool_invocation("p2", "test_structured_agent_output", "tool_invocation")
_emit_captures_execution_output("p2", "test_structured_agent_output", "exec_output")
_emit_dispatches_agent("p3", "test_structured_agent_output", "agent_dispatch")
_emit_coordinates_agents("p3", "test_structured_agent_output", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_structured_agent_output", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_structured_agent_output", "healing_outcome")
_emit_escalates_failure("p3", "test_structured_agent_output", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_structured_agent_output", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_structured_agent_output", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_structured_agent_output", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_structured_agent_output", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_structured_agent_output", "eval_metric")
_emit_stores_embedding("p4", "test_structured_agent_output", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_structured_agent_output", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_structured_agent_output", "exec_snapshot_link")

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

from agentic_core.L2_execution.types.structured_agent_output_types import (
    StructuredAgentOutput,
    StructuredOutputViolation,
    ToolRequest,
)


class TestToolRequest:
    def test_valid_tool_request(self):
        r = ToolRequest(tool_name="file_system.read", args={"path": "/tmp/x"})
        assert r.tool_name == "file_system.read"

    def test_empty_tool_name_raises(self):
        with pytest.raises(StructuredOutputViolation, match="tool_name must be non-empty"):
            ToolRequest(tool_name="")

    def test_whitespace_tool_name_raises(self):
        with pytest.raises(StructuredOutputViolation, match="tool_name must be non-empty"):
            ToolRequest(tool_name="   ")

    def test_no_args_defaults_to_empty_dict(self):
        r = ToolRequest(tool_name="some.tool")
        assert r.args == {}


class TestStructuredAgentOutput:
    def test_valid_output(self):
        out = StructuredAgentOutput(
            intent_delta="Create a summary report",
            tool_requests=(ToolRequest(tool_name="file_system.write"),),
            state_diff_proposal={"report_written": True},
        )
        assert out.intent_delta == "Create a summary report"
        assert len(out.tool_requests) == 1
        assert out.state_diff_proposal == {"report_written": True}

    def test_empty_intent_delta_raises(self):
        with pytest.raises(StructuredOutputViolation, match="intent_delta must be a non-empty"):
            StructuredAgentOutput(
                intent_delta="",
                tool_requests=(),
                state_diff_proposal={},
            )

    def test_whitespace_intent_delta_raises(self):
        with pytest.raises(StructuredOutputViolation, match="intent_delta must be a non-empty"):
            StructuredAgentOutput(
                intent_delta="   ",
                tool_requests=(),
                state_diff_proposal={},
            )

    def test_non_tuple_tool_requests_raises(self):
        with pytest.raises(StructuredOutputViolation, match="tool_requests must be a tuple"):
            StructuredAgentOutput(
                intent_delta="valid",
                tool_requests=[ToolRequest(tool_name="x")],  # type: ignore[arg-type]
                state_diff_proposal={},
            )

    def test_non_dict_state_diff_raises(self):
        with pytest.raises(StructuredOutputViolation, match="state_diff_proposal must be a dict"):
            StructuredAgentOutput(
                intent_delta="valid",
                tool_requests=(),
                state_diff_proposal="not a dict",  # type: ignore[arg-type]
            )

    def test_empty_factory(self):
        out = StructuredAgentOutput.empty("No-op pass")
        assert out.intent_delta == "No-op pass"
        assert out.tool_requests == ()
        assert out.state_diff_proposal == {}

    def test_to_dict_shape(self):
        out = StructuredAgentOutput(
            intent_delta="Write report",
            tool_requests=(ToolRequest(tool_name="file_system.write", args={"path": "artifacts/x.json"}),),
            state_diff_proposal={"written": True},
        )
        d = out.to_dict()
        assert d["intent_delta"] == "Write report"
        assert len(d["tool_requests"]) == 1
        assert d["tool_requests"][0]["tool_name"] == "file_system.write"
        assert d["tool_requests"][0]["args"] == {"path": "artifacts/x.json"}
        assert d["state_diff_proposal"] == {"written": True}

    def test_to_dict_keys_present(self):
        out = StructuredAgentOutput.empty("test")
        d = out.to_dict()
        assert "intent_delta" in d
        assert "tool_requests" in d
        assert "state_diff_proposal" in d

    def test_zero_tool_requests_allowed(self):
        out = StructuredAgentOutput(
            intent_delta="Read-only operation",
            tool_requests=(),
            state_diff_proposal={},
        )
        assert out.tool_requests == ()

    def test_multiple_tool_requests(self):
        out = StructuredAgentOutput(
            intent_delta="Multi-step",
            tool_requests=(
                ToolRequest(tool_name="tool.a"),
                ToolRequest(tool_name="tool.b"),
            ),
            state_diff_proposal={"step": 2},
        )
        assert len(out.tool_requests) == 2
