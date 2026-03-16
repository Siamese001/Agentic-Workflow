"""ADG-driven tests for system_learning/engines/retrieval_profile_invariant_checker.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_retrieval_profile_invariant_checker_adg")
_emit_applies_guardrail("p0", "test_retrieval_profile_invariant_checker_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_retrieval_profile_invariant_checker_adg", "policy_binding")
_emit_snapshots_state("p0", "test_retrieval_profile_invariant_checker_adg", "state_snapshot")
emit_replay_key("p0", "test_retrieval_profile_invariant_checker_adg")
emit_determinism_digest("p0", "test_retrieval_profile_invariant_checker_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from system_learning.engines.retrieval_profile_invariant_checker import (
    InvariantViolation,
    RetrievalProfileInvariantChecker,
)


class TestInvariantViolation:
    def test_creates(self):
        v = InvariantViolation(
            field="top_k",
            expected="in [1, 200]",
            actual="300",
            message="top_k out of bounds",
        )
        assert v.field == "top_k"
        assert v.message == "top_k out of bounds"

    def test_is_frozen(self):
        v = InvariantViolation(field="f", expected="e", actual="a", message="m")
        with pytest.raises(Exception):
            v.field = "modified"


class TestRetrievalProfileInvariantChecker:
    def test_creates_with_defaults(self):
        checker = RetrievalProfileInvariantChecker()
        assert checker.min_top_k == 1
        assert checker.max_top_k == 200

    def test_creates_with_custom_bounds(self):
        checker = RetrievalProfileInvariantChecker(min_top_k=5, max_top_k=50)
        assert checker.min_top_k == 5
        assert checker.max_top_k == 50

    def test_has_validate(self):
        assert hasattr(RetrievalProfileInvariantChecker, "validate")
