"""ADG-driven tests for embeddings/tokenization_adapter.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_tokenization_adapter_adg")
_emit_applies_guardrail("p0", "test_tokenization_adapter_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_tokenization_adapter_adg", "policy_binding")
_emit_snapshots_state("p0", "test_tokenization_adapter_adg", "state_snapshot")
emit_replay_key("p0", "test_tokenization_adapter_adg")
emit_determinism_digest("p0", "test_tokenization_adapter_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_tokenization_adapter_adg", "execution_auth")
_emit_validates_capability("p2", "test_tokenization_adapter_adg", "capability_check")
_emit_routes_to_capability("p2", "test_tokenization_adapter_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_tokenization_adapter_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_tokenization_adapter_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_tokenization_adapter_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_tokenization_adapter_adg", "exec_output")
_emit_dispatches_agent("p3", "test_tokenization_adapter_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_tokenization_adapter_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_tokenization_adapter_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_tokenization_adapter_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_tokenization_adapter_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_tokenization_adapter_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_tokenization_adapter_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_tokenization_adapter_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_tokenization_adapter_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_tokenization_adapter_adg", "eval_metric")
_emit_stores_embedding("p4", "test_tokenization_adapter_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_tokenization_adapter_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_tokenization_adapter_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.embeddings.tokenization_adapter import TokenCountAdapter


class TestTokenCountAdapter:
    def test_count_tokens_returns_int(self):
        result = TokenCountAdapter.count_tokens("hello world foo", "gpt-4")
        assert isinstance(result, int)

    def test_count_tokens_empty_string(self):
        result = TokenCountAdapter.count_tokens("", "gpt-4")
        assert result == 0

    def test_count_tokens_single_word(self):
        result = TokenCountAdapter.count_tokens("hello", "gpt-4")
        assert result == 1

    def test_count_tokens_multiple_words(self):
        result = TokenCountAdapter.count_tokens("hello world", "gpt-4")
        assert result == 2

    def test_is_static_method(self):
        assert callable(TokenCountAdapter.count_tokens)
