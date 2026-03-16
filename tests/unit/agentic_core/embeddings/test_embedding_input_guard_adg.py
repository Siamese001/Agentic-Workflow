"""ADG-driven tests for agentic_core/embeddings/embedding_input_guard.py — fan_in=2.

Contract tests: EmbeddingInputViolation, GuardedText, EmbeddingInputGuard.guard().
"""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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
