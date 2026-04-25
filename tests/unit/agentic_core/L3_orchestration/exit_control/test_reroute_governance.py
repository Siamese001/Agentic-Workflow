"""Unit tests for ``agentic_core.L3_orchestration.exit_control.reroute_governance``.

Plan: ``.windsurf/plans/routing-decision-process-enhancement-9c7e4d.md`` W10.
"""

from __future__ import annotations

import pytest

from agentic_core.L3_orchestration.exit_control.reroute_governance import (
    ReplayCertResult,
    RerouteCeiling,
    RerouteCeilingExceededError,
    evaluate_judge_disagreement,
    judge_disagreement_rate,
    replay_cert_blocks,
)


def test_reroute_ceiling_default_two_allowed() -> None:
    ceiling = RerouteCeiling(max_reroutes=2)
    assert ceiling.attempt_reroute("req_1") == 1
    assert ceiling.attempt_reroute("req_1") == 2
    with pytest.raises(RerouteCeilingExceededError):
        ceiling.attempt_reroute("req_1")


def test_reroute_ceiling_per_request_isolated() -> None:
    ceiling = RerouteCeiling(max_reroutes=1)
    ceiling.attempt_reroute("req_a")
    ceiling.attempt_reroute("req_b")
    # Each is at 1; one more on req_a should fail
    with pytest.raises(RerouteCeilingExceededError):
        ceiling.attempt_reroute("req_a")
    assert ceiling.reroute_count("req_b") == 1


def test_reroute_ceiling_zero_blocks_all() -> None:
    ceiling = RerouteCeiling(max_reroutes=0)
    with pytest.raises(RerouteCeilingExceededError):
        ceiling.attempt_reroute("req")


def test_reroute_ceiling_negative_max_raises() -> None:
    with pytest.raises(ValueError):
        RerouteCeiling(max_reroutes=-1)


def test_reroute_ceiling_reset() -> None:
    ceiling = RerouteCeiling(max_reroutes=2)
    ceiling.attempt_reroute("r")
    ceiling.attempt_reroute("r")
    ceiling.reset("r")
    # After reset can attempt again
    assert ceiling.attempt_reroute("r") == 1


def test_judge_disagreement_empty_zero() -> None:
    assert judge_disagreement_rate([], []) == 0.0


def test_judge_disagreement_full_agreement() -> None:
    assert judge_disagreement_rate([True, False, True], [True, False, True]) == 0.0


def test_judge_disagreement_mixed() -> None:
    rate = judge_disagreement_rate([True, False, True, False], [False, False, True, True])
    # Rows 0 and 3 disagree → 2/4 = 0.5
    assert rate == 0.5


def test_judge_disagreement_length_mismatch_raises() -> None:
    with pytest.raises(ValueError):
        judge_disagreement_rate([True], [True, False])


def test_evaluate_judge_disagreement_alarm() -> None:
    s = evaluate_judge_disagreement(
        [True] * 8 + [False] * 2,
        [False] * 8 + [True] * 2,
        alarm_threshold=0.15,
    )
    # Disagreement on every row → 1.0
    assert s.rate == 1.0
    assert s.alarm is True
    assert s.n_rows == 10


def test_evaluate_judge_disagreement_no_alarm() -> None:
    s = evaluate_judge_disagreement(
        [True] * 10,
        [True] * 10,
        alarm_threshold=0.10,
    )
    assert s.alarm is False


def test_replay_cert_blocks_pure() -> None:
    """Failed certs surface as blocked decision_ids; passed ones do not."""
    results = [
        ReplayCertResult(decision_id="d1", expected_digest="a", observed_digest="a"),
        ReplayCertResult(decision_id="d2", expected_digest="a", observed_digest="b"),
        ReplayCertResult(decision_id="d3", expected_digest="x", observed_digest="x"),
        ReplayCertResult(decision_id="d4", expected_digest="x", observed_digest="y"),
    ]
    blocked = replay_cert_blocks(results)
    assert blocked == {"d2", "d4"}


def test_replay_cert_blocks_empty() -> None:
    assert replay_cert_blocks([]) == set()
