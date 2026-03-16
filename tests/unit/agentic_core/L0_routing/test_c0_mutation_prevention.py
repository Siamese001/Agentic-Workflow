"""Addendum 3.2: C0 Context Mutation Prevention tests."""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.context.c0_guard import verify_c0_immutability
from agentic_core.L5_safety.types.hardening_errors import C0MutationViolation
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_c0_mutation_prevention")
_emit_applies_guardrail("p0", "test_c0_mutation_prevention", "p0_governance")
_emit_reads_policy_state("p0", "test_c0_mutation_prevention", "policy_binding")
_emit_snapshots_state("p0", "test_c0_mutation_prevention", "state_snapshot")
emit_replay_key("p0", "test_c0_mutation_prevention")
emit_determinism_digest("p0", "test_c0_mutation_prevention")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class TestVerifyC0Immutability:
    def test_identical_payloads_pass(self):
        payload = {"query": "hello", "context": "ctx"}
        verify_c0_immutability(payload, {"query": "hello", "context": "ctx"})

    def test_empty_payloads_pass(self):
        verify_c0_immutability({}, {})

    def test_mutated_value_raises(self):
        with pytest.raises(C0MutationViolation, match="mutated"):
            verify_c0_immutability(
                {"key": "original"},
                {"key": "modified"},
            )

    def test_added_key_raises(self):
        with pytest.raises(C0MutationViolation, match="mutated"):
            verify_c0_immutability(
                {"key": "value"},
                {"key": "value", "extra": "injected"},
            )

    def test_removed_key_raises(self):
        with pytest.raises(C0MutationViolation, match="mutated"):
            verify_c0_immutability(
                {"key": "value", "other": "data"},
                {"key": "value"},
            )

    def test_nested_mutation_raises(self):
        with pytest.raises(C0MutationViolation, match="mutated"):
            verify_c0_immutability(
                {"nested": {"a": 1}},
                {"nested": {"a": 2}},
            )

    def test_negative_same_content_never_raises(self):
        """Negative control: same content dict must never raise."""
        payload = {"query": "test", "score": 0.9, "tags": ["a", "b"]}
        raised = False
        try:
            verify_c0_immutability(payload, dict(payload))
        except C0MutationViolation:  # guardian: allow-silent-swallower
            raised = True
        assert not raised
