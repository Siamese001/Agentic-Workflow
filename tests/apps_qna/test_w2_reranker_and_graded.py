"""Wave 2 tests — cross-encoder reranker + graded outcome binding.

Covers:
  * W2.1: ``apps_qna.router.reranker`` passthrough contract (explicit env off),
          §29 marker emission in both passthrough and live paths.
  * W2.2: graded ``update_outcome(score=...)`` on both
          ``AppsQnaRouteBandit`` and ``AppsQnaPasteBandit``; spine
          ``NamespaceBandit.update_graded`` + ``BetaPosterior.update_graded``.
  * W2.3: ``rank_routes_by_signal(rerank=True/False)`` contract —
          passthrough when explicitly disabled, fail-soft on reranker failure.

The reranker defaults ON; tests that assert bi-encoder passthrough set
``APPS_QNA_RERANKER=0`` explicitly.
"""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from agentic_core.L0_routing.reasoning.namespace_bandit import (
    BetaPosterior,
    NamespaceBandit,
)
from apps_qna.config.route_registry import Route, RouteRegistry
from apps_qna.router.paste_bandit import AppsQnaPasteBandit
from apps_qna.router.reranker import (
    RerankOutcome,
    rerank_candidate_scores,
    rerank_routes,
)
from apps_qna.router.route_bandit import AppsQnaRouteBandit, _hash_signal
from apps_qna.router.route_seeding import rank_routes_by_signal
from apps_qna.router.semantic_router import RouteScore


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
        ],
        tie_breaker_rules=[],
    )


# --------------------------------------------------------------------------
# W2.1 — reranker contract
# --------------------------------------------------------------------------


def test_reranker_passthrough_when_env_off(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """With APPS_QNA_RERANKER=0, reranker returns bi-encoder order."""
    candidates = [
        RouteScore(
            route_id="architecture",
            route_name="Architecture",
            primary_card="05_ARCHITECTURE_CORE.md",
            score=0.8,
            mode="embedding",
        ),
        RouteScore(
            route_id="executive_fit",
            route_name="Executive Fit",
            primary_card="13_EXECUTIVE_FIT.md",
            score=0.5,
            mode="embedding",
        ),
    ]
    with patch.dict(os.environ, {"APPS_QNA_RERANKER": "0"}, clear=False):
        outcome = rerank_routes(
            query="architecture question",
            candidates=candidates,
            descriptors={"architecture": "arch", "executive_fit": "exec"},
        )
    assert outcome.mode == "bi_encoder_passthrough"
    assert outcome.rerank_delta == 0
    assert [c.route_id for c in outcome.reranked] == [
        "architecture",
        "executive_fit",
    ]
    captured = capsys.readouterr()
    marker_lines = [
        line for line in captured.out.splitlines() if line.startswith("ROUTER_DECISION:")
    ]
    assert len(marker_lines) == 1, captured.out
    assert "router=apps_qna_reranker" in marker_lines[0]
    assert "mode=bi_encoder_passthrough" in marker_lines[0]


@pytest.mark.parametrize(
    "module_name",
    [
        "apps_qna.router.reranker",
        "apps_qna.engines.router.reranker",
    ],
)
def test_reranker_gate_defaults_on_and_respects_opt_out(module_name: str) -> None:
    mod = __import__(module_name, fromlist=["_reranker_enabled"])

    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("APPS_QNA_RERANKER", None)
        assert mod._reranker_enabled() is True

    with patch.dict(os.environ, {"APPS_QNA_RERANKER": "0"}, clear=False):
        assert mod._reranker_enabled() is False


def test_reranker_default_on_uses_cross_encoder_when_available(
    capsys: pytest.CaptureFixture[str],
) -> None:
    candidates = [
        RouteScore(
            route_id="architecture",
            route_name="Architecture",
            primary_card="05_ARCHITECTURE_CORE.md",
            score=0.8,
            mode="embedding",
        ),
        RouteScore(
            route_id="executive_fit",
            route_name="Executive Fit",
            primary_card="13_EXECUTIVE_FIT.md",
            score=0.5,
            mode="embedding",
        ),
    ]

    class FakeAdapter:
        def score(self, query: str, candidate_texts: list[str]) -> list[float]:
            assert query == "leadership architecture question"
            assert candidate_texts == ["arch", "exec"]
            return [0.1, 0.9]

    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("APPS_QNA_RERANKER", None)
        with patch(
            "agentic_core.knowledge.retrieval.bge_reranker_adapter.BgeRerankerAdapter",
            return_value=FakeAdapter(),
        ):
            outcome = rerank_routes(
                query="leadership architecture question",
                candidates=candidates,
                descriptors={"architecture": "arch", "executive_fit": "exec"},
            )

    assert outcome.mode == "cross_encoder"
    assert outcome.rerank_delta == 2
    assert [c.route_id for c in outcome.reranked] == [
        "executive_fit",
        "architecture",
    ]
    captured = capsys.readouterr()
    marker_lines = [
        line for line in captured.out.splitlines() if line.startswith("ROUTER_DECISION:")
    ]
    assert len(marker_lines) == 1, captured.out
    assert "mode=cross_encoder" in marker_lines[0]


def test_reranker_empty_candidates_emits_marker(
    capsys: pytest.CaptureFixture[str],
) -> None:
    outcome = rerank_routes(
        query="irrelevant",
        candidates=[],
        descriptors={},
    )
    assert isinstance(outcome, RerankOutcome)
    assert outcome.reranked == []
    assert outcome.rerank_delta == 0
    captured = capsys.readouterr()
    marker_lines = [
        line for line in captured.out.splitlines() if line.startswith("ROUTER_DECISION:")
    ]
    assert len(marker_lines) == 1


def test_rerank_candidate_scores_passthrough_roundtrips_tuples() -> None:
    """The tuple-based entrypoint preserves order under passthrough."""
    tuples = [
        ("architecture", 0.8, "embedding"),
        ("executive_fit", 0.5, "embedding"),
    ]
    with patch.dict(os.environ, {"APPS_QNA_RERANKER": "0"}, clear=False):
        reranked, mode, delta = rerank_candidate_scores(
            query="anything",
            candidates=tuples,
            descriptors={"architecture": "arch", "executive_fit": "exec"},
        )
    assert mode == "bi_encoder_passthrough"
    assert delta == 0
    assert [t[0] for t in reranked] == ["architecture", "executive_fit"]


# --------------------------------------------------------------------------
# W2.2 — graded outcome binding
# --------------------------------------------------------------------------


def test_beta_posterior_update_graded_credits_alpha_and_beta() -> None:
    """Graded update distributes credit additively across alpha/beta."""
    p = BetaPosterior(alpha=1.0, beta=1.0)
    p.update_graded(0.75)
    assert p.alpha == pytest.approx(1.75)
    assert p.beta == pytest.approx(1.25)
    # One graded outcome == one observation.
    assert p.n_observations == 1


def test_beta_posterior_update_graded_clamps() -> None:
    p = BetaPosterior(alpha=1.0, beta=1.0)
    p.update_graded(-0.3)
    assert p.alpha == pytest.approx(1.0)
    assert p.beta == pytest.approx(2.0)
    p.update_graded(1.5)
    assert p.alpha == pytest.approx(2.0)
    assert p.beta == pytest.approx(2.0)


def test_beta_posterior_update_graded_rejects_nan() -> None:
    p = BetaPosterior()
    with pytest.raises(ValueError):
        p.update_graded(float("nan"))


def test_namespace_bandit_update_graded_flows_to_posterior() -> None:
    b = NamespaceBandit(seed=42)
    b.update_graded("ns1", "routeA", score=0.8)
    post = b.posterior("ns1", "routeA")
    assert post.alpha == pytest.approx(1.8)
    assert post.beta == pytest.approx(1.2)


def test_route_bandit_graded_update_emits_marker_and_ledger(
    capsys: pytest.CaptureFixture[str],
) -> None:
    bandit = AppsQnaRouteBandit(_mock_registry(), seed=42)
    namespace = _hash_signal("graded test signal")
    bandit.update_outcome(
        namespace=namespace,
        route="architecture",
        asked=True,
        landed=True,
        score=0.9,
    )
    captured = capsys.readouterr()
    marker_lines = [
        line for line in captured.out.splitlines() if line.startswith("ROUTER_DECISION:")
    ]
    assert marker_lines, captured.out
    line = marker_lines[0]
    assert "router=apps_qna_route_bandit" in line
    assert "event=graded_outcome" in line
    assert "grade_normalized=0.900" in line
    # Posterior reflects the graded credit (alpha += 0.9).
    post = bandit._bandit.posterior(namespace, "architecture")
    assert post.alpha == pytest.approx(1.9)
    assert post.beta == pytest.approx(1.1)


def test_paste_bandit_graded_update_emits_marker(
    capsys: pytest.CaptureFixture[str],
) -> None:
    bandit = AppsQnaPasteBandit(seed=42)
    bandit.update_outcome(
        namespace="ns_paste",
        card_id="13_EXECUTIVE_FIT.md",
        included=True,
        useful=True,
        score=0.6,
    )
    captured = capsys.readouterr()
    marker_lines = [
        line for line in captured.out.splitlines() if line.startswith("ROUTER_DECISION:")
    ]
    assert marker_lines
    line = marker_lines[0]
    assert "router=apps_qna_paste_bandit" in line
    assert "event=graded_outcome" in line
    assert "grade_normalized=0.600" in line


def test_route_bandit_bernoulli_path_unchanged(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Bernoulli ``update_outcome`` without score must NOT emit the graded marker."""
    bandit = AppsQnaRouteBandit(_mock_registry(), seed=42)
    namespace = _hash_signal("bernoulli test")
    bandit.update_outcome(
        namespace=namespace, route="architecture", asked=True, landed=True
    )
    captured = capsys.readouterr()
    # Bernoulli path does not emit a §29 apps_qna_route_bandit marker on
    # update — markers are emitted at choose() time only.
    marker_lines = [
        line for line in captured.out.splitlines() if line.startswith("ROUTER_DECISION:")
    ]
    assert not marker_lines, f"unexpected markers from Bernoulli path: {marker_lines}"
    post = bandit._bandit.posterior(namespace, "architecture")
    assert post.alpha == pytest.approx(2.0)  # 1.0 prior + 1.0 success
    assert post.beta == pytest.approx(1.0)


# --------------------------------------------------------------------------
# W2.3 — reranker wiring in route_seeding
# --------------------------------------------------------------------------


def test_rank_routes_by_signal_rerank_false_unchanged() -> None:
    """rerank=False returns bi-encoder top-N unchanged."""
    registry = _mock_registry()
    out = rank_routes_by_signal(
        registry=registry,
        signal="architecture and components and system design",
        top_n=3,
        rerank=False,
    )
    assert len(out) > 0
    # Scores are monotonically non-increasing (bi-encoder sort).
    scores = [row[1] for row in out]
    assert scores == sorted(scores, reverse=True)


def test_rank_routes_by_signal_default_rerank_true_passthrough_when_env_off() -> None:
    """Default rerank=True is a no-op when APPS_QNA_RERANKER=0."""
    registry = _mock_registry()
    with patch.dict(os.environ, {"APPS_QNA_RERANKER": "0"}, clear=False):
        out = rank_routes_by_signal(
            registry=registry,
            signal="architecture and components and system design",
            top_n=3,
        )
    assert len(out) > 0
    # Passthrough preserves the bi-encoder order => score-desc.
    scores = [row[1] for row in out]
    assert scores == sorted(scores, reverse=True)


def test_rank_routes_by_signal_empty_signal_no_rerank() -> None:
    """Empty signal returns [] without invoking the reranker."""
    registry = _mock_registry()
    assert rank_routes_by_signal(registry=registry, signal="", top_n=3) == []
    assert rank_routes_by_signal(registry=registry, signal="   ", top_n=3) == []
