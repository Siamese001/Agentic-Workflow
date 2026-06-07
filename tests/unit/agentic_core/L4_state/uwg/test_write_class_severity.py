"""Unit tests for ``agentic_core.L4_state.uwg.write_class_severity``.

Plan: ``docs/archive/windsurf/legacy-tree/plans/routing-decision-process-enhancement-9c7e4d.md`` W11.
"""

from __future__ import annotations

import pytest

from agentic_core.L4_state.uwg.write_class_severity import (
    AliasAtomicityViolationError,
    AliasManifest,
    InvalidationCoverageGate,
    InvalidationProposal,
    WriteClass,
    alias_swap_atomicity_proof,
    classify_write,
    requires_second_judge,
)


def test_classify_schema_change() -> None:
    assert classify_write(op="ALTER TABLE", target="users") == WriteClass.SCHEMA_CHANGE
    assert classify_write(op="DDL", target="schema_v3") == WriteClass.SCHEMA_CHANGE


def test_classify_policy_update() -> None:
    assert classify_write(op="promote_policy", target="policy_v2") == WriteClass.POLICY_UPDATE
    assert classify_write(op="upsert", target="policy_snapshot/v3") == WriteClass.POLICY_UPDATE


def test_classify_irreversible() -> None:
    assert classify_write(op="delete", target="rows") == WriteClass.IRREVERSIBLE
    assert classify_write(op="api_call:send_email", target="user@x") == WriteClass.IRREVERSIBLE


def test_classify_reversible_default() -> None:
    assert classify_write(op="upsert", target="profile") == WriteClass.REVERSIBLE


def test_requires_second_judge_only_on_heavy() -> None:
    assert requires_second_judge(WriteClass.REVERSIBLE) is False
    assert requires_second_judge(WriteClass.SCHEMA_CHANGE) is True
    assert requires_second_judge(WriteClass.IRREVERSIBLE) is True
    assert requires_second_judge(WriteClass.POLICY_UPDATE) is True


def test_invalidation_gate_zero_when_empty() -> None:
    gate = InvalidationCoverageGate()
    assert gate.miss_rate() == 0.0


def test_invalidation_gate_covered_reads_no_miss() -> None:
    gate = InvalidationCoverageGate()
    gate.record_proposal(InvalidationProposal(write_id="w1", invalidates=frozenset({"cache_a"})))
    # Stale read on declared namespace → not a miss
    gate.record_stale_read("w1", "cache_a")
    assert gate.miss_rate() == 0.0


def test_invalidation_gate_uncovered_read_is_miss() -> None:
    gate = InvalidationCoverageGate()
    gate.record_proposal(InvalidationProposal(write_id="w1", invalidates=frozenset({"cache_a"})))
    gate.record_stale_read("w1", "cache_b")  # not in declared set
    assert gate.miss_rate() == 1.0


def test_invalidation_gate_unknown_write_is_miss() -> None:
    gate = InvalidationCoverageGate()
    gate.record_stale_read("w_phantom", "cache_a")
    assert gate.miss_rate() == 1.0


def test_invalidation_gate_partial_misses() -> None:
    gate = InvalidationCoverageGate()
    gate.record_proposal(InvalidationProposal(write_id="w1", invalidates=frozenset({"a"})))
    gate.record_stale_read("w1", "a")  # covered
    gate.record_stale_read("w1", "b")  # miss
    gate.record_stale_read("w1", "c")  # miss
    assert gate.miss_rate() == pytest.approx(2 / 3)


def test_invalidation_gate_reset() -> None:
    gate = InvalidationCoverageGate()
    gate.record_proposal(InvalidationProposal(write_id="w1", invalidates=frozenset()))
    gate.record_stale_read("w1", "x")
    gate.reset()
    assert gate.miss_rate() == 0.0


def test_alias_atomicity_passes_with_sufficient_gap() -> None:
    before = AliasManifest(timestamp=100.0, alias_to_target={"a": "v1"})
    after = AliasManifest(timestamp=100.5, alias_to_target={"a": "v2"})
    # gap=0.5 >= 0.1 required → no raise
    alias_swap_atomicity_proof(before, after, swap_window_seconds=0.1)


def test_alias_atomicity_raises_on_overlap() -> None:
    before = AliasManifest(timestamp=100.0, alias_to_target={"a": "v1"})
    after = AliasManifest(timestamp=100.05, alias_to_target={"a": "v2"})
    with pytest.raises(AliasAtomicityViolationError):
        alias_swap_atomicity_proof(before, after, swap_window_seconds=0.1)


def test_alias_atomicity_raises_when_after_before_before() -> None:
    before = AliasManifest(timestamp=100.0, alias_to_target={"a": "v1"})
    after = AliasManifest(timestamp=99.9, alias_to_target={"a": "v2"})
    with pytest.raises(AliasAtomicityViolationError):
        alias_swap_atomicity_proof(before, after, swap_window_seconds=0.1)
