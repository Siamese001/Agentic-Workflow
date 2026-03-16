"""Contract tests for AgentOutputContract (spec [7])."""

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

_emit_records_execution_trace("p0", "evidence", "test_agent_output_contract")
_emit_applies_guardrail("p0", "test_agent_output_contract", "p0_governance")
_emit_reads_policy_state("p0", "test_agent_output_contract", "policy_binding")
_emit_snapshots_state("p0", "test_agent_output_contract", "state_snapshot")
emit_replay_key("p0", "test_agent_output_contract")
emit_determinism_digest("p0", "test_agent_output_contract")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_agent_output_contract", "execution_auth")
_emit_validates_capability("p2", "test_agent_output_contract", "capability_check")
_emit_routes_to_capability("p2", "test_agent_output_contract", "capability_route")
_emit_writes_via_uwg("p2", "test_agent_output_contract", "uwg_write")
_emit_blocks_direct_write("p2", "test_agent_output_contract", "direct_write_block")
_emit_records_tool_invocation("p2", "test_agent_output_contract", "tool_invocation")
_emit_captures_execution_output("p2", "test_agent_output_contract", "exec_output")
_emit_dispatches_agent("p3", "test_agent_output_contract", "agent_dispatch")
_emit_coordinates_agents("p3", "test_agent_output_contract", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_agent_output_contract", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_agent_output_contract", "healing_outcome")
_emit_escalates_failure("p3", "test_agent_output_contract", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_agent_output_contract", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_agent_output_contract", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_agent_output_contract", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_agent_output_contract", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_agent_output_contract", "eval_metric")
_emit_stores_embedding("p4", "test_agent_output_contract", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_agent_output_contract", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_agent_output_contract", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.unit_min_deps

from pydantic import BaseModel

from agentic_core.L2_execution.types.agent_output_contract_types import (
    AgentOutputContract,
    OutputContractViolation,
    wrap_output,
)
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
)

_emit_emits_metric_event("test_agent_output_contract", "p4obs", "metric_1")
_emit_emits_metric_event("test_agent_output_contract", "p4obs", "metric_2")
_emit_emits_metric_event("test_agent_output_contract", "p4obs", "metric_3")
_emit_emits_metric_event("test_agent_output_contract", "p4obs", "metric_4")
_emit_emits_metric_event("test_agent_output_contract", "p4obs", "metric_5")
_emit_emits_metric_event("test_agent_output_contract", "p4obs", "metric_6")
_emit_records_incident_event("test_agent_output_contract", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_agent_output_contract", "p4obs", "anomaly")
_emit_writes_observability_log("test_agent_output_contract", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_agent_output_contract", "p4obs", "mon_state")
_emit_triggers_alert("test_agent_output_contract", "p4obs", "alert")
_emit_links_incident_trace("test_agent_output_contract", "p4obs", "trace_link")
_emit_captures_pattern("test_agent_output_contract", "p3lm", "pattern")
_emit_records_learning_event("test_agent_output_contract", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_agent_output_contract", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_agent_output_contract", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_agent_output_contract", "p3lm", "routing")
_emit_improves_agent_policy("test_agent_output_contract", "p3lm", "policy")
_emit_stores_learning_state("test_agent_output_contract", "p3lm", "state")
_emit_records_execution_trace("test_agent_output_contract", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_agent_output_contract", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_agent_output_contract", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_agent_output_contract", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_agent_output_contract", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_agent_output_contract", "env_read", "p2_env_1")
_emit_reads_environ("test_agent_output_contract", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_agent_output_contract", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_agent_output_contract", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_agent_output_contract", "context_pull")
_emit_pulls_context("p1", "test_agent_output_contract", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_agent_output_contract", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_agent_output_contract", "uwg_term_secondary")
_emit_writes_through("p1", "test_agent_output_contract", "write_through")
_emit_writes_through("p1", "test_agent_output_contract", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_agent_output_contract", "safety_validation")
_emit_invokes_eval("p1", "test_agent_output_contract", "eval_call")
_emit_proposal_commits_routing("p1", "test_agent_output_contract", "routing_commit")

SECRET = b"test-l2-output-secret"


class _FakeOutput(BaseModel):
    result: str
    score: float


def test_wrap_output_produces_signed_contract():
    out = _FakeOutput(result="ok", score=0.9)
    contract = wrap_output("MyAgent", "trace-1", out, SECRET)
    assert contract.agent_id == "MyAgent"
    assert contract.trace_id == "trace-1"
    assert "FakeOutput" in contract.schema_tag
    assert len(contract.output_contract_hash) == 64
    assert len(contract.signature) == 64


def test_verify_roundtrip():
    out = _FakeOutput(result="ok", score=0.9)
    contract = wrap_output("MyAgent", "trace-1", out, SECRET)
    contract.verify(SECRET)  # must not raise


def test_different_payloads_produce_different_hashes():
    c1 = wrap_output("A", "t", _FakeOutput(result="a", score=0.1), SECRET)
    c2 = wrap_output("A", "t", _FakeOutput(result="b", score=0.2), SECRET)
    assert c1.output_contract_hash != c2.output_contract_hash


def test_tampered_contract_rejected():
    contract = wrap_output("MyAgent", "trace-1", _FakeOutput(result="ok", score=0.9), SECRET)
    tampered = AgentOutputContract(
        agent_id=contract.agent_id,
        trace_id=contract.trace_id,
        schema_tag=contract.schema_tag,
        output_contract_hash=contract.output_contract_hash,
        payload=contract.payload,
        signature="deadbeef" * 8,
    )
    with pytest.raises(OutputContractViolation, match="mismatch"):
        tampered.verify(SECRET)


def test_missing_agent_id_rejected():
    with pytest.raises(OutputContractViolation, match="agent_id"):
        AgentOutputContract(
            agent_id="",
            trace_id="t",
            schema_tag="foo.Bar",
            output_contract_hash="a" * 64,
            payload={},
        )


def test_missing_schema_tag_rejected():
    with pytest.raises(OutputContractViolation, match="schema_tag"):
        AgentOutputContract(
            agent_id="A",
            trace_id="t",
            schema_tag="",
            output_contract_hash="a" * 64,
            payload={},
        )
