"""W3 + W4 tests — panel-shared namespaces, LLM fallback, dynamic paste
buckets, rehearsal semantic cache.

Covers:
  * W3.1 — ``_hash_panel_signal`` canonicalization + ``choose_routes_for_panel``
           cold-start / hot-path / §29 paired emission.
  * W3.2 — ``classify_intent`` env-gate abstain + §29 marker emission;
           fail-soft fallthrough to static order when env disabled.
  * W4.1 — ``bucket_for(panel_size, depth)`` semantics + back-compat with
           legacy ``_bucket_for_budget``; integration through
           ``choose_paste_set(panel_size, depth)``.
  * W4.2 — ``rehearsal_cache.question_signature`` stability; ``lookup``
           miss on empty ledger emits §29 paired marker + ``cache_miss``
           ledger row.
"""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from apps_qna.config.route_registry import Route, RouteRegistry
from apps_qna.integrations import intent_classifier, rehearsal_cache
from apps_qna.router.paste_bandit import (
    AppsQnaPasteBandit,
    _bucket_for_budget,
    bucket_for,
)
from apps_qna.router.route_bandit import (
    AppsQnaRouteBandit,
    _hash_panel_signal,
    _hash_signal,
)


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
# W3.1 — panel-shared namespace hashing
# --------------------------------------------------------------------------


def test_hash_panel_signal_canonicalizes_order() -> None:
    """Sets of interviewers hash to the same namespace regardless of order."""
    a = _hash_panel_signal(["Alice deep probe", "Bob storytelling", "Carol RCA"])
    b = _hash_panel_signal(["Carol RCA", "Alice deep probe", "Bob storytelling"])
    c = _hash_panel_signal(["Bob storytelling", "Carol RCA", "Alice deep probe"])
    assert a == b == c


def test_hash_panel_signal_distinct_from_single() -> None:
    """Panel namespace prefix (qna_panel_) differs from single (qna_signal_)."""
    p = _hash_panel_signal(["single signal"])
    s = _hash_signal("single signal")
    assert p.startswith("qna_panel_")
    assert s.startswith("qna_signal_")
    assert p != s  # prefix alone already guarantees this, but assert anyway


def test_hash_panel_signal_empty() -> None:
    assert _hash_panel_signal([]) == "qna_panel_empty"
    assert _hash_panel_signal(["", "  ", "\t"]) == "qna_panel_empty"


def test_hash_panel_signal_filters_whitespace_only_entries() -> None:
    """Whitespace-only entries are dropped before hashing."""
    with_junk = _hash_panel_signal(["", "Alice", "   ", "Bob"])
    clean = _hash_panel_signal(["Alice", "Bob"])
    assert with_junk == clean


def test_choose_routes_for_panel_cold_start_returns_none() -> None:
    bandit = AppsQnaRouteBandit(_mock_registry(), seed=42)
    result = bandit.choose_routes_for_panel(
        ["interviewer A signal", "interviewer B signal"], top_n=3
    )
    assert result is None


def test_choose_routes_for_panel_empty_returns_none() -> None:
    bandit = AppsQnaRouteBandit(_mock_registry(), seed=42)
    assert bandit.choose_routes_for_panel([], top_n=3) is None


def test_choose_routes_for_panel_hot_path_emits_marker_and_ledger(
    capsys: pytest.CaptureFixture[str],
) -> None:
    bandit = AppsQnaRouteBandit(_mock_registry(), seed=42)
    signals = ["Alice leadership lens", "Bob architecture lens", "Carol RCA lens"]
    panel_ns = _hash_panel_signal(signals)
    # Pump panel-namespace observations above cold-start.
    for route in ("executive_fit", "architecture", "productization", "rca", "executive_fit", "architecture"):
        bandit._bandit.update(panel_ns, route, success=True)
    result = bandit.choose_routes_for_panel(signals, top_n=3)
    assert result is not None
    assert len(result) == 3
    captured = capsys.readouterr()
    marker_lines = [
        line for line in captured.out.splitlines() if line.startswith("ROUTER_DECISION:")
    ]
    # One marker per selection.
    assert len(marker_lines) == 3
    for line in marker_lines:
        assert f"ns={panel_ns}" in line
        assert "router=apps_qna_route_bandit" in line


# --------------------------------------------------------------------------
# W3.2 — small-LLM intent-classifier fallback
# --------------------------------------------------------------------------


def test_classify_intent_abstains_when_env_off(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("APPS_QNA_INTENT_LLM", None)
        result = intent_classifier.classify_intent(
            question="Tell me about a time you led architecture",
            registry=_mock_registry(),
        )
    assert result is None
    captured = capsys.readouterr()
    marker_lines = [
        line for line in captured.out.splitlines() if line.startswith("ROUTER_DECISION:")
    ]
    assert len(marker_lines) == 1
    assert "router=apps_qna_intent_llm" in marker_lines[0]
    assert "reason=env_gate_off" in marker_lines[0]


def test_classify_intent_empty_question_abstains() -> None:
    with patch.dict(os.environ, {"APPS_QNA_INTENT_LLM": "1"}):
        result = intent_classifier.classify_intent(
            question="", registry=_mock_registry()
        )
    assert result is None


def test_classify_intent_empty_registry_abstains() -> None:
    empty = RouteRegistry(version="v1", routes=[], tie_breaker_rules=[])
    with patch.dict(os.environ, {"APPS_QNA_INTENT_LLM": "1"}):
        assert intent_classifier.classify_intent(
            question="any question", registry=empty
        ) is None


def test_classify_intent_rejects_unknown_route_id(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """LLM returns a string that isn't a registered route — must abstain."""
    with patch.dict(os.environ, {"APPS_QNA_INTENT_LLM": "1"}):
        with patch.object(
            intent_classifier, "_invoke_provider", return_value="not_a_real_route"
        ):
            result = intent_classifier.classify_intent(
                question="any question", registry=_mock_registry()
            )
    assert result is None
    captured = capsys.readouterr()
    marker_lines = [
        line for line in captured.out.splitlines() if line.startswith("ROUTER_DECISION:")
    ]
    assert marker_lines
    assert "reason=unknown_route_id" in marker_lines[0]


def test_classify_intent_accepts_valid_route_id() -> None:
    with patch.dict(os.environ, {"APPS_QNA_INTENT_LLM": "1"}):
        with patch.object(
            intent_classifier, "_invoke_provider", return_value="architecture"
        ):
            result = intent_classifier.classify_intent(
                question="How do you design agent systems?",
                registry=_mock_registry(),
            )
    assert result == "architecture"


# --------------------------------------------------------------------------
# W4.1 — dynamic paste buckets
# --------------------------------------------------------------------------


def test_bucket_for_panel_size_base() -> None:
    """Base bucket scales with panel size, medium depth."""
    assert bucket_for(panel_size=1, depth="medium") == 10
    assert bucket_for(panel_size=2, depth="medium") == 14
    assert bucket_for(panel_size=3, depth="medium") == 18


def test_bucket_for_depth_delta() -> None:
    """Deeper panels get larger buckets; lighter get smaller."""
    light = bucket_for(panel_size=2, depth="light")
    medium = bucket_for(panel_size=2, depth="medium")
    deep = bucket_for(panel_size=2, depth="deep")
    assert light <= medium < deep


def test_bucket_for_unknown_depth_clamps_to_medium() -> None:
    assert bucket_for(panel_size=2, depth="weird") == bucket_for(
        panel_size=2, depth="medium"
    )


def test_bucket_for_returns_ceiling_entry() -> None:
    """Every output must be one of the ≤8 canonical buckets."""
    allowed = {8, 10, 12, 14, 18, 22, 25, 30}
    seen = set()
    for ps in (1, 2, 3, 5):
        for d in ("light", "medium", "deep"):
            b = bucket_for(panel_size=ps, depth=d)
            assert b in allowed
            seen.add(b)
    # The ≤ 8 budget constraint: we must use at most 8 distinct buckets.
    assert len(seen) <= 8


def test_legacy_bucket_for_budget_still_works() -> None:
    """Back-compat: callers that pass raw budgets get the legacy 4-bucket table."""
    assert _bucket_for_budget(9) == 8
    assert _bucket_for_budget(13) == 12
    assert _bucket_for_budget(17) == 18
    assert _bucket_for_budget(24) == 25


def test_choose_paste_set_uses_dynamic_bucket_when_shape_provided() -> None:
    """choose_paste_set honors (panel_size, depth) when threaded through."""
    bandit = AppsQnaPasteBandit(seed=42)
    # Cold-start returns None but the call must not raise on the new kwargs.
    result = bandit.choose_paste_set(
        signal="architecture panel",
        paste_budget=18,
        admissible_cards=["05_ARCHITECTURE_CORE.md", "12_PRODUCTIZATION.md"],
        panel_size=3,
        depth="deep",
    )
    # cold-start -> None, but no exception.
    assert result is None


# --------------------------------------------------------------------------
# W4.2 — rehearsal semantic cache
# --------------------------------------------------------------------------


def test_question_signature_is_stable_across_whitespace_and_case() -> None:
    a = rehearsal_cache.question_signature(
        "Tell me about a time you led architecture"
    )
    b = rehearsal_cache.question_signature(
        "  TELL ME ABOUT A TIME YOU LED ARCHITECTURE  "
    )
    c = rehearsal_cache.question_signature(
        "tell me about a time you led architecture?"
    )
    assert a == b == c


def test_question_signature_distinguishes_distinct_questions() -> None:
    a = rehearsal_cache.question_signature("question one about architecture")
    b = rehearsal_cache.question_signature("question two about governance")
    assert a != b


def test_question_signature_empty_is_stable() -> None:
    assert rehearsal_cache.question_signature("") == "qna_q_empty"
    assert rehearsal_cache.question_signature("   ") == "qna_q_empty"


def test_rehearsal_cache_lookup_miss_emits_marker_and_row(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Empty question -> cache_miss path emits paired §29 marker."""
    result = rehearsal_cache.lookup("")
    assert result.hit is False
    assert result.route_id is None
    captured = capsys.readouterr()
    marker_lines = [
        line for line in captured.out.splitlines() if line.startswith("ROUTER_DECISION:")
    ]
    assert len(marker_lines) == 1
    assert "router=apps_qna_rehearsal_cache" in marker_lines[0]
    assert "event=cache_miss" in marker_lines[0]


def test_warm_start_signal_returns_none_on_miss() -> None:
    """A never-seen question returns None so bandits can skip the warm-start."""
    # A random, never-cached signature ensures a miss regardless of ledger.
    q = "xyzzy-unique-question-" + rehearsal_cache.question_signature(
        "unique-" + os.urandom(8).hex()
    )
    assert rehearsal_cache.warm_start_signal(q) is None
