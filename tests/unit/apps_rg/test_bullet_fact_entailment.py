"""W4.3 (G15/G17) — selection-time numeric fact-entailment unit coverage.

Deterministic, hermetic. No provider calls. Covers token extraction, magnitude/unit
normalization equivalence, per-slot corpus provenance (selected_fact_plan C0-pool facts +
bundle NON-metric text), fail-open behavior, and the ibm shared-bundle metric-leak
regression: bul_ibm_001-003 share ``reb_ibm_technical_presales_gtm`` whose
``linked_metric_outcome_ids`` carry ``metric_ibm_10m_arr`` — a $10M-class token from a
sibling slot's metric id must NOT entail for a slot whose own fact has no such metric.
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
    text = "Drove $10M ARR and $2.5 million savings, 20% growth, 3x throughput, 10 million events."
    tokens = extract_numeric_tokens(text)
    assert "$10M" in tokens
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


def test_normalize_currency_equivalence_10m() -> None:
    # $10M == $10,000,000 (usd) and 10 million (count) share magnitude "10000000".
    assert normalize_numeric_token("$10M") == ("10000000", "usd")
    assert normalize_numeric_token("$10,000,000") == ("10000000", "usd")
    assert normalize_numeric_token("10 million") == ("10000000", "count")


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
    for corpus in ("generated $10M in new ARR", "generated $10,000,000 ARR", "10 million in ARR"):
        entailed, missing = numeric_entailment_check("Delivered $10M ARR uplift.", corpus)
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
        "Salesforce pipeline analytics generating $10M new ARR",
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
        "fact_id": "bul_ibm_001",
        "claim_text": "Designed Salesforce pipeline analytics prioritizing high-potential deals.",
        "metric_raw": "$10M new ARR",
        "has_metric": True,
    },
    {
        "fact_id": "bul_ibm_002",
        "claim_text": "Deployed transparent budget and cost-optimization dashboards.",
        "metric_raw": "",
        "has_metric": False,
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


def test_ibm_shared_bundle_metric_id_does_not_leak_into_sibling_slot_corpus() -> None:
    """bul_ibm_001-003 share reb_ibm_technical_presales_gtm (linked_metric_outcome_ids =
    [metric_ibm_10m_arr]). The $10M magnitude must come ONLY from the slot's own fact
    metric_raw — never from the shared bundle's metric fields."""
    from apps_rg.runtime.sections.ibm_role_episode_evidence import IBM_BULLET_SLOT_BUNDLE_MAP

    assert IBM_BULLET_SLOT_BUNDLE_MAP["bul_ibm_001"] == IBM_BULLET_SLOT_BUNDLE_MAP["bul_ibm_002"]

    corpus = build_slot_entailment_corpus("ibm_bullets", {"facts": _IBM_PLAN_FACTS})
    assert set(corpus) == {"bul_ibm_001", "bul_ibm_002"}

    # Slot 002's corpus carries neither the raw metric text nor the metric outcome id token.
    blob_002 = corpus["bul_ibm_002"].lower()
    assert "$10m" not in blob_002
    assert "metric_ibm_10m_arr" not in blob_002
    assert "10m arr" not in blob_002


def test_ibm_sibling_slot_10m_claim_not_entailed_own_slot_entailed() -> None:
    corpus = build_slot_entailment_corpus("ibm_bullets", {"facts": _IBM_PLAN_FACTS})
    drifted_bullet = "Deployed cost dashboards generating $10M in new ARR."

    # Sibling-slot drift: 002's own fact has no $10M — the shared bundle must not entail it.
    entailed_002, missing_002 = numeric_entailment_check(drifted_bullet, corpus["bul_ibm_002"])
    assert entailed_002 is False
    assert "$10M" in missing_002

    # Own-slot metric: 001's fact metric_raw carries $10M — entailed.
    entailed_001, missing_001 = numeric_entailment_check(
        "Designed pipeline analytics generating $10M in new ARR.", corpus["bul_ibm_001"]
    )
    assert entailed_001 is True
    assert missing_001 == []
