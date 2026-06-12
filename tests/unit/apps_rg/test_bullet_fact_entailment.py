"""W4.3 (G15/G17) — selection-time numeric fact-entailment unit coverage.

Deterministic, hermetic. No provider calls. Covers token extraction, magnitude/unit
normalization equivalence, per-slot corpus provenance (selected_fact_plan C0-pool facts +
bundle NON-metric text), fail-open behavior, and the ibm shared-bundle metric-leak
regression: IBM bundle ``linked_metric_outcome_ids`` are graph routing metadata, not
free-floating proof text. A metric token from one IBM slot must NOT entail for a
slot whose own selected fact has no such metric.
"""

from __future__ import annotations

from apps_rg.runtime.reasoning.bullet_fact_entailment import (
    build_slot_entailment_corpus,
    extract_numeric_tokens,
    normalize_numeric_token,
    numeric_entailment_check,
)


# ---------------------------------------------------------------------------
# Token extraction
# ---------------------------------------------------------------------------


def test_extract_currency_percent_multiplier_and_worded_tokens() -> None:
    text = "Drove $12M ARR and $2.5 million savings, 20% growth, 3x throughput, 10 million events."
    tokens = extract_numeric_tokens(text)
    assert "$12M" in tokens
    assert "$2.5 million" in tokens
    assert "20%" in tokens
    assert "3x" in tokens
    assert "10 million" in tokens


def test_extract_range_endpoints_and_small_ordinal_skip() -> None:
    # "8 to 28": 8 is below the bare-number floor (list ordinals / small counts), 28 extracted.
    tokens = extract_numeric_tokens("Scaled the team from 8 to 28 engineers.")
    assert tokens == ["28"]


def test_extract_skips_small_integers_and_keeps_years() -> None:
    assert extract_numeric_tokens("Led 3 teams across 2 regions.") == []
    assert "2017" in extract_numeric_tokens("From 2017-04 onward.")


def test_extract_no_tokens_in_qualitative_text() -> None:
    assert extract_numeric_tokens("Directed enterprise platform modernization programs.") == []


# ---------------------------------------------------------------------------
# Normalization equivalence
# ---------------------------------------------------------------------------


def test_normalize_currency_equivalence_12m() -> None:
    # $12M == $12,000,000 (usd) and 12 million (count) share magnitude "12000000".
    assert normalize_numeric_token("$12M") == ("12000000", "usd")
    assert normalize_numeric_token("$12,000,000") == ("12000000", "usd")
    assert normalize_numeric_token("12 million") == ("12000000", "count")


def test_normalize_percent_and_multiplier() -> None:
    assert normalize_numeric_token("20%") == ("20", "pct")
    assert normalize_numeric_token("20 percent") == ("20", "pct")
    assert normalize_numeric_token("3x") == ("3", "x")


def test_normalize_invalid_token_returns_none() -> None:
    assert normalize_numeric_token("") is None
    assert normalize_numeric_token("ARR") is None


# ---------------------------------------------------------------------------
# Entailment check (magnitude + unit compatibility)
# ---------------------------------------------------------------------------


def test_entailment_currency_matches_worded_and_digit_forms() -> None:
    for corpus in ("generated $12M in new ARR", "generated $12,000,000 ARR", "12 million in ARR"):
        entailed, missing = numeric_entailment_check("Delivered $12M ARR uplift.", corpus)
        assert entailed is True, corpus
        assert missing == []


def test_entailment_percent_only_matches_percent() -> None:
    entailed, missing = numeric_entailment_check("Cut spend 20%.", "saved $20 per seat")
    assert entailed is False
    assert missing == ["20%"]
    entailed2, _ = numeric_entailment_check("Cut spend 20 percent.", "drove 20% savings")
    assert entailed2 is True


def test_entailment_fabricated_magnitude_fails_with_missing_tokens() -> None:
    entailed, missing = numeric_entailment_check(
        "Generated $25M pipeline at 40% margin.",
        "Pipeline analytics generating $12M new ARR",
    )
    assert entailed is False
    assert "$25M" in missing
    assert "40%" in missing


def test_entailment_no_numeric_claims_is_entailed() -> None:
    entailed, missing = numeric_entailment_check(
        "Led enterprise platform modernization.", "any corpus text"
    )
    assert entailed is True
    assert missing == []


# ---------------------------------------------------------------------------
# Corpus build — provenance + fail-open
# ---------------------------------------------------------------------------

_IBM_PLAN_FACTS = [
    {
        "fact_id": "bul_ibm_004",
        "claim_text": "Built budget and delivery-status BI views for executive portfolio decisions.",
        "metric_raw": "",
        "has_metric": False,
    },
    {
        "fact_id": "bul_ibm_005",
        "claim_text": "Led IBM-AWS alliance co-sell frameworks that expanded joint revenue.",
        "metric_raw": "20% joint revenue growth",
        "has_metric": True,
    },
]


def test_corpus_build_fail_open_on_missing_or_malformed_plan() -> None:
    assert build_slot_entailment_corpus("unify_bullets", None) == {}
    assert build_slot_entailment_corpus("unify_bullets", {}) == {}
    assert build_slot_entailment_corpus("unify_bullets", {"facts": "not-a-list"}) == {}


def test_corpus_build_unknown_lane_uses_fact_text_only() -> None:
    corpus = build_slot_entailment_corpus(
        "ey_bullets",
        {"facts": [{"fact_id": "bul_ey_001", "claim_text": "Audit delivery.", "metric_raw": "30%"}]},
    )
    assert corpus == {"bul_ey_001": "Audit delivery. 30%"}


def test_corpus_build_unify_includes_fact_and_bundle_non_metric_text() -> None:
    from apps_rg.runtime.sections.unify_graph_role_episode_registry import get_bundle_by_id
    from apps_rg.runtime.sections.unify_role_episode_evidence import UNIFY_BULLET_SLOT_BUNDLE_MAP

    plan = {
        "facts": [
            {
                "fact_id": "bul_unify_001",
                "claim_text": "Architected the agentic AI platform spine.",
                "metric_raw": "",
            }
        ]
    }
    corpus = build_slot_entailment_corpus("unify_bullets", plan)
    assert "bul_unify_001" in corpus
    assert "Architected the agentic AI platform spine." in corpus["bul_unify_001"]
    bundle = get_bundle_by_id(UNIFY_BULLET_SLOT_BUNDLE_MAP["bul_unify_001"])
    assert bundle is not None
    assert str(bundle.get("operating_context") or "") in corpus["bul_unify_001"]


def test_unify_slot_bundle_map_is_distinct_per_slot() -> None:
    """Unify needs no shared-bundle metric restriction equivalent: one bundle per slot."""
    from apps_rg.runtime.sections.unify_role_episode_evidence import UNIFY_BULLET_SLOT_BUNDLE_MAP

    values = list(UNIFY_BULLET_SLOT_BUNDLE_MAP.values())
    assert len(set(values)) == len(values)


# ---------------------------------------------------------------------------
# MANDATORY regression — ibm shared-bundle metric leak (closeout2 evidence)
# ---------------------------------------------------------------------------


def test_ibm_bundle_metric_id_does_not_leak_into_unmet_slot_corpus() -> None:
    """IBM graph metric IDs are metadata; visible metric proof comes from the slot fact."""
    corpus = build_slot_entailment_corpus("ibm_bullets", {"facts": _IBM_PLAN_FACTS})
    assert set(corpus) == {"bul_ibm_004", "bul_ibm_005"}

    # Slot 004's corpus carries neither the alliance metric text nor the metric outcome id token.
    blob_004 = corpus["bul_ibm_004"].lower()
    assert "20%" not in blob_004
    assert "metric_ibm_20pct_joint_revenue_growth" not in blob_004
    assert "joint revenue growth" not in blob_004


def test_ibm_sibling_slot_20pct_claim_not_entailed_own_slot_entailed() -> None:
    corpus = build_slot_entailment_corpus("ibm_bullets", {"facts": _IBM_PLAN_FACTS})
    drifted_bullet = "Built portfolio BI views generating 20% joint revenue growth."

    # Sibling-slot drift: 004's own fact has no 20% — the graph bundle must not entail it.
    entailed_004, missing_004 = numeric_entailment_check(drifted_bullet, corpus["bul_ibm_004"])
    assert entailed_004 is False
    assert "20%" in missing_004

    # Own-slot metric: 005's fact metric_raw carries 20% — entailed.
    entailed_005, missing_005 = numeric_entailment_check(
        "Led IBM-AWS co-sell frameworks generating 20% joint revenue growth.", corpus["bul_ibm_005"]
    )
    assert entailed_005 is True
    assert missing_005 == []
