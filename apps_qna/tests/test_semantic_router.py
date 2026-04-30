"""Tests for apps_qna.router.semantic_router (Wave 6 — embedding router)."""

from __future__ import annotations

import io
from contextlib import redirect_stdout

import pytest

from apps_qna.config.route_registry import load_route_registry
from apps_qna.router.semantic_router import (
    RouteScore,
    SemanticRouter,
    _cosine,
    _tokenize,
)
from apps_qna.scripts.run_qna import main as cli_main


@pytest.fixture(scope="module")
def router() -> SemanticRouter:
    return SemanticRouter(load_route_registry())


# ------------- Token / cosine primitives -------------


def test_tokenize_drops_stopwords_and_short_tokens() -> None:
    tokens = _tokenize("Tell me about a time you used MMM in production")
    # 'tell', 'me', 'about', 'a', 'in' all dropped; case-insensitive
    assert "mmm" in tokens
    assert "production" in tokens
    assert "tell" not in tokens
    assert "me" not in tokens
    assert "about" not in tokens
    assert "a" not in tokens


def test_tokenize_empty_string() -> None:
    assert _tokenize("") == {}


def test_cosine_identical_vectors_is_one() -> None:
    a = _tokenize("architecture orchestration governance")
    assert _cosine(a, a) == pytest.approx(1.0)


def test_cosine_disjoint_is_zero() -> None:
    a = _tokenize("architecture orchestration")
    b = _tokenize("offshore distributed")
    assert _cosine(a, b) == 0.0


def test_cosine_empty_is_zero() -> None:
    a = _tokenize("anything")
    assert _cosine(a, {}) == 0.0  # type: ignore[arg-type]
    assert _cosine({}, a) == 0.0  # type: ignore[arg-type]


# ------------- Route ranking — manifest-aligned expectations -------------


_ROUTING_EXPECTATIONS: list[tuple[str, str]] = [
    ("How would you build an agentic architecture for our team?", "architecture"),
    ("How do you handle hallucinations and guardrails?", "governance"),
    # NB: STAR triggers are mostly stopwords ("tell me about a time", "give me an
    # example") so the surviving tokens must include the genuinely-distinctive
    # words. Domain-heavy STAR prompts (e.g. "measurement model rollout") will
    # tie or lose to ds_to_platform/architecture under pure BoW; resolving that
    # is a tie-breaker concern noted in NEXT_STEP_router_tiebreakers.
    ("Give me an example of prior work you have shipped.", "star_proof"),
    ("What went wrong on your last big project? Root cause please.", "rca"),
    ("How does MMM relate to incrementality and Meridian?", "ds_to_platform"),
    ("What's your approach to ROI and planner adoption?", "productization"),
    ("How do you run a distributed pods / DGS engineering org?", "global_engineering"),
    ("Be more specific — what tools exactly did you use?", "cross_exam"),
    ("Why this company? Why this role for you?", "executive_fit"),
]


@pytest.mark.parametrize("question,expected_route_id", _ROUTING_EXPECTATIONS)
def test_route_lands_on_expected_primary(
    router: SemanticRouter, question: str, expected_route_id: str
) -> None:
    """Each canonical sample question should rank its expected route #1."""
    ranked = router.route(question, top_k=3)
    assert ranked, "router returned no candidates"
    assert ranked[0].route_id == expected_route_id, (
        f"Question {question!r} ranked {ranked[0].route_id} first, "
        f"expected {expected_route_id}. Top-3: "
        f"{[(h.route_id, round(h.score, 3)) for h in ranked]}"
    )


def test_route_returns_route_score_objects(router: SemanticRouter) -> None:
    ranked = router.route("architecture orchestration", top_k=1)
    assert len(ranked) == 1
    assert isinstance(ranked[0], RouteScore)
    assert ranked[0].route_id == "architecture"
    assert ranked[0].primary_card == "05_ARCHITECTURE_CORE.md"
    assert 0.0 < ranked[0].score <= 1.0


def test_route_top_k_caps_results(router: SemanticRouter) -> None:
    ranked = router.route("architecture", top_k=5)
    assert len(ranked) == 5
    # Scores are non-increasing
    scores = [h.score for h in ranked]
    assert scores == sorted(scores, reverse=True)


def test_route_invalid_top_k_raises(router: SemanticRouter) -> None:
    with pytest.raises(ValueError):
        router.route("anything", top_k=0)
    with pytest.raises(ValueError):
        router.route("anything", top_k=-1)


def test_route_zero_overlap_returns_zero_scores(router: SemanticRouter) -> None:
    """A nonsense question with no token overlap returns all-zero scores."""
    ranked = router.route("xyzzy plugh foo bar quux", top_k=3)
    assert all(h.score == 0.0 for h in ranked)


def test_best_returns_none_when_no_overlap(router: SemanticRouter) -> None:
    assert router.best("xyzzy plugh foo bar quux") is None


def test_best_returns_top_when_overlap(router: SemanticRouter) -> None:
    best = router.best("Tell me about a time you shipped governed agents")
    assert best is not None
    assert best.route_id in {"star_proof", "governance"}


# ------------- CLI integration -------------


def test_cli_route_subcommand(capsys: pytest.CaptureFixture[str]) -> None:
    rc = cli_main(["route", "How would you build a governed agentic architecture?"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "How would you build" in out
    # Architecture should be ranked #1; the primary card filename appears
    assert "05_ARCHITECTURE_CORE.md" in out


def test_cli_route_zero_overlap_returns_1(capsys: pytest.CaptureFixture[str]) -> None:
    rc = cli_main(["route", "xyzzy plugh foo"])
    assert rc == 1
    assert "All scores zero" in capsys.readouterr().out


def test_cli_route_respects_top_k(capsys: pytest.CaptureFixture[str]) -> None:
    rc = cli_main(["route", "architecture orchestration", "--top-k", "1"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Top 1 routes:" in out
    # Only one numbered line in the ranking
    numbered = [line for line in out.splitlines() if line.lstrip().startswith("1.")]
    assert len(numbered) == 1
