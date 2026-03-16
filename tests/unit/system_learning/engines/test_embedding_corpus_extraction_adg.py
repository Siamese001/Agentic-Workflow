"""ADG-driven tests for system_learning/engines/embedding_corpus_extraction.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_embedding_corpus_extraction_adg")
_emit_applies_guardrail("p0", "test_embedding_corpus_extraction_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_embedding_corpus_extraction_adg", "policy_binding")
_emit_snapshots_state("p0", "test_embedding_corpus_extraction_adg", "state_snapshot")
emit_replay_key("p0", "test_embedding_corpus_extraction_adg")
emit_determinism_digest("p0", "test_embedding_corpus_extraction_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from system_learning.engines.embedding_corpus_extraction import (
    CorpusRecord,
    canonical_record_json,
    compute_content_hash,
)


class TestCorpusRecord:
    def test_creates(self):
        record = CorpusRecord(
            text="test text",
            trace_id="trace-1",
            content_hash="a" * 64,
            namespace="healing_contexts",
        )
        assert record.text == "test text"
        assert record.namespace == "healing_contexts"

    def test_is_frozen(self):
        record = CorpusRecord(
            text="t",
            trace_id="tr",
            content_hash="a" * 64,
            namespace="ns",
        )
        with pytest.raises(Exception):
            record.text = "modified"


class TestCanonicalRecordJson:
    def test_returns_bytes(self):
        result = canonical_record_json({"key": "value"})
        assert isinstance(result, bytes)

    def test_keys_sorted(self):
        result = canonical_record_json({"z": 1, "a": 2})
        decoded = result.decode("ascii")
        assert decoded.index('"a"') < decoded.index('"z"')

    def test_empty_dict(self):
        result = canonical_record_json({})
        assert result == b"{}"


class TestComputeContentHash:
    def test_returns_64_hex(self):
        data = b'{"key":"value"}'
        h = compute_content_hash(data)
        assert isinstance(h, str)
        assert len(h) == 64

    def test_deterministic(self):
        data = b"hello"
        assert compute_content_hash(data) == compute_content_hash(data)
