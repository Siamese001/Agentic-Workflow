"""W2 — Brown SVP gap hardening (non-stock openers, S5 weave, C0 framing, judge variance)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.prompt_assembly.e0_examples import example_after_text
from apps_rg.runtime.sections.executive_summary_evidence_capsule import (
    PREFERRED_DISPLAY_FRAMING_BY_FACT_ID,
    build_capsule_document,
    format_evidence_capsule_c0_block,
)
from apps_rg.runtime.sections.executive_summary_judge_variance import (
    JUDGE_SCORE_VARIANCE_THRESHOLD,
    build_judge_score_variance_receipt,
    emit_judge_score_variance_if_dual_panel,
)
from apps_rg.runtime.sections.executive_summary_synthesis_contract import (
    APPROVED_NON_STOCK_OPENERS,
)
from apps_rg.runtime.validators.executive_summary_x2 import (
    check_exec_summary_stock_bridge_count,
)

_REPO = Path(__file__).resolve().parents[3]
_TEMPLATE = (
    _REPO
    / "apps_rg"
    / "prompt_assembly"
    / "templates"
    / "executive_summary.generate_scratch_v1.yaml"
)


def test_template_contains_approved_non_stock_openers() -> None:
    text = _TEMPLATE.read_text(encoding="utf-8")
    assert "approved_non_stock_openers" in text
    assert "From that commercial base" in text
    assert APPROVED_NON_STOCK_OPENERS[0] in text


def test_y0_positive_s5_quant_weave_guidance() -> None:
    text = _TEMPLATE.read_text(encoding="utf-8")
    assert "fact_quant_hpc_003" in text
    assert "FSA-chartered" in text
    assert "quantitative foundation" in text
    assert "Positive S5 weave" in text


def test_e0_positive_s5_pairs_fsa_with_hpc_metric() -> None:
    """SVP positive S5 must have a quantitative-foundation + operational-metric pairing.

    Since W1 (retired_provider-prompt-regen-reduction-7481e3), real metrics ($22M/40%) are replaced
    with domain-transposed placeholders so RetiredProvider cannot anchor to candidate-specific values.
    The test now verifies structural intent: quantitative credential + measurable outcome
    language is present, and the forbidden 'derivatives pricing' phrase is absent.
    """
    prose = example_after_text("executive_summary", "exec_summary_pos_svp_it_strategy_001")
    low = prose.lower()
    # S5 must have quantitative/credential language
    assert "quantitative" in low or "credential" in low or "chartered" in low or "fsa" in low, (
        "S5 in SVP positive must contain quantitative/credential language."
    )
    # S5 must pair with an operational-outcome phrase (placeholder or real)
    has_metric_phrase = (
        "%" in prose  # percent placeholder like [Z]% is fine
        or "shortening" in low
        or "improved" in low
        or "reduced" in low
        or "cycle" in low
    )
    assert has_metric_phrase, "S5 in SVP positive must reference a measurable operational outcome."
    # Forbidden phrase must never appear in any positive example
    assert "derivatives pricing" not in low, (
        "S5 must not contain 'derivatives pricing' in the positive example."
    )


def test_stock_bridge_x2_gate_id_registered_in_run_x2_gates() -> None:
    from apps_rg.runtime.validators.executive_summary_x2 import run_x2_gates

    text = (
        "Enterprise technology leader opening thesis for regulated scale. "
        "From that base, platform work scaled. "
        "Complementing that delivery, governance improved. "
        "Building on that foundation, revenue grew. "
        "In parallel, HPC shortened cycles. "
        "Forward capstone closing the arc."
    )
    gates = run_x2_gates(
        resume_display_text=text,
        parsed_output={
            "executive_strategy_thesis": "Thesis.",
            "resume_display_text": text,
            "claim_ledger": [{"claim": "c", "source_fact_ids": ["fact_exec_002"]}] * 6,
            "jd_alignment": {
                "targeting_only": True,
                "jd_used_as_proof": False,
                "briefing_used_as_proof": False,
                "graph_targeting": {
                    "release_eligible_targeting_proof": True,
                    "sqlite_projection_row_found": True,
                    "projection_source": "sqlite_role_family_projection",
                },
            },
        },
        claim_ledger=[{"claim": "c", "source_fact_ids": ["fact_exec_002"]}] * 6,
        text_claim_coverage={"sentences": [], "overall_pass": True},
        allowed_fact_ids={"fact_exec_002"},
        target_company="Acme",
        jd_text="jd",
        temperature=0.0,
        runtime_generation_status="REAL_LLM",
        monolithic_prompt_invoked=False,
        strategic_tailor_v1_invoked=False,
        target_role="SVP IT Strategy & Innovation",
        selected_facts=[{"fact_id": "fact_exec_002", "claim_text": "Scale."}],
    )
    gate_ids = [g.gate_id for g in gates]
    assert "x2_exec_summary_stock_bridge_max_two" in gate_ids
    failed = [g for g in gates if g.gate_id == "x2_exec_summary_stock_bridge_max_two" and not g.pass_]
    assert failed


def test_stock_bridge_lint_flags_three_bridges_in_s2_s5() -> None:
    text = (
        "S1 thesis sentence here. "
        "From that base, platform work scaled. "
        "Complementing that delivery, governance improved. "
        "Building on that foundation, revenue grew. "
        "In parallel, HPC shortened cycles. "
        "Forward capstone closes the arc."
    )
    ok, reason = check_exec_summary_stock_bridge_count(text, max_bridges=2)
    assert ok is False
    assert reason and "stock_bridge_stack" in reason


def test_c0_capsule_emits_preferred_display_framing_for_quant_fsa() -> None:
    capsule = build_capsule_document(
        runtime_payload={"proof_pool_metadata": {}},
        plan_facts=[
            {
                "fact_id": "fact_quant_hpc_003",
                "claim_text": "Built quantitative foundation through derivatives pricing and FSA.",
                "confidence": "HIGH",
            },
        ],
        allowed_ids=["fact_quant_hpc_003"],
        pool_context={},
    )
    row = capsule["facts"][0]
    assert row.get("preferred_display_framing") == PREFERRED_DISPLAY_FRAMING_BY_FACT_ID["fact_quant_hpc_003"]
    block = format_evidence_capsule_c0_block(capsule, ["fact_quant_hpc_003"])
    assert "preferred_display_framing=" in block
    assert "FSA-chartered" in block


def test_judge_variance_receipt_flags_delta_at_threshold(tmp_path: Path) -> None:
    prior = [
        {
            "provider_key": "gemini",
            "evaluator_mode": "MODEL_BACKED",
            "score": 4.5,
            "judge_packet_hash": "abc123",
        },
        {
            "provider_key": "openai",
            "evaluator_mode": "MODEL_BACKED",
            "score": 4.6,
            "judge_packet_hash": "abc123",
        },
    ]
    refreshed = [
        {
            "provider_key": "gemini",
            "evaluator_mode": "MODEL_BACKED",
            "score": 4.0,
            "judge_packet_hash": "abc123",
        },
        {
            "provider_key": "openai",
            "evaluator_mode": "MODEL_BACKED",
            "score": 4.4,
            "judge_packet_hash": "abc123",
        },
    ]
    receipt = build_judge_score_variance_receipt(
        prior_judges=prior,
        refreshed_judges=refreshed,
        judge_packet_hash="abc123",
    )
    assert receipt["dual_panel"] is True
    assert receipt["any_variance_flagged"] is True
    assert "gemini" in receipt["flagged_provider_keys"]
    assert receipt["variance_threshold"] == JUDGE_SCORE_VARIANCE_THRESHOLD

    written = emit_judge_score_variance_if_dual_panel(
        artifact_dir=tmp_path,
        prior_judges=prior,
        refreshed_judges=refreshed,
        judge_packet_hash="abc123",
    )
    assert written is not None
    on_disk = json.loads((tmp_path / "judge_score_variance_receipt.json").read_text(encoding="utf-8"))
    assert on_disk["any_variance_flagged"] is True
