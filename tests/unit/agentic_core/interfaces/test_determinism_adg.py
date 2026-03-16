"""ADG-driven tests for interfaces/determinism.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_determinism_adg")
_emit_applies_guardrail("p0", "test_determinism_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_determinism_adg", "policy_binding")
_emit_snapshots_state("p0", "test_determinism_adg", "state_snapshot")
emit_replay_key("p0", "test_determinism_adg")
emit_determinism_digest("p0", "test_determinism_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.interfaces.determinism import DETERMINISM_EXCLUDED_FIELDS


class TestDeterminismExcludedFields:
    def test_is_frozenset(self):
        assert isinstance(DETERMINISM_EXCLUDED_FIELDS, frozenset)

    def test_contains_timestamp(self):
        assert "timestamp" in DETERMINISM_EXCLUDED_FIELDS

    def test_contains_duration_ms(self):
        assert "duration_ms" in DETERMINISM_EXCLUDED_FIELDS

    def test_contains_trace_id(self):
        assert "trace_id" in DETERMINISM_EXCLUDED_FIELDS


class TestCanonicalBytes:
    def test_importable(self):
        from agentic_core.interfaces.determinism import canonical_bytes
        assert callable(canonical_bytes)

    def test_returns_bytes(self):
        from agentic_core.interfaces.determinism import canonical_bytes
        result = canonical_bytes({"key": "value"})
        assert isinstance(result, bytes)


class TestCanonicalHash:
    def test_importable(self):
        from agentic_core.interfaces.determinism import canonical_hash
        assert callable(canonical_hash)

    def test_returns_string(self):
        from agentic_core.interfaces.determinism import canonical_hash
        result = canonical_hash({"key": "value"})
        assert isinstance(result, str)
        assert len(result) == 64  # sha256 hex
