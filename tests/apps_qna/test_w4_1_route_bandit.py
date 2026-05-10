"""W4.1 tests — AppsQnaRouteBandit + bandit-aware seeding.

Covers:
    - Signal hashing (stable, distinct signals -> distinct namespaces)
    - Cold-start abstention (returns None when n_observations < threshold)
    - Hot-path ranking (returns RouteSelection list ordered by Thompson sample)
    - Outcome update flows through the spine NamespaceBandit
    - Constitutional §29 paired emissions: ROUTER_DECISION marker + ledger row
    - seed_likely_questions_from_research: bandit path supersedes when hot,
      cold-start gracefully falls through to W2.3 keyword ranking
"""

from __future__ import annotations

import sqlite3
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

from apps_qna.config.route_registry import Route, RouteRegistry
from apps_qna.router.route_bandit import (
    AppsQnaRouteBandit,
    RouteSelection,
    _hash_signal,
)
from apps_qna.router.route_seeding import seed_likely_questions_from_research


def _mock_registry() -> RouteRegistry:
    return RouteRegistry(
        version="v1",
        routes=[
            Route(
                id="executive_fit",
                number=1,
                name="Executive Fit",
                triggers=["leadership", "strategic"],
                answer_shape=["headline", "evidence"],
                primary_card="13_EXECUTIVE_FIT.md",
            ),
            Route(
                id="architecture",
                number=2,
                name="Architecture",
                triggers=["system design", "components"],
                answer_shape=["headline", "components"],
                primary_card="05_ARCHITECTURE_CORE.md",
            ),
            Route(
                id="productization",
                number=3,
                name="Productization",
                triggers=["accelerator", "platform"],
                answer_shape=["headline", "evidence"],
                primary_card="12_PRODUCTIZATION.md",
            ),
            Route(
                id="rca",
                number=4,
                name="RCA",
                triggers=["root cause", "post-mortem"],
                answer_shape=["timeline", "root cause"],
                primary_card="15_RCA.md",
            ),
        ],
        tie_breaker_rules=[],
    )


# --------------------------------------------------------------------------
# Signal hashing
# --------------------------------------------------------------------------


def test_hash_signal_is_stable() -> None:
    h1 = _hash_signal("Vrinda probes architecture and platform")
    h2 = _hash_signal("Vrinda probes architecture and platform")
    assert h1 == h2


def test_hash_signal_handles_empty() -> None:
    assert _hash_signal("") == "qna_signal_empty"
    assert _hash_signal("   ") == "qna_signal_empty"


def test_hash_signal_distinct_signals_distinct_namespaces() -> None:
    h1 = _hash_signal("Architecture-heavy interviewer")
    h2 = _hash_signal("Productization-heavy interviewer")
    assert h1 != h2


def test_hash_signal_starts_with_qna_signal_prefix() -> None:
    h = _hash_signal("any text")
    assert h.startswith("qna_signal_")


# --------------------------------------------------------------------------
# AppsQnaRouteBandit
# --------------------------------------------------------------------------


def test_bandit_cold_start_returns_none() -> None:
    bandit = AppsQnaRouteBandit(_mock_registry(), seed=42)
    result = bandit.choose_routes_for_signal("interviewer probes architecture", top_n=4)
    assert result is None


def test_bandit_total_observations_starts_at_zero() -> None:
    bandit = AppsQnaRouteBandit(_mock_registry(), seed=42)
    namespace = _hash_signal("test signal")
    assert bandit.total_observations(namespace) == 0


def test_bandit_clears_cold_start_after_enough_updates() -> None:
    bandit = AppsQnaRouteBandit(_mock_registry(), seed=42)
    signal = "Vrinda probes architecture, productization, executive fit"
    namespace = _hash_signal(signal)
    # Need >=5 total observations across the namespace; spread them across routes.
    for route in ("executive_fit", "architecture", "productization", "rca", "executive_fit"):
        bandit.update_outcome(
            namespace=namespace,
            route=route,
            asked=True,
            landed=True,
        )
    assert bandit.total_observations(namespace) >= 5
    result = bandit.choose_routes_for_signal(signal, top_n=4)
    assert result is not None
    assert len(result) == 4
    # All entries are RouteSelection objects with the right shape.
    for sel in result:
        assert isinstance(sel, RouteSelection)
        assert sel.route_id in {"executive_fit", "architecture", "productization", "rca"}
        assert sel.rank in {1, 2, 3, 4}
        assert 0.0 <= sel.posterior_mean <= 1.0
        assert sel.decision_id  # non-empty uuid


def test_bandit_ranking_is_descending_by_thompson_sample() -> None:
    bandit = AppsQnaRouteBandit(_mock_registry(), seed=42)
    signal = "test signal"
    namespace = _hash_signal(signal)
    # Push enough observations so we leave cold-start.
    for _ in range(8):
        bandit.update_outcome(namespace=namespace, route="executive_fit", asked=True, landed=True)
    result = bandit.choose_routes_for_signal(signal, top_n=4)
    assert result is not None
    samples = [s.thompson_sample for s in result]
    assert samples == sorted(samples, reverse=True)


def test_bandit_emits_router_decision_marker_and_ledger_row(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """End-to-end: hot-path choose() must emit BOTH marker and ledger row."""
    bandit = AppsQnaRouteBandit(_mock_registry(), seed=42)
    signal = "marker-emission test signal"
    namespace = _hash_signal(signal)
    for _ in range(6):
        bandit.update_outcome(namespace=namespace, route="architecture", asked=True, landed=True)

    # Capture stdout for marker assertion.
    result = bandit.choose_routes_for_signal(signal, top_n=2)
    assert result is not None
    captured = capsys.readouterr()
    # Marker count must equal selection count (one per surfaced route).
    marker_lines = [
        line for line in captured.out.splitlines() if line.startswith("ROUTER_DECISION:")
    ]
    assert len(marker_lines) == len(result), captured.out
    # Each marker has the expected fields.
    for line in marker_lines:
        assert "layer=L0" in line
        assert "router=apps_qna_route_bandit" in line
        assert f"ns={namespace}" in line
        assert "posterior_alpha=" in line
        assert "posterior_beta=" in line
        assert "decision_id=" in line

    # Ledger row check: open the apps_qna_pack_lifecycle DB and find rows
    # tagged with the decision_ids we just emitted.
    from tools.ledgers.schema_registry import get
    ledger_path = get("apps_qna_pack_lifecycle").db_path
    if not ledger_path.is_file():
        pytest.skip("Ledger DB not materialized")
    decision_ids = {sel.decision_id for sel in result}
    con = sqlite3.connect(ledger_path)
    try:
        cur = con.cursor()
        cur.execute(
            """SELECT event_kind, prediction_json, metadata_json FROM events
               WHERE event_kind = 'route_select' ORDER BY ts_utc DESC LIMIT 50"""
        )
        rows = cur.fetchall()
    finally:
        con.close()
    # At least one of the recently-emitted decision_ids must appear.
    found_ids = set()
    for kind, prediction_json, metadata_json in rows:
        assert kind == "route_select"
        if metadata_json:
            for did in decision_ids:
                if did in (metadata_json or ""):
                    found_ids.add(did)
    assert found_ids, "no route_select rows in ledger matched the emitted decision_ids"


def test_bandit_reset_clears_state() -> None:
    bandit = AppsQnaRouteBandit(_mock_registry(), seed=42)
    namespace = _hash_signal("reset test")
    for _ in range(8):
        bandit.update_outcome(namespace=namespace, route="rca", asked=True, landed=True)
    assert bandit.total_observations(namespace) >= 8
    bandit.reset()
    assert bandit.total_observations(namespace) == 0


def test_bandit_failure_outcomes_register_correctly() -> None:
    """asked=True, landed=False is a Bernoulli failure (routing miss)."""
    bandit = AppsQnaRouteBandit(_mock_registry(), seed=42)
    namespace = _hash_signal("failure test")
    # 3 successes for executive_fit, 5 failures for architecture.
    for _ in range(3):
        bandit.update_outcome(
            namespace=namespace, route="executive_fit", asked=True, landed=True
        )
    for _ in range(5):
        bandit.update_outcome(
            namespace=namespace, route="architecture", asked=True, landed=False
        )
    # Both arms have observations; bandit should leave cold-start.
    assert bandit.total_observations(namespace) >= 5
    # The failure-heavy arm should have a lower posterior mean than the success-heavy arm.
    exec_post = bandit._bandit.posterior(namespace, "executive_fit")
    arch_post = bandit._bandit.posterior(namespace, "architecture")
    assert exec_post.mean > arch_post.mean


# --------------------------------------------------------------------------
# seed_likely_questions_from_research bandit integration
# --------------------------------------------------------------------------


def test_seeding_uses_bandit_when_hot() -> None:
    """When bandit is hot, its ranking drives the output order."""
    registry = _mock_registry()
    bandit = AppsQnaRouteBandit(registry, seed=42)
    signal = "Vrinda probes architecture, productization, executive fit"
    namespace = _hash_signal(signal)
    # Heavy success on rca; bandit should rank it high.
    for _ in range(8):
        bandit.update_outcome(namespace=namespace, route="rca", asked=True, landed=True)

    groups = seed_likely_questions_from_research(
        registry=registry,
        interviewer_lenses={"Vrinda": signal},
        role_areas=[],
        industry_trends=[],
        top_n=4,
        bandit=bandit,
    )
    route_ids = [g.route_id for g in groups]
    assert "rca" in route_ids
    # All emitted groups have empty questions list (operator fills).
    for g in groups:
        assert g.questions == []


def test_seeding_falls_back_to_keyword_when_bandit_cold() -> None:
    """Cold bandit must not block W2.3 keyword ranking."""
    registry = _mock_registry()
    bandit = AppsQnaRouteBandit(registry, seed=42)
    # No updates; bandit is cold.
    groups = seed_likely_questions_from_research(
        registry=registry,
        interviewer_lenses={"V": "interviewer probes architecture and platform"},
        role_areas=["Architecture", "Platform engineering"],
        industry_trends=["AI adoption accelerating"],
        top_n=4,
        bandit=bandit,
    )
    # W2.3 path returns groups; result must be non-empty.
    assert len(groups) > 0
    for g in groups:
        assert g.route_id in {r.id for r in registry.routes}


def test_seeding_without_bandit_unchanged_behavior() -> None:
    """Default call (no bandit kwarg) preserves W2.3 behavior."""
    registry = _mock_registry()
    groups = seed_likely_questions_from_research(
        registry=registry,
        interviewer_lenses={"V": "architecture-heavy interviewer"},
        role_areas=["Architecture"],
        industry_trends=[],
        top_n=4,
    )
    assert len(groups) > 0


def test_seeding_handles_bandit_failure_gracefully() -> None:
    """A bandit that raises on choose_routes_for_signal must not break seeding."""
    registry = _mock_registry()

    class BrokenBandit:
        def choose_routes_for_signal(self, signal: str, *, top_n: int) -> None:
            raise RuntimeError("simulated bandit failure")

    groups = seed_likely_questions_from_research(
        registry=registry,
        interviewer_lenses={"V": "test signal"},
        role_areas=[],
        industry_trends=[],
        top_n=3,
        bandit=BrokenBandit(),
    )
    # Falls through to W2.3 / fallback; result must still be non-empty.
    assert len(groups) > 0
