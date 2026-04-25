"""Unit tests for ``agentic_core.L0_routing.reasoning.namespace_bandit``.

Plan: ``.windsurf/plans/routing-decision-process-enhancement-9c7e4d.md`` W4.
"""

from __future__ import annotations

import sqlite3
import time
import uuid

import pytest

from agentic_core.L0_routing.reasoning.namespace_bandit import (
    BetaPosterior,
    NamespaceBandit,
)
from agentic_core.L6_observability.decision_events_schema import (
    DecisionEventRow,
    ensure_schema,
    insert_decision_event,
)


def test_fresh_bandit_returns_uniform_prior() -> None:
    bandit = NamespaceBandit(seed=0)
    p = bandit.posterior("ns_a", "R3")
    assert p.alpha == 1.0
    assert p.beta == 1.0
    assert p.mean == 0.5
    assert p.n_observations == 0


def test_update_increments_correct_param() -> None:
    bandit = NamespaceBandit(seed=0)
    bandit.update("ns_a", "R3", success=True)
    bandit.update("ns_a", "R3", success=True)
    bandit.update("ns_a", "R3", success=False)
    p = bandit.posterior("ns_a", "R3")
    assert p.alpha == pytest.approx(3.0)
    assert p.beta == pytest.approx(2.0)
    assert p.n_observations == 3


def test_choose_converges_to_winning_arm() -> None:
    """Heavy-success arm should dominate after many updates."""
    bandit = NamespaceBandit(seed=42)
    # R3: 90/100 success; R1B: 10/100 success
    for _ in range(90):
        bandit.update("legal", "R3", success=True)
    for _ in range(10):
        bandit.update("legal", "R3", success=False)
    for _ in range(10):
        bandit.update("legal", "R1B", success=True)
    for _ in range(90):
        bandit.update("legal", "R1B", success=False)

    picks = [bandit.choose("legal", ["R1B", "R3"]) for _ in range(200)]
    r3_share = picks.count("R3") / len(picks)
    assert r3_share > 0.9, f"expected R3 dominance, got {r3_share:.2f}"


def test_choose_empty_admissible_raises() -> None:
    bandit = NamespaceBandit(seed=0)
    with pytest.raises(ValueError):
        bandit.choose("ns", [])


def test_per_namespace_isolation() -> None:
    """Updates in one namespace do not leak into another."""
    bandit = NamespaceBandit(seed=0)
    bandit.update("ns_a", "R3", success=True)
    bandit.update("ns_a", "R3", success=True)
    p_a = bandit.posterior("ns_a", "R3")
    p_b = bandit.posterior("ns_b", "R3")
    assert p_a.alpha == 3.0
    assert p_b.alpha == 1.0  # unchanged prior


def test_snapshot_is_deep_copy() -> None:
    bandit = NamespaceBandit(seed=0)
    bandit.update("ns_a", "R3", success=True)
    snap = bandit.snapshot()
    # Mutating the snapshot must not change live state
    for posterior in snap.values():
        posterior.alpha = 999.0
    live = bandit.posterior("ns_a", "R3")
    assert live.alpha == 2.0


def test_rebuild_from_decision_events() -> None:
    """Replay decision_events outcomes into the bandit."""
    conn = sqlite3.connect(":memory:")
    ensure_schema(conn)

    def _insert(ns: str, route: str, success: bool) -> None:
        row = DecisionEventRow(
            decision_id=str(uuid.uuid4()),
            timestamp=time.time(),
            decision_layer="L0_routing",
            app_name=ns,
            request_hash="r",
            chosen_route=route,
            policy_hash="p",
            snapshot_id="s",
            calibration_version="c",
            judge_version="j",
            provenance_digest="d",
            outcome_success=success,
        )
        insert_decision_event(conn, row)

    for _ in range(7):
        _insert("legal", "R3", True)
    for _ in range(3):
        _insert("legal", "R3", False)
    _insert("medical", "R1B", True)

    bandit = NamespaceBandit(seed=0)
    applied = bandit.rebuild_from_decision_events(conn)
    assert applied == 11
    p_legal = bandit.posterior("legal", "R3")
    assert p_legal.alpha == pytest.approx(8.0)  # prior 1 + 7 successes
    assert p_legal.beta == pytest.approx(4.0)  # prior 1 + 3 failures
    p_med = bandit.posterior("medical", "R1B")
    assert p_med.alpha == pytest.approx(2.0)


def test_reset_clears_all_posteriors() -> None:
    bandit = NamespaceBandit(seed=0)
    bandit.update("ns_a", "R3", success=True)
    bandit.reset()
    p = bandit.posterior("ns_a", "R3")
    assert p.alpha == 1.0
    assert p.beta == 1.0


def test_beta_posterior_sample_in_unit_interval() -> None:
    import random as _r

    rng = _r.Random(0)
    p = BetaPosterior(alpha=5.0, beta=3.0)
    for _ in range(100):
        x = p.sample(rng)
        assert 0.0 <= x <= 1.0
