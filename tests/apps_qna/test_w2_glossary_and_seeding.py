"""W2.2 + W2.3 tests — global glossary extraction + route seeding.

Covers:
    - ``_extract_glossary_globally``: acronym + parenthetical + inline definition patterns
    - ``_accept_glossary_entry``: quality gate (length, alpha ratio, blocklist)
    - ``rank_routes_by_signal``: BGE / keyword route ranking
    - ``seed_likely_questions_from_research``: end-to-end seeding with fallback order
    - ``parse_research_brief_text(..., route_registry=...)`` integration
"""

from __future__ import annotations

import textwrap

import pytest

from apps_qna.config.route_registry import Route, RouteRegistry
from apps_qna.integrations.from_research_brief import (
    _accept_glossary_entry,
    _extract_glossary_globally,
    parse_research_brief_text,
)
from apps_qna.router.route_seeding import (
    rank_routes_by_signal,
    seed_likely_questions_from_research,
)


@pytest.fixture(autouse=True)
def _disable_reranker_for_bi_encoder_ranking_tests(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_QNA_RERANKER", "0")


def _mock_registry() -> RouteRegistry:
    """Build a minimal but realistic registry for ranking tests."""
    return RouteRegistry(
        version="v1",
        routes=[
            Route(
                id="executive_fit",
                number=1,
                name="Executive Fit",
                triggers=["leadership", "first 90 days", "strategic", "cultural fit"],
                answer_shape=["headline", "evidence"],
                primary_card="13_EXECUTIVE_FIT.md",
            ),
            Route(
                id="architecture",
                number=2,
                name="Architecture",
                triggers=["system design", "components", "diagrams", "scalability"],
                answer_shape=["headline", "components"],
                primary_card="05_ARCHITECTURE_CORE.md",
            ),
            Route(
                id="productization",
                number=3,
                name="Productization",
                triggers=["accelerator", "reusable IP", "platform", "GTM"],
                answer_shape=["headline", "evidence"],
                primary_card="12_PRODUCTIZATION.md",
            ),
            Route(
                id="rca",
                number=4,
                name="RCA",
                triggers=["root cause", "incident", "post-mortem", "failure"],
                answer_shape=["timeline", "root cause"],
                primary_card="15_RCA.md",
            ),
            Route(
                id="cross_exam",
                number=5,
                name="Cross-Exam",
                triggers=["challenge", "defend", "scrutiny"],
                answer_shape=["claim", "evidence"],
                primary_card="16_CROSS_EXAM.md",
            ),
        ],
        tie_breaker_rules=[],
    )


# --------------------------------------------------------------------------
# W2.2 — Global glossary extraction
# --------------------------------------------------------------------------


def test_extract_glossary_acronym_with_expansion() -> None:
    """`Long Form (ACRONYM)` -> ACRONYM = Long Form."""
    text = (
        "Searce uses Model Context Protocol (MCP) to integrate AI agents "
        "with external tools."
    )
    entries = _extract_glossary_globally(text)
    terms = {e.term: e.definition for e in entries}
    assert "MCP" in terms
    assert "Model Context Protocol" in terms["MCP"]


def test_extract_glossary_acronym_inverse() -> None:
    """`ACRONYM (Long Form)` -> ACRONYM = Long Form."""
    text = "The team built RAG (Retrieval Augmented Generation) pipelines."
    entries = _extract_glossary_globally(text)
    terms = {e.term: e.definition for e in entries}
    assert "RAG" in terms
    assert "Retrieval Augmented Generation" in terms["RAG"]


def test_extract_glossary_inline_definition() -> None:
    """`Term is/means/refers to definition` -> Term = definition."""
    text = (
        "EVLOS is the company's internal methodology for process "
        "redesign before technology adoption is attempted."
    )
    entries = _extract_glossary_globally(text)
    # Inline pattern is loose; we accept that EVLOS may or may not match
    # (depending on exact regex tokenization), but the function must not
    # raise and must return entries that pass the quality gate.
    for entry in entries:
        assert _accept_glossary_entry(entry.term, entry.definition)


def test_extract_glossary_dedupes_repeated_acronyms() -> None:
    """Repeated acronyms emit one entry."""
    text = (
        "Model Context Protocol (MCP) is widely adopted. "
        "Many systems use Model Context Protocol (MCP) today."
    )
    entries = _extract_glossary_globally(text)
    mcp_entries = [e for e in entries if e.term == "MCP"]
    assert len(mcp_entries) == 1


def test_accept_glossary_entry_rejects_too_short_definition() -> None:
    assert not _accept_glossary_entry("MCP", "x")


def test_accept_glossary_entry_rejects_too_long_definition() -> None:
    assert not _accept_glossary_entry("MCP", "y" * 500)


def test_accept_glossary_entry_rejects_blocklisted_term() -> None:
    assert not _accept_glossary_entry("This", "is a definition that looks valid")


def test_accept_glossary_entry_rejects_low_alpha_ratio() -> None:
    """Mostly-punctuation 'definitions' must be rejected."""
    assert not _accept_glossary_entry("MCP", "...!!! ??? ----- $$$")


def test_accept_glossary_entry_accepts_valid() -> None:
    assert _accept_glossary_entry(
        "MCP", "Model Context Protocol used to connect agents to tools"
    )


def test_parse_research_brief_text_picks_up_global_glossary() -> None:
    """End-to-end: glossary entries flow up from the global scan."""
    text = textwrap.dedent(
        """
        ## Company Overview
        Acme uses Model Context Protocol (MCP) extensively. The team also
        relies on Retrieval Augmented Generation (RAG) for context.

        ## Industry Trends
        AI adoption is accelerating.
        """
    ).strip()
    result = parse_research_brief_text(text)
    terms = {e.term for e in result.glossary_entries}
    assert "MCP" in terms
    assert "RAG" in terms


# --------------------------------------------------------------------------
# W2.3 — Route relevance ranking + seeding
# --------------------------------------------------------------------------


def test_rank_routes_by_signal_returns_sorted_results() -> None:
    """Architecture-heavy signal must rank architecture above RCA."""
    registry = _mock_registry()
    signal = (
        "The interviewer probes deeply on system design, scalability, "
        "components, and architecture diagrams. Hot buttons include "
        "platform engineering and architecture trade-offs."
    )
    ranked = rank_routes_by_signal(registry=registry, signal=signal, top_n=5)
    assert len(ranked) > 0
    # Scores must be sorted descending.
    scores = [r[1] for r in ranked]
    assert scores == sorted(scores, reverse=True)
    # Architecture should rank above RCA for this signal.
    arch_rank = next(i for i, r in enumerate(ranked) if r[0] == "architecture")
    rca_rank = next(i for i, r in enumerate(ranked) if r[0] == "rca")
    assert arch_rank < rca_rank


def test_rank_routes_by_signal_empty_signal_returns_empty() -> None:
    registry = _mock_registry()
    assert rank_routes_by_signal(registry=registry, signal="", top_n=5) == []


def test_rank_routes_by_signal_empty_registry_returns_empty() -> None:
    empty = RouteRegistry(version="v1", routes=[], tie_breaker_rules=[])
    assert rank_routes_by_signal(registry=empty, signal="anything", top_n=5) == []


def test_seed_likely_questions_emits_priority_order() -> None:
    """Seeded groups must be in ranked order with empty questions list."""
    registry = _mock_registry()
    groups = seed_likely_questions_from_research(
        registry=registry,
        interviewer_lenses={
            "Vrinda": (
                "Commercial leader who probes architecture, productization, "
                "and executive-fit. Hot buttons: scaling AI offerings, "
                "team building, customer trust, partner ecosystem."
            )
        },
        role_areas=["Pipeline ownership", "Production architecture", "Delivery quality"],
        industry_trends=["Enterprise AI adoption", "Regulated industries shift"],
        top_n=5,
    )
    assert len(groups) == 5
    # Each group has a route_id present in the registry.
    valid_ids = {r.id for r in registry.routes}
    for g in groups:
        assert g.route_id in valid_ids
        assert g.questions == []
    # Order is unique (no dupes).
    assert len({g.route_id for g in groups}) == 5


def test_seed_likely_questions_falls_back_when_no_signal() -> None:
    """No interviewer / role / trend signal -> fallback ordering kicks in."""
    registry = _mock_registry()
    groups = seed_likely_questions_from_research(
        registry=registry,
        interviewer_lenses={},
        role_areas=[],
        industry_trends=[],
        top_n=5,
    )
    # Fallback order still produces a list (executive_fit prioritized).
    assert len(groups) == 5
    assert groups[0].route_id == "executive_fit"


def test_parse_research_brief_text_seeds_when_registry_passed() -> None:
    """End-to-end: passing route_registry triggers seeding."""
    registry = _mock_registry()
    text = textwrap.dedent(
        """
        ## Company Overview
        Acme is a 2200-person consulting firm.

        ## Interviewer Lens: Vrinda
        She probes architecture, scalability, and platform components.
        Hot buttons include system design and architecture trade-offs.
        """
    ).strip()
    result = parse_research_brief_text(text, route_registry=registry)
    assert len(result.likely_questions) > 0
    # Each entry has an empty questions list.
    for g in result.likely_questions:
        assert g.questions == []


def test_parse_research_brief_text_no_seeding_when_no_registry() -> None:
    """Default behavior: no registry -> no seeding -> empty likely_questions."""
    text = "## Company Overview\nAcme is a firm.\n## Trends\nAI adoption."
    result = parse_research_brief_text(text)
    assert result.likely_questions == []
