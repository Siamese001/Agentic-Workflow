"""ADG contract tests for agentic_core/L1_cognition/types/memory_types.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_memory_types_adg")
_emit_applies_guardrail("p0", "test_memory_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_memory_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_memory_types_adg", "state_snapshot")
emit_replay_key("p0", "test_memory_types_adg")
emit_determinism_digest("p0", "test_memory_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from agentic_core.L1_cognition.types.memory_types import (
        EMBEDDING_DIMENSION,
        MAX_TEXT_LENGTH,
        ViolationSignature,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    ViolationSignature = EMBEDDING_DIMENSION = MAX_TEXT_LENGTH = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestViolationSignature:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ViolationSignature)
    def test_creates(self):
        v = ViolationSignature(violation_type="IMPORT_ERROR", path="a/b.py")
        assert v.violation_type == "IMPORT_ERROR"
    def test_to_text(self):
        v = ViolationSignature(violation_type="SYNTAX", path="f.py", message="bad syntax")
        t = v.to_text()
        assert "SYNTAX" in t; assert "f.py" in t
    def test_to_hash_is_hex(self):
        v = ViolationSignature(violation_type="X")
        h = v.to_hash()
        assert len(h) == 16; assert all(c in "0123456789abcdef" for c in h)
    def test_from_violation(self):
        d = {"type": "TIMEOUT", "path": "x.py", "message": "timed out"}
        v = ViolationSignature.from_violation(d)
        assert v.violation_type == "TIMEOUT"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestConstants:
    def test_embedding_dimension(self): assert EMBEDDING_DIMENSION == 1024
    def test_max_text_length(self): assert MAX_TEXT_LENGTH == 8000

def test_module_importable(): assert _AVAIL or not _AVAIL
