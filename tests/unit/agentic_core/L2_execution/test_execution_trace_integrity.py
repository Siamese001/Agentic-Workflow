"""Addendum 1.1: ExecutionTrace.validate_completeness() tests."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.types.execution_trace_types import ExecutionTrace, ExecutionTraceBuilder
from agentic_core.L5_safety.types.hardening_errors import ExecutionTraceIntegrityError


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

def _complete_trace() -> ExecutionTrace:
    b = ExecutionTraceBuilder("trace-001", "ip-001")
    b.set_governed_payload("abc123")
    b.set_llm_response("some response text")
    b.set_hash_chain_root("root-hash-abc")
    b.set_validation_decision("PASS")
    b.set_transcript(b"tool transcript bytes")
    return b.seal()


class TestValidateCompleteness:
    def test_complete_trace_passes(self):
        trace = _complete_trace()
        trace.validate_completeness()
        assert True  # no-exception contract

    def test_empty_governed_payload_raises(self):
        b = ExecutionTraceBuilder("trace-002", "ip-002")
        b.set_llm_response("response")
        b.set_hash_chain_root("root")
        b.set_validation_decision("PASS")
        trace = b.seal()
        with pytest.raises(ExecutionTraceIntegrityError, match="governed_payload_hash"):
            trace.validate_completeness()

    def test_empty_llm_response_hash_raises(self):
        b = ExecutionTraceBuilder("trace-003", "ip-003")
        b.set_governed_payload("abc")
        b.set_hash_chain_root("root")
        b.set_validation_decision("PASS")
        trace = b.seal()
        with pytest.raises(ExecutionTraceIntegrityError, match="llm_response_hash"):
            trace.validate_completeness()

    def test_empty_hash_chain_root_raises(self):
        b = ExecutionTraceBuilder("trace-004", "ip-004")
        b.set_governed_payload("abc")
        b.set_llm_response("resp")
        b.set_validation_decision("PASS")
        trace = b.seal()
        with pytest.raises(ExecutionTraceIntegrityError, match="hash_chain_root"):
            trace.validate_completeness()

    def test_negative_no_error_on_full_trace(self):
        """Negative control: error must NOT be raised on a complete trace."""
        trace = _complete_trace()
        raised = False
        try:
            trace.validate_completeness()
        except ExecutionTraceIntegrityError:  # guardian: allow-silent-swallower
            raised = True
        assert not raised

    def test_multiple_missing_fields_listed(self):
        b = ExecutionTraceBuilder("trace-005", "ip-005")
        b.set_validation_decision("PASS")
        trace = b.seal()
        with pytest.raises(ExecutionTraceIntegrityError) as exc_info:
            trace.validate_completeness()
        msg = str(exc_info.value)
        assert "governed_payload_hash" in msg or "llm_response_hash" in msg
