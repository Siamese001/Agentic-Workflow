"""Unit tests for graph-only executive_summary quality repair."""

from __future__ import annotations

from apps_rg.runtime.sections.exec_summary_graph_only_quality import (
    _unsupported_margin_phrase_hit,
    apply_graph_only_generation_quality_repair,
    build_graph_only_executive_summary_from_facts,
    detect_graph_only_synthesis_violations,
)
from apps_rg.runtime.sections.executive_summary_composition import is_mechanism_inventory_sentence
from apps_rg.runtime.validators.executive_summary_x2 import (
    check_exec_summary_cross_sentence_metric_dedup,
    check_exec_summary_evidence_utilization,
    check_exec_summary_mechanical_opener_stack,
    check_synthesis_quality,
    split_sentences,
)


def _sample_facts() -> list[dict]:
    return [
        {
            "fact_id": "fact_engineering_platform_001",
            "claim_text": (
                "Designed and operationalized governed agentic AI platform capabilities "
                "for regulated enterprise workflows, including deterministic routing."
            ),
            "metric_raw": "",
        },
        {
            "fact_id": "fact_governance_003",
            "claim_text": (
                "Implemented Basel III / CCAR data lineage frameworks that cut "
                "regulatory reporting errors by 40%."
            ),
            "metric_raw": "40% reporting error reduction",
        },
        {
            "fact_id": "fact_exec_002",
            "claim_text": "Scaled ML engineering organization from 8 to 28 specialists.",
            "metric_raw": "team 8 to 28",
        },
    ]


def test_build_graph_only_summary_omits_gross_margin() -> None:
    allowed = {
        "fact_engineering_platform_001",
        "fact_governance_003",
        "fact_governance_003_metric_e5abeb74",
        "fact_exec_002",
        "fact_exec_002_metric_c880fce9",
    }
    resume, ledger = build_graph_only_executive_summary_from_facts(_sample_facts(), allowed)
    assert "gross margin" not in resume.lower()
    assert "40%" in resume
    assert "8 to 28" in resume or "8 to  28" in resume
    assert not any("Holds AWS" in resume for _ in [0])
    assert len(ledger) <= 4


def _seven_fact_pool() -> list[dict]:
    return [
        {
            "fact_id": "fact_exec_002",
            "claim_text": "Scaled ML engineering organization from 8 to 28 specialists.",
            "metric_raw": "team 8 to 28",
        },
        {
            "fact_id": "fact_engineering_platform_006",
            "claim_text": (
                "Productized agentic AI primitives, generating $22M in IP-led revenue "
                "and expanding gross margins by 20%."
            ),
            "metric_raw": "$22M IP-led revenue|20% gross margin expansion",
        },
        {
            "fact_id": "fact_certs_001",
            "claim_text": "Holds AWS Certified Machine Learning Engineer credentials.",
            "metric_raw": "",
        },
        {
            "fact_id": "fact_engineering_platform_001",
            "claim_text": "Designed governed agentic AI platforms for regulated workflows.",
            "metric_raw": "",
        },
        {
            "fact_id": "fact_governance_003",
            "claim_text": "Implemented Basel III / CCAR data lineage that cut reporting errors by 40%.",
            "metric_raw": "40% reporting error reduction",
        },
        {
            "fact_id": "fact_quant_hpc_001",
            "claim_text": "Re-architected risk analytics with HPC, trimming cycles by 40%.",
            "metric_raw": "40% faster calculations / stress testing",
        },
        {
            "fact_id": "fact_quant_hpc_003",
            "claim_text": "Built quantitative foundation through derivatives pricing.",
            "metric_raw": "",
        },
    ]


def test_build_graph_only_passes_mechanism_inventory_on_opener() -> None:
    allowed = {str(row["fact_id"]) for row in _seven_fact_pool()}
    resume, _ledger = build_graph_only_executive_summary_from_facts(_seven_fact_pool(), allowed)
    sents = split_sentences(resume)
    assert len(sents) >= 4
    inv, reason = is_mechanism_inventory_sentence(sents[0])
    assert inv is False, reason


def test_build_graph_only_no_duplicate_team_scale_metric() -> None:
    allowed = {str(row["fact_id"]) for row in _seven_fact_pool()}
    resume, _ledger = build_graph_only_executive_summary_from_facts(_seven_fact_pool(), allowed)
    dedup_ok, dedup_reason = check_exec_summary_cross_sentence_metric_dedup(resume)
    assert dedup_ok, dedup_reason
    assert resume.lower().count("8 to 28") <= 1


def test_build_graph_only_passes_synthesis_and_mechanical_opener_gates() -> None:
    allowed = {str(row["fact_id"]) for row in _seven_fact_pool()}
    resume, _ledger = build_graph_only_executive_summary_from_facts(_seven_fact_pool(), allowed)
    stack_ok, stack_reason = check_exec_summary_mechanical_opener_stack(resume)
    assert stack_ok, stack_reason
    synth_ok, synth_reason = check_synthesis_quality(resume)
    assert synth_ok, synth_reason


def test_build_graph_only_five_ledger_rows_when_pool_seven() -> None:
    allowed = {str(row["fact_id"]) for row in _seven_fact_pool()}
    _resume, ledger = build_graph_only_executive_summary_from_facts(_seven_fact_pool(), allowed)
    assert len(ledger) >= 5
    util_ok, util_reason = check_exec_summary_evidence_utilization(
        _resume,
        {"claim_ledger": ledger},
        selected_facts=_seven_fact_pool(),
    )
    assert util_ok, util_reason


def test_apply_repair_opener_only_skips_full_rewrite() -> None:
    allowed = {
        "fact_engineering_platform_001",
        "fact_governance_003",
        "fact_exec_002",
    }
    parsed = {
        "resume_display_text": (
            "Led the implementation of automated validation frameworks, reducing errors by 40%. "
            "Built advanced quantitative foundations through derivatives pricing. "
            "Also delivered platform services with deterministic routing. "
            "Successfully scaled engineering programs across regulated workflows. "
            "Delivered measurable outcomes across enterprise platform programs. "
            "Generated measurable platform outcomes across regulated delivery."
        ),
        "claim_ledger": [{"claim_text": "x", "source_fact_ids": ["fact_governance_003"]}],
    }
    repaired, meta = apply_graph_only_generation_quality_repair(
        parsed,
        allowed_fact_ids=allowed,
        plan_facts=_sample_facts(),
    )
    assert meta.get("repair_kind") == "opener_normalize_only"
    assert meta.get("applied") is True
    assert "Led the" not in str(repaired.get("resume_display_text") or "")


def test_apply_repair_strips_hallucinated_margin() -> None:
    allowed = {
        "fact_engineering_platform_001",
        "fact_governance_003",
        "fact_governance_003_metric_e5abeb74",
        "fact_exec_002",
        "fact_exec_002_metric_c880fce9",
    }
    parsed = {
        "resume_display_text": (
            "Platform leader. Built systems leading to 40% error reduction and "
            "20% expansion in gross margins. Scaled team improving reliability; "
            "Holds AWS Certified Machine Learning Engineer credentials."
        ),
        "claim_ledger": [
            {
                "claim_text": "Merged claim leading to 40% and 20% gross margins",
                "source_fact_ids": [
                    "fact_engineering_platform_001",
                    "fact_governance_003",
                ],
            }
        ],
    }
    repaired, meta = apply_graph_only_generation_quality_repair(
        parsed,
        allowed_fact_ids=allowed,
        plan_facts=_sample_facts(),
    )
    assert meta["had_unsupported_gross_margin"] is True
    assert "gross margin" not in str(repaired.get("resume_display_text") or "").lower()
    assert "20%" not in str(repaired.get("resume_display_text") or "")


# --- Support-aware had_unsupported_gross_margin regression pins -------------------------
# Live incident (attempt4_20260610_2329 + patch-run-2, identical claim_ledger row-2 orphan):
# the flag was unconditional, so a fact-SUPPORTED "expanding gross margins by 20%" clause in
# S3 was deleted by the margin sanitizer, gutting the sentence; the post-chain ledger rebuild
# orphaned claim_ledger[2] and 11 derived X2 gates failed. The fix makes the flag support-aware
# (margin echo trips only when the allowed fact pool lacks margin support). Unsupported margin
# echoes MUST still trip — gate correctness preserved, nothing weakened.

_MARGIN_DISPLAY = (
    "Building on that platform foundation, platform revenue outcomes generated $22M in "
    "IP-led revenue and expanded gross margins by 20% while scaling the ML engineering "
    "organization from 8 to 28 specialists."
)

_MARGIN_SUPPORTED_FACT = {
    "fact_id": "fact_engineering_platform_006",
    "claim_text": (
        "Productized agentic AI primitives, generating $22M in IP-led revenue "
        "and expanding gross margins by 20%."
    ),
    "metric_raw": "$22M IP-led revenue|20% gross margin expansion",
}


def test_margin_flag_false_when_fact_pool_supports_margin() -> None:
    """(a) Supported case: margin echo backed by the allowed fact pool must NOT trip the flag."""
    facts = [_MARGIN_SUPPORTED_FACT, *_sample_facts()]
    allowed = {str(f["fact_id"]) for f in facts}
    parsed = {
        "resume_display_text": _MARGIN_DISPLAY,
        "claim_ledger": [
            {
                "claim_text": _MARGIN_DISPLAY,
                "source_fact_ids": ["fact_engineering_platform_006"],
            }
        ],
    }
    _needs, flags = detect_graph_only_synthesis_violations(
        parsed, allowed_fact_ids=allowed, plan_facts=facts
    )
    assert flags["had_unsupported_gross_margin"] is False
    # 20% is fact-backed via metric_raw -> not an unsupported percent token either.
    assert "20%" not in (flags.get("unsupported_percent_tokens") or [])


def test_margin_flag_true_when_fact_pool_lacks_margin_support() -> None:
    """(b) Unsupported case: same display text, no margin support in pool -> flag still trips."""
    facts = _sample_facts()  # no margin text in any claim_text/metric_raw
    allowed = {str(f["fact_id"]) for f in facts}
    parsed = {
        "resume_display_text": _MARGIN_DISPLAY,
        "claim_ledger": [
            {
                "claim_text": _MARGIN_DISPLAY,
                "source_fact_ids": ["fact_engineering_platform_001"],
            }
        ],
    }
    _needs, flags = detect_graph_only_synthesis_violations(
        parsed, allowed_fact_ids=allowed, plan_facts=facts
    )
    assert flags["had_unsupported_gross_margin"] is True
    # Repair must still remove the unsupported margin echo from the display text.
    out, meta = apply_graph_only_generation_quality_repair(
        parsed, allowed_fact_ids=allowed, plan_facts=facts
    )
    assert meta["had_unsupported_gross_margin"] is True
    assert "gross margin" not in str(out.get("resume_display_text") or "").lower()


def test_margin_flag_fail_closed_on_empty_fact_pool() -> None:
    """(c) Empty facts -> no support blob -> unsupported -> flag trips (fail-closed)."""
    assert _unsupported_margin_phrase_hit(_MARGIN_DISPLAY, []) is True
    # Helper-level supported/unsupported A-B on identical text.
    assert _unsupported_margin_phrase_hit(_MARGIN_DISPLAY, [_MARGIN_SUPPORTED_FACT]) is False
    assert _unsupported_margin_phrase_hit(_MARGIN_DISPLAY, _sample_facts()) is True


def test_supported_margin_clause_survives_repair_seam() -> None:
    """End-to-end incident pin: builder emits the supported margin clause; the repair seam
    (commercialization-thread sanitize + re-detect) must NOT delete it, so the claim ledger
    keeps binding (attempt4 row-2 orphan -> 11-gate echo)."""
    facts = _seven_fact_pool()
    allowed = {str(row["fact_id"]) for row in facts}
    resume, ledger = build_graph_only_executive_summary_from_facts(facts, allowed)
    assert "gross margins by 20%" in resume  # precondition: supported clause present in S-band
    parsed = {"resume_display_text": resume, "claim_ledger": ledger}
    out, meta = apply_graph_only_generation_quality_repair(
        parsed, allowed_fact_ids=allowed, plan_facts=facts
    )
    assert meta["had_unsupported_gross_margin"] is False
    after = str(out.get("resume_display_text") or "")
    assert "gross margins by 20%" in after
    assert "$22M" in after
    assert len(out.get("claim_ledger") or []) >= 1
