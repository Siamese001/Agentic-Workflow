"""Tests for golden-set candidate selection (v6 §S2D / §S4A).

Plan ``finish-open-scope-test-harden-38010b``.
"""

from __future__ import annotations

import pytest

from agentic_core.L3_orchestration.exit_eval.consistency import (
    BucketKey,
    PassKStore,
    TrialRecord,
)
from agentic_core.L3_orchestration.exit_eval.golden_set import (
    CandidateRecord,
    GoldenSetPolicy,
    select_candidates,
)


def _seed(store: PassKStore, key: BucketKey, results: list[bool]) -> None:
    for i, ok in enumerate(results):
        store.record(key, TrialRecord(run_id=f"r{i}", passed=ok, timestamp=float(i)))


def _key(t: str = "brief") -> BucketKey:
    return BucketKey(t, "X1D@v1", "v1", "v1")


# --------------------------------------------------------------------------- #
# Policy validation
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "kwargs, msg",
    [
        ({"min_history": 0}, "min_history"),
        ({"pass_rate_threshold": 1.5}, "pass_rate_threshold"),
        ({"recency_window": 0}, "recency_window"),
        ({"min_history": 5, "recency_window": 6}, "recency_window cannot exceed"),
    ],
)
def test_policy_rejects_bad_values(kwargs, msg):
    with pytest.raises(ValueError, match=msg):
        GoldenSetPolicy(**kwargs)


def test_policy_defaults_are_conservative():
    """Defaults: 20-trial history, 100% pass rate, last-5 must all pass."""
    p = GoldenSetPolicy()
    assert p.min_history == 20
    assert p.pass_rate_threshold == 1.0
    assert p.recency_window == 5


# --------------------------------------------------------------------------- #
# Selection rules
# --------------------------------------------------------------------------- #


def test_below_min_history_is_excluded():
    store = PassKStore()
    k = _key()
    _seed(store, k, [True] * 5)  # only 5 trials
    out = select_candidates(store, [k], policy=GoldenSetPolicy(min_history=10, recency_window=2))
    assert out == ()


def test_perfect_history_above_threshold_is_promoted():
    store = PassKStore()
    k = _key()
    _seed(store, k, [True] * 25)
    pol = GoldenSetPolicy(min_history=20, pass_rate_threshold=1.0, recency_window=5)
    out = select_candidates(store, [k], policy=pol)
    assert len(out) == 1
    rec = out[0]
    assert isinstance(rec, CandidateRecord)
    assert rec.key == k
    assert rec.history_size == 25
    assert rec.recent_pass_rate == 1.0
    assert rec.had_recent_failure is False


def test_recent_failure_short_circuits_promotion():
    """Even with high pass-rate, a single failure in recency_window blocks."""
    store = PassKStore()
    k = _key()
    # 25 passes, then 1 fail at the very end -> recent failure.
    _seed(store, k, [True] * 25 + [False])
    pol = GoldenSetPolicy(min_history=20, pass_rate_threshold=0.9, recency_window=5)
    out = select_candidates(store, [k], policy=pol)
    assert out == ()


def test_old_failure_outside_recency_window_does_not_block():
    """A failure older than recency_window must not block promotion."""
    store = PassKStore()
    k = _key()
    # One failure in slot 0, then 25 passes -> last 5 are clean.
    _seed(store, k, [False] + [True] * 25)
    # min_history=20 evaluates the last 20 (all pass), recency_window=5 (all pass).
    pol = GoldenSetPolicy(min_history=20, pass_rate_threshold=1.0, recency_window=5)
    out = select_candidates(store, [k], policy=pol)
    assert len(out) == 1
    assert out[0].had_recent_failure is False


def test_pass_rate_below_threshold_is_excluded():
    store = PassKStore()
    k = _key()
    # 18 passes + 2 fails in middle = 90%, then 5 clean passes at tail.
    seq = [True] * 18 + [False, False] + [True] * 5
    _seed(store, k, seq)
    pol = GoldenSetPolicy(min_history=20, pass_rate_threshold=1.0, recency_window=5)
    out = select_candidates(store, [k], policy=pol)
    assert out == ()


def test_relaxed_policy_admits_imperfect_track():
    store = PassKStore()
    k = _key("capability_track")
    # 19 passes + 1 fail spread out, then 5 clean passes at tail = 95% over last 20.
    seq = [True] * 13 + [False] + [True] * 6 + [True] * 5
    _seed(store, k, seq)
    pol = GoldenSetPolicy(min_history=20, pass_rate_threshold=0.9, recency_window=5)
    out = select_candidates(store, [k], policy=pol)
    assert len(out) == 1
    assert out[0].recent_pass_rate >= 0.9


# --------------------------------------------------------------------------- #
# Determinism + read-only contract
# --------------------------------------------------------------------------- #


def test_select_is_deterministic_and_sorted():
    store = PassKStore()
    keys = [
        BucketKey("brief", "X1D@v2", "v1", "v1"),
        BucketKey("brief", "X1D@v1", "v1", "v1"),
        BucketKey("answer", "X1D@v1", "v1", "v1"),
    ]
    for k in keys:
        _seed(store, k, [True] * 25)
    out1 = select_candidates(store, keys)
    out2 = select_candidates(store, list(reversed(keys)))
    # Sorted by trajectory_class then rubric_version.
    assert [r.key for r in out1] == [
        BucketKey("answer", "X1D@v1", "v1", "v1"),
        BucketKey("brief", "X1D@v1", "v1", "v1"),
        BucketKey("brief", "X1D@v2", "v1", "v1"),
    ]
    assert out1 == out2


def test_select_does_not_mutate_store():
    store = PassKStore()
    k = _key()
    _seed(store, k, [True] * 25)
    snapshot_before = store.history(k)
    select_candidates(store, [k])
    snapshot_after = store.history(k)
    assert snapshot_before == snapshot_after


def test_duplicate_keys_in_input_are_deduped():
    store = PassKStore()
    k = _key()
    _seed(store, k, [True] * 25)
    out = select_candidates(store, [k, k, k])
    assert len(out) == 1


def test_unknown_key_returns_empty_silently():
    """A key with no history must not crash; just exclude it."""
    store = PassKStore()
    out = select_candidates(store, [_key("never_seen")])
    assert out == ()
