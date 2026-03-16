"""ADG-driven tests for system_learning/engines/local_embedding_population_service.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_local_embedding_population_service_adg")
_emit_applies_guardrail("p0", "test_local_embedding_population_service_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_local_embedding_population_service_adg", "policy_binding")
_emit_snapshots_state("p0", "test_local_embedding_population_service_adg", "state_snapshot")
emit_replay_key("p0", "test_local_embedding_population_service_adg")
emit_determinism_digest("p0", "test_local_embedding_population_service_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_local_embedding_population_service_adg", "execution_auth")
_emit_validates_capability("p2", "test_local_embedding_population_service_adg", "capability_check")
_emit_routes_to_capability("p2", "test_local_embedding_population_service_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_local_embedding_population_service_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_local_embedding_population_service_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_local_embedding_population_service_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_local_embedding_population_service_adg", "exec_output")
_emit_dispatches_agent("p3", "test_local_embedding_population_service_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_local_embedding_population_service_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_local_embedding_population_service_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_local_embedding_population_service_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_local_embedding_population_service_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_local_embedding_population_service_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_local_embedding_population_service_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_local_embedding_population_service_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_local_embedding_population_service_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_local_embedding_population_service_adg", "eval_metric")
_emit_stores_embedding("p4", "test_local_embedding_population_service_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_local_embedding_population_service_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_local_embedding_population_service_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from system_learning.engines.local_embedding_population_service import (
    extract_embedding_text,
    normalize_l2,
)


class TestExtractEmbeddingText:
    def test_extracts_text_field(self):
        record = {"text": "hello world", "other": 123}
        assert extract_embedding_text(record) == "hello world"

    def test_missing_text_raises(self):
        with pytest.raises(ValueError, match="missing required 'text'"):
            extract_embedding_text({"key": "value"})

    def test_non_string_text_raises(self):
        with pytest.raises(ValueError, match="must be string"):
            extract_embedding_text({"text": 42})


class TestNormalizeL2:
    def test_unit_vector_unchanged(self):
        v = [1.0, 0.0, 0.0]
        result = normalize_l2(v)
        assert abs(result[0] - 1.0) < 1e-6

    def test_returns_unit_norm(self):
        import math
        v = [3.0, 4.0]
        result = normalize_l2(v)
        norm = math.sqrt(sum(x ** 2 for x in result))
        assert abs(norm - 1.0) < 1e-6

    def test_returns_list(self):
        result = normalize_l2([1.0, 2.0, 3.0])
        assert isinstance(result, list)
