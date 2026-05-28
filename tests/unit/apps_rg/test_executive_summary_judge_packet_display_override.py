"""Tests for judge-packet display-override parity (closes Bug:ExecSummaryJudgeDisplayOverrideInvisible).

Plan: exec-summary-judge-display-override-parity-7c3e8a (W3.2).

These tests would have caught the Brown & Brown SVP run full_resume_3976479ef871 Claude
soft-fail loop (3.6 -> 3.8 -> 3.8 stuck) which was caused by the L2/Qwen prompt receiving
FACT_C0_DISPLAY_OVERRIDES while the X1D judge packet only carried raw claim_text.
"""

from __future__ import annotations

import pytest

from apps_rg.runtime.judges.executive_summary_judge_packet import (
    GRADE_ONLY_INSTRUCTION,
    GRAPH_ONLY_GRADE_ONLY_RUBRIC,
    build_executive_summary_judge_packet,
    enrich_allowed_fact_packet_for_judges,
)
from apps_rg.runtime.sections.executive_summary_synthesis_contract import (
    DEPENDENCY_GRAPH_FACT_ID,
    FACT_C0_DISPLAY_OVERRIDES,
    FSA_CREDENTIAL_FACT_ID,
)
from apps_rg.runtime.validators.executive_summary_x2 import (
    check_judge_packet_display_override_parity,
)


def _raw_plan_facts() -> list[dict[str, object]]:
    return [
        {
            "fact_id": FSA_CREDENTIAL_FACT_ID,
            "claim_text": (
                "Built quantitative rigor through derivatives pricing, capital modeling, "
                "and portfolio stress analytics across early-career actuarial roles."
            ),
        },
        {
            "fact_id": DEPENDENCY_GRAPH_FACT_ID,
            "claim_text": (
                "Built and applied software dependency graph intelligence to accelerate "
                "legacy-system analysis, expose dependency chains, improve architecture "
                "visibility, and reduce refactor risk."
            ),
        },
        {
            "fact_id": "fact_governance_003",
            "claim_text": (
                "Implemented Basel III / CCAR data lineage, cataloging, and automated "
                "validation frameworks that cut regulatory reporting errors by 40%."
            ),
        },
    ]


def test_enricher_attaches_display_override_text_for_overridden_fact_ids() -> None:
    rows = enrich_allowed_fact_packet_for_judges(
        _raw_plan_facts(),
        {FSA_CREDENTIAL_FACT_ID, DEPENDENCY_GRAPH_FACT_ID, "fact_governance_003"},
    )
    by_fid = {str(r.get("fact_id")): r for r in rows}

    fsa_row = by_fid[FSA_CREDENTIAL_FACT_ID]
    assert fsa_row["display_override_text"] == FACT_C0_DISPLAY_OVERRIDES[FSA_CREDENTIAL_FACT_ID]
    assert fsa_row["display_substrate_authority"] == "union_claim_text_and_display_override_text"

    graph_row = by_fid[DEPENDENCY_GRAPH_FACT_ID]
    assert graph_row["display_override_text"] == FACT_C0_DISPLAY_OVERRIDES[DEPENDENCY_GRAPH_FACT_ID]

    gov_row = by_fid["fact_governance_003"]
    assert "display_override_text" not in gov_row, (
        "fact_governance_003 has no FACT_C0_DISPLAY_OVERRIDES entry; row must not carry override text"
    )


def test_parity_validator_passes_when_overrides_present() -> None:
    rows = enrich_allowed_fact_packet_for_judges(
        _raw_plan_facts(),
        {FSA_CREDENTIAL_FACT_ID, DEPENDENCY_GRAPH_FACT_ID},
    )
    ok, detail = check_judge_packet_display_override_parity(
        judge_allowed_fact_packet=rows,
        cited_fact_ids=[FSA_CREDENTIAL_FACT_ID, DEPENDENCY_GRAPH_FACT_ID],
    )
    assert ok is True
    assert detail is None


def test_parity_validator_fails_closed_when_override_stripped() -> None:
    rows = enrich_allowed_fact_packet_for_judges(
        _raw_plan_facts(),
        {FSA_CREDENTIAL_FACT_ID, DEPENDENCY_GRAPH_FACT_ID},
    )
    tampered = [
        {k: v for k, v in row.items() if k != "display_override_text"} for row in rows
    ]
    ok, detail = check_judge_packet_display_override_parity(
        judge_allowed_fact_packet=tampered,
        cited_fact_ids=[FSA_CREDENTIAL_FACT_ID, DEPENDENCY_GRAPH_FACT_ID],
    )
    assert ok is False
    assert detail is not None
    assert "judge_packet_missing_display_override_text" in detail
    assert FSA_CREDENTIAL_FACT_ID in detail
    assert DEPENDENCY_GRAPH_FACT_ID in detail


def test_parity_validator_skips_uncited_overrides() -> None:
    """An override defined in FACT_C0_DISPLAY_OVERRIDES but not cited must not fail the gate."""
    rows = enrich_allowed_fact_packet_for_judges(
        _raw_plan_facts(),
        {FSA_CREDENTIAL_FACT_ID, DEPENDENCY_GRAPH_FACT_ID},
    )
    ok, detail = check_judge_packet_display_override_parity(
        judge_allowed_fact_packet=rows,
        cited_fact_ids=["fact_governance_003"],
    )
    assert ok is True
    assert detail is None


def test_grade_only_instruction_documents_display_override_parity() -> None:
    assert "DISPLAY_OVERRIDE PARITY" in GRADE_ONLY_INSTRUCTION
    assert "union" in GRADE_ONLY_INSTRUCTION.lower()
    assert "display_override_text" in GRADE_ONLY_INSTRUCTION


def test_rubric_authorizes_override_phrases_in_factual_support_and_anti_overfit() -> None:
    rubric = GRAPH_ONLY_GRADE_ONLY_RUBRIC
    factual_section = rubric.split("2. executive_signal", 1)[0]
    assert "display_override_text" in factual_section, (
        "factual_support dimension must explicitly authorize display_override_text union"
    )
    assert "UNION" in factual_section
    anti_overfit_section = rubric.split("5. anti_overfit", 1)[1].split("6. synthesis_quality", 1)[0]
    assert "display_override_text" in anti_overfit_section


def test_full_packet_build_emits_parity_gate_in_deterministic_gate_summary() -> None:
    allowed_ids = {FSA_CREDENTIAL_FACT_ID, DEPENDENCY_GRAPH_FACT_ID, "fact_governance_003"}
    claim_ledger = [
        {
            "claim_text": "Some sentence citing FSA fact.",
            "source_fact_ids": [FSA_CREDENTIAL_FACT_ID],
        },
        {
            "claim_text": "Some sentence citing dependency graph.",
            "source_fact_ids": [DEPENDENCY_GRAPH_FACT_ID],
        },
    ]
    packet = build_executive_summary_judge_packet(
        resume_display_text="Stub display text for packet build test.",
        claim_ledger=claim_ledger,
        allowed_fact_packet=_raw_plan_facts(),
        allowed_fact_ids=allowed_ids,
        target_title="SVP IT Strategy & Innovation",
        target_company="Brown & Brown",
        jd_text="(targeting only)",
        briefing_text="(targeting only)",
        parsed_output={"resume_display_text": "stub"},
    )
    summary = packet.get("deterministic_gate_summary") or {}
    parity_gate = summary.get("x2_executive_summary_judge_packet_display_override_parity")
    assert isinstance(parity_gate, dict)
    assert parity_gate["pass"] is True
    assert parity_gate["detail"] == "ok"

    judge_rows_by_fid = {
        str(r.get("fact_id")): r for r in (packet.get("allowed_fact_packet") or [])
    }
    assert (
        judge_rows_by_fid[FSA_CREDENTIAL_FACT_ID]["display_override_text"]
        == FACT_C0_DISPLAY_OVERRIDES[FSA_CREDENTIAL_FACT_ID]
    )
    assert (
        judge_rows_by_fid[DEPENDENCY_GRAPH_FACT_ID]["display_override_text"]
        == FACT_C0_DISPLAY_OVERRIDES[DEPENDENCY_GRAPH_FACT_ID]
    )


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-v"]))
