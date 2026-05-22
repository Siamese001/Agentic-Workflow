"""IBM narrative display contracts: meta-disclaimer ban and clause-level ledger."""

from __future__ import annotations

from apps_rg.runtime.validators.ibm_narrative_x2 import (
    check_ibm_narrative_claim_ledger_clause_decomposition,
    run_ibm_narrative_x2_gates,
)
from apps_rg.runtime.validators.resume_narrative_display_x2 import (
    check_ibm_narrative_no_meta_disclaimer_in_display,
)


def test_meta_disclaimer_patterns_fail_display_gate():
    bad_samples = [
        "At IBM, led cloud work without claiming IBM delivered agentic products.",
        "At IBM, led cloud work without asserting IBM shipped agentic platform products.",
        "At IBM, led cloud work, not claiming IBM built agentic platforms.",
        "At IBM, led cloud work, not asserting IBM built agentic platforms.",
        "At IBM, led cloud work and did not claim IBM delivered agentic products.",
        "At IBM, led cloud work and did not assert IBM delivered agentic products.",
    ]
    for sample in bad_samples:
        ok, hits = check_ibm_narrative_no_meta_disclaimer_in_display(sample)
        assert ok is False, sample
        assert hits


def test_clean_narrative_passes_meta_disclaimer_gate():
    good = (
        "At IBM, led enterprise-scale cloud, data, lineage, and observability foundations for regulated "
        "financial services, establishing reliability and governance discipline for governed analytics delivery."
    )
    ok, hits = check_ibm_narrative_no_meta_disclaimer_in_display(good)
    assert ok is True
    assert not hits


def test_clause_decomposition_rejects_career_bridge_and_loose_union():
    narrative = (
        "At IBM, led cloud foundations, establishing discipline that supported later production AI "
        "platform leadership in subsequent roles."
    )
    ledger = [
        {
            "claim_text": narrative,
            "source_fact_ids": ["bul_ibm_001", "bul_ibm_002", "bul_ibm_003", "bul_ibm_004"],
        }
    ]
    ok, detail = check_ibm_narrative_claim_ledger_clause_decomposition(narrative, ledger)
    assert ok is False
    assert detail.get("reason") in {
        "career_bridge_phrase_without_allowed_fact_class",
        "loose_source_fact_id_union",
        "multi_clause_sentence_requires_multiple_ledger_rows",
    }


def test_clause_decomposition_accepts_per_clause_rows():
    narrative = (
        "At IBM, led enterprise-scale cloud, data, lineage, and observability foundations for regulated "
        "financial services, establishing reliability and governance discipline for governed analytics delivery."
    )
    ledger = [
        {
            "claim_text": (
                "At IBM, led enterprise-scale cloud, data, lineage, and observability foundations "
                "for regulated financial services"
            ),
            "source_fact_ids": ["bul_ibm_001", "bul_ibm_004"],
        },
        {
            "claim_text": "establishing reliability and governance discipline for governed analytics delivery",
            "source_fact_ids": ["bul_ibm_003"],
        },
    ]
    ok, detail = check_ibm_narrative_claim_ledger_clause_decomposition(narrative, ledger)
    assert ok is True
    assert detail.get("reason") == "ok"


def test_x2_gate_ids_include_meta_disclaimer_and_clause_decomposition():
    gates = run_ibm_narrative_x2_gates(
        narrative_sentence=(
            "At IBM, led enterprise-scale cloud, data, lineage, and observability foundations for regulated "
            "financial services, establishing reliability and governance discipline for governed analytics delivery."
        ),
        parsed_output={},
        claim_ledger=[
            {
                "claim_text": (
                    "At IBM, led enterprise-scale cloud, data, lineage, and observability foundations "
                    "for regulated financial services"
                ),
                "source_fact_ids": ["bul_ibm_001", "bul_ibm_004"],
            },
            {
                "claim_text": "establishing reliability and governance discipline for governed analytics delivery",
                "source_fact_ids": ["bul_ibm_003"],
            },
        ],
        jd_text="",
        runtime_generation_status="MOCKED",
        companion_bullet_texts="",
        companion_bullets_status="MISSING",
        companion_aware=False,
    )
    gate_ids = {g.gate_id for g in gates}
    assert "x2_ibm_narrative_no_meta_disclaimer_in_display" in gate_ids
    assert "x2_ibm_narrative_claim_ledger_clause_decomposition" in gate_ids
    assert "x2_ibm_narrative_requires_finalized_bullets" in gate_ids
