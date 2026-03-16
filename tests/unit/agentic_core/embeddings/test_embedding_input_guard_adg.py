"""ADG-driven tests for agentic_core/embeddings/embedding_input_guard.py — fan_in=2.

Contract tests: EmbeddingInputViolation, GuardedText, EmbeddingInputGuard.guard().
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

_emit_records_execution_trace("p0", "evidence", "test_embedding_input_guard_adg")
_emit_applies_guardrail("p0", "test_embedding_input_guard_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_embedding_input_guard_adg", "policy_binding")
_emit_snapshots_state("p0", "test_embedding_input_guard_adg", "state_snapshot")
emit_replay_key("p0", "test_embedding_input_guard_adg")
emit_determinism_digest("p0", "test_embedding_input_guard_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_embedding_input_guard_adg", "execution_auth")
_emit_validates_capability("p2", "test_embedding_input_guard_adg", "capability_check")
_emit_routes_to_capability("p2", "test_embedding_input_guard_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_embedding_input_guard_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_embedding_input_guard_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_embedding_input_guard_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_embedding_input_guard_adg", "exec_output")
_emit_dispatches_agent("p3", "test_embedding_input_guard_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_embedding_input_guard_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_embedding_input_guard_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_embedding_input_guard_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_embedding_input_guard_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_embedding_input_guard_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_embedding_input_guard_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_embedding_input_guard_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_embedding_input_guard_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_embedding_input_guard_adg", "eval_metric")
_emit_stores_embedding("p4", "test_embedding_input_guard_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_embedding_input_guard_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_embedding_input_guard_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.embeddings.embedding_input_guard import (
    EmbeddingInputGuard,
    EmbeddingInputViolation,
    GuardedText,
)


class TestEmbeddingInputViolation:
    def test_is_value_error(self):
        assert issubclass(EmbeddingInputViolation, ValueError)

    def test_raises_with_message(self):
        with pytest.raises(EmbeddingInputViolation, match="not allowed"):
            raise EmbeddingInputViolation("Field 'x' is not allowed for embedding.")


class TestGuardedText:
    def test_is_frozen_dataclass(self):
        g = GuardedText(redacted_text="hello", hash="abc123", size=5)
        with pytest.raises(Exception):
            g.redacted_text = "mutate"  # frozen should raise

    def test_creates_valid(self):
        g = GuardedText(redacted_text="hello", hash="abc123", size=5)
        assert g.redacted_text == "hello"
        assert g.hash == "abc123"
        assert g.size == 5


class TestEmbeddingInputGuardAllowedFields:
    def test_allowed_fields_nonempty(self):
        assert len(EmbeddingInputGuard.ALLOWED_FIELDS) > 0

    def test_known_allowed_field_present(self):
        assert "u0_user_prompt" in EmbeddingInputGuard.ALLOWED_FIELDS

    def test_rag_query_allowed(self):
        assert "rag_query" in EmbeddingInputGuard.ALLOWED_FIELDS

    def test_redaction_patterns_nonempty(self):
        assert len(EmbeddingInputGuard.REDACTION_PATTERNS) > 0


class TestEmbeddingInputGuardGuard:
    def test_rejects_unknown_field(self):
        with pytest.raises(EmbeddingInputViolation):
            EmbeddingInputGuard.guard("some text", "secret_field")

    def test_accepts_allowed_field(self):
        result = EmbeddingInputGuard.guard("hello world", "u0_user_prompt")
        assert isinstance(result, GuardedText)

    def test_returns_guarded_text_with_hash(self):
        result = EmbeddingInputGuard.guard("test query", "rag_query")
        assert len(result.hash) == 64  # sha256 hex

    def test_size_matches_redacted_length(self):
        text = "hello world"
        result = EmbeddingInputGuard.guard(text, "rag_query")
        assert result.size == len(result.redacted_text)

    def test_redacts_api_key(self):
        text = "sk-abcdefghijklmnopqrstuvwx"
        result = EmbeddingInputGuard.guard(text, "rag_query")
        assert "sk-" not in result.redacted_text
        assert "[REDACTED]" in result.redacted_text

    def test_redacts_email(self):
        text = "contact user@example.com for help"
        result = EmbeddingInputGuard.guard(text, "rag_query")
        assert "user@example.com" not in result.redacted_text

    def test_redacts_bearer_token(self):
        text = "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9"
        result = EmbeddingInputGuard.guard(text, "rag_query")
        assert "eyJhbGciOiJIUzI1NiJ9" not in result.redacted_text

    def test_clean_text_not_modified(self):
        text = "The quick brown fox"
        result = EmbeddingInputGuard.guard(text, "u0_user_prompt")
        assert result.redacted_text == text

    def test_deterministic_hash(self):
        r1 = EmbeddingInputGuard.guard("same text", "rag_query")
        r2 = EmbeddingInputGuard.guard("same text", "rag_query")
        assert r1.hash == r2.hash
