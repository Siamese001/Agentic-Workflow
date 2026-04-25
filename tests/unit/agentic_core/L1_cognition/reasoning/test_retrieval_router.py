"""Tests for the agentic retrieval router — ADR-064."""

from __future__ import annotations

import pytest

from agentic_core.L1_cognition.reasoning.retrieval_router import (
    SLO,
    IntentClass,
    RetrievalRouter,
    RouteUnsatisfiableError,
    RouterHints,
    classify_intent,
)


# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "query,expected",
    [
        # Code concept (NL question + code tokens).
        (
            "How does the reranker_factory pick the backend?",
            IntentClass.CODE_CONCEPT,
        ),
        # Code locator (lone path).
        (
            "agentic_core.knowledge.retrieval.reranker_factory",
            IntentClass.CODE_LOCATOR,
        ),
        # Prose factual (short NL question, no code tokens).
        ("what is the deployment process", IntentClass.PROSE_FACTUAL),
        # Prose abstract why.
        (
            "Why do MCP calls hang and which server owns the race",
            IntentClass.PROSE_ABSTRACT_WHY,
        ),
        # Metadata filter (date cue).
        (
            "find all guardian exemptions since 2026",
            IntentClass.METADATA_FILTER,
        ),
        # Metadata filter (layer cue).
        ("show all rules in layer L5", IntentClass.METADATA_FILTER),
        # Trace lookup.
        ("look up trace_id abc123", IntentClass.TRACE_LOOKUP),
        # Incident recall.
        ("what was the RCA for the chromadb outage", IntentClass.INCIDENT_RECALL),
        # Empty.
        ("", IntentClass.UNKNOWN),
        # Bare filepath.
        ("ADR-046-rerank-revival.md", IntentClass.CODE_LOCATOR),
        # Question with acronym → CODE_CONCEPT (acronym matches CamelCase token).
        ("What is CRAG?", IntentClass.CODE_CONCEPT),
    ],
)
def test_intent_classifier(query: str, expected: IntentClass) -> None:
    assert classify_intent(query) == expected


def test_compound_query_with_length_threshold() -> None:
    long_compound = (
        "list every reranker module and describe each backend "
        "and document their callers and identify their tests "
        "and enumerate their fixtures and explain their assertions"
    )
    assert classify_intent(long_compound) == IntentClass.PROSE_COMPOUND


# ---------------------------------------------------------------------------
# Router (Tier 1 + budget enforcement)
# ---------------------------------------------------------------------------


class TestRouterBasic:
    def test_code_concept_uses_hyde_and_late_rerank(self) -> None:
        router = RetrievalRouter()
        plan = router.route(
            "How does the reranker_factory pick the backend?",
            RouterHints(slo=SLO.BACKGROUND),
        )
        assert plan.intent_class == IntentClass.CODE_CONCEPT
        assert plan.query_transform == "hyde"
        assert plan.reranker_mode in {"cross_encoder_late", "cross_encoder"}
        assert plan.reflective is True

    def test_metadata_filter_uses_self_query(self) -> None:
        router = RetrievalRouter()
        plan = router.route(
            "find all rules in layer L5 since 2026",
            RouterHints(slo=SLO.INTERACTIVE),
        )
        assert plan.intent_class == IntentClass.METADATA_FILTER
        assert plan.query_transform == "self_query"

    def test_unknown_uses_identity_baseline(self) -> None:
        router = RetrievalRouter()
        plan = router.route("", RouterHints())
        assert plan.intent_class == IntentClass.UNKNOWN
        assert plan.query_transform == "identity"

    def test_route_reason_includes_intent(self) -> None:
        router = RetrievalRouter()
        plan = router.route("anything random", RouterHints())
        assert "intent=" in plan.route_reason


class TestBudgetDowngrade:
    def test_interactive_slo_triggers_downgrade_for_heavy_intent(self) -> None:
        router = RetrievalRouter()
        # CODE_CONCEPT default = hyde (250) + late_rerank (500) +
        # reflective (2000) + hot (200) = 2950ms vs 800ms interactive.
        plan = router.route(
            "How does the reranker_factory pick the backend?",
            RouterHints(slo=SLO.INTERACTIVE),
        )
        # Should have applied at least one downgrade to fit.
        assert len(plan.downgrades) >= 1
        assert plan.latency_budget_ms <= 800

    def test_batch_slo_keeps_full_plan(self) -> None:
        router = RetrievalRouter()
        plan = router.route(
            "How does the reranker_factory pick the backend?",
            RouterHints(slo=SLO.BATCH),
        )
        # Batch budget 30s — no downgrades needed.
        assert plan.downgrades == ()
        assert plan.reflective is True


class TestHintsNarrowing:
    def test_allowed_collections_narrows(self) -> None:
        router = RetrievalRouter()
        plan = router.route(
            "How does the reranker_factory pick the backend?",
            RouterHints(
                slo=SLO.BACKGROUND,
                allowed_collections=("code_chunks",),
            ),
        )
        assert plan.collections == ("code_chunks",)

    def test_allowed_collections_with_no_match_falls_back_to_caller(self) -> None:
        router = RetrievalRouter()
        plan = router.route(
            "look up trace_id abc",  # default collections = (traces,)
            RouterHints(
                slo=SLO.BACKGROUND,
                allowed_collections=("code_chunks", "docs"),
            ),
        )
        # No overlap with trace defaults; router falls back to caller list.
        assert plan.collections == ("code_chunks", "docs")

    def test_allowed_tiers_narrowing(self) -> None:
        router = RetrievalRouter()
        plan = router.route(
            "anything",
            RouterHints(allowed_tiers=("cold-batch",)),
        )
        assert plan.dim_tier == "cold-batch"


class TestUnsatisfiable:
    def test_strict_raises_when_collections_disallowed(self) -> None:
        router = RetrievalRouter()
        with pytest.raises(RouteUnsatisfiableError):
            router.route(
                "look up trace_id abc",  # wants 'traces'
                RouterHints(
                    allowed_collections=("docs",),
                    fail_on_unsatisfiable=True,
                ),
            )

    def test_strict_raises_when_tier_disallowed(self) -> None:
        router = RetrievalRouter()
        with pytest.raises(RouteUnsatisfiableError):
            router.route(
                "anything",
                RouterHints(
                    allowed_tiers=("nonexistent-tier",),
                    fail_on_unsatisfiable=True,
                ),
            )


class TestDeterminism:
    def test_same_query_same_plan(self) -> None:
        router = RetrievalRouter()
        a = router.route(
            "How does the reranker_factory pick the backend?",
            RouterHints(slo=SLO.BACKGROUND),
        )
        b = router.route(
            "How does the reranker_factory pick the backend?",
            RouterHints(slo=SLO.BACKGROUND),
        )
        assert a == b
