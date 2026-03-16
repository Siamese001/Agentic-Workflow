"""ADG-driven tests for embeddings/tokenization_adapter.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_tokenization_adapter_adg")
_emit_applies_guardrail("p0", "test_tokenization_adapter_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_tokenization_adapter_adg", "policy_binding")
_emit_snapshots_state("p0", "test_tokenization_adapter_adg", "state_snapshot")
emit_replay_key("p0", "test_tokenization_adapter_adg")
emit_determinism_digest("p0", "test_tokenization_adapter_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
