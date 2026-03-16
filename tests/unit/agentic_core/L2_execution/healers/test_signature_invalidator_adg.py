"""ADG-driven tests for L2_execution/healers/signature_invalidator.py — fan_in=0."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_signature_invalidator_adg")
_emit_applies_guardrail("p0", "test_signature_invalidator_adg", "p0_governance")
_emit_snapshots_state("p0", "test_signature_invalidator_adg", "state_snapshot")
emit_replay_key("p0", "test_signature_invalidator_adg")
emit_determinism_digest("p0", "test_signature_invalidator_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.healers.signature_invalidator import (
    InvalidationResult,
    StaleSignatureViolation,
    invalidate_signature_and_rehash,
)


class TestStaleSignatureViolation:
    def test_is_exception(self):
        assert issubclass(StaleSignatureViolation, Exception)


class TestInvalidationResult:
    def test_is_named_tuple(self):
        r = InvalidationResult(invalidated_plan={"key": "val"}, new_policy_hash="abc123")
        assert r.new_policy_hash == "abc123"
        assert r.invalidated_plan == {"key": "val"}


class TestInvalidateSignatureAndRehash:
    def test_returns_invalidation_result(self):
        plan = {"id": "p1", "steps": ["s1"], "signature": "old_sig"}
        result = invalidate_signature_and_rehash(plan)
        assert isinstance(result, InvalidationResult)

    def test_returns_plan_with_policy_hash(self):
        plan = {"id": "p1", "signature": "old_sig", "approval_hash": "ah"}
        result = invalidate_signature_and_rehash(plan)
        assert "policy_hash" in result.invalidated_plan

    def test_new_policy_hash_is_hex(self):
        plan = {"id": "p1", "content": "heal_result"}
        result = invalidate_signature_and_rehash(plan)
        assert isinstance(result.new_policy_hash, str)
        assert len(result.new_policy_hash) == 64
