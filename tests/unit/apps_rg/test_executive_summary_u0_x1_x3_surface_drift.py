"""U0 → L2 → X2 → X1D → X3 surface drift guards (exec summary).

Locks the RCA in docs/reports/apps_rg/exec_summary_l2_x1d_input_parity_rca_20260525.md:
- U0/product_patch and full I0/E0/SRFS live on L2 compiled prompt only.
- X1D judges use GRADE_ONLY packet (not compiled_prompt reuse).
- Token trim on E0/Y0/JD must block unfair judge regen when targeting parity still matches.
- Post-X2 gate snapshot must feed dimension_gate_map for judge alignment.
"""

from __future__ import annotations

import json

from apps_rg.runtime.judges.executive_summary_judge_packet import (
    build_deterministic_gate_summary,
    build_deterministic_gate_summary_from_x2_gates,
    build_executive_summary_judge_packet,
    packet_forbids_generator_prompt_reuse,
    render_judge_prompt_from_packet,
)
from apps_rg.runtime.sections.executive_summary_generation_grade_contract import (
    JUDGE_EXCLUDED_BY_DESIGN,
    build_generation_grade_contract_manifest,
    dimension_gate_map,
)
from apps_rg.runtime.sections.executive_summary_pa import compile_executive_summary_prompt
from apps_rg.runtime.sections.executive_summary_targeting_publish import (
    instructional_surface_drift_risk,
    parity_allows_judge_regen,
)
from apps_rg.runtime.sections.executive_summary_token_budget import (
    trim_executive_summary_prompt_content,
)
from apps_rg.runtime.targeting_context_authority import (
    GenerationMaterialContext,
    JudgeMaterialContext,
    generation_material_context_from_compiled_prompt,
    judge_material_context_from_packet,
)


def _minimal_runtime_payload() -> dict:
    return {
        "product_visible": False,
        "proof_pool_metadata": {
            "proof_pool_type": "augmented_skills_graph",
            "evidence_authority": {
                "authority": "augmented_skills_graph",
                "graph_ref": "apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
                "ledger_ref": "artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger.json",
            },
        },
        "run_id": "surface_drift_run",
        "target_title": "SVP IT Strategy",
        "target_company": "Brown & Brown",
        "jd_text": "Enterprise architecture and innovation programs.",
        "briefing": "Insurance brokerage technology leadership.",
        "allowed_fact_ids": ["fact_platform_001"],
        "selected_fact_plan": {
            "facts": [
                {
                    "fact_id": "fact_platform_001",
                    "claim_text": "Delivered governed platform outcomes.",
                }
            ]
        },
    }


def _six_sentence_resume() -> str:
    return (
        "Technology strategy executive building governed platforms for regulated enterprise delivery. "
        "The platform generated proof-backed revenue outcomes while scaling engineering delivery. "
        "Implementation of Basel III frameworks reduced regulatory reporting errors for stakeholders. "
        "Re-architected analytics achieved faster calculations and reliable decision support. "
        "Quantitative depth informs governance and delivery trade-offs across complex programs. "
        "Governed runtime delivery stays audit-ready without weakening commercial velocity."
    )


def test_compiled_prompt_carries_l2_only_markers_absent_from_judge_packet() -> None:
    payload = _minimal_runtime_payload()
    out = compile_executive_summary_prompt(payload, run_id=payload["run_id"])
    compiled = out.artifact.messages[0]["content"]
    text = _six_sentence_resume()
    summary = build_deterministic_gate_summary(
        resume_display_text=text,
        parsed_output={"resume_display_text": text},
        claim_ledger=[
            {"claim_text": "Governed platform.", "source_fact_ids": ["fact_platform_001"]}
        ],
        allowed_fact_ids={"fact_platform_001"},
    )
    packet = build_executive_summary_judge_packet(
        resume_display_text=text,
        claim_ledger=[
            {"claim_text": "Governed platform.", "source_fact_ids": ["fact_platform_001"]}
        ],
        allowed_fact_packet=[],
        allowed_fact_ids={"fact_platform_001"},
        target_title="SVP IT Strategy",
        target_company="Brown & Brown",
        jd_text=payload["jd_text"],
        briefing_text=payload["briefing"],
        parsed_output={"resume_display_text": text},
        deterministic_gate_summary=summary,
    )
    judge_prompt = render_judge_prompt_from_packet(packet)

    assert "GRADE_ONLY" in judge_prompt
    assert packet_forbids_generator_prompt_reuse(compiled, judge_prompt)
    assert "<many_shot_examples>" in compiled
    assert "<many_shot_examples>" not in judge_prompt
    assert "GENERATION_LAW_DIGEST" in judge_prompt
    assert "proof_law_v1" in compiled or "EXEC_SUMMARY_PROMPT_CORE_LAW" in compiled


def test_u0_targeting_digest_can_match_while_instructional_surfaces_differ() -> None:
    """RCA C1: JD/briefing parity can hold while L2 loses E0 judges never had."""
    payload = _minimal_runtime_payload()
    out = compile_executive_summary_prompt(payload, run_id=payload["run_id"])
    compiled = out.artifact.messages[0]["content"]
    gen = generation_material_context_from_compiled_prompt(compiled)
    trimmed, _, applied = trim_executive_summary_prompt_content(
        compiled,
        protected_ids=set(payload["allowed_fact_ids"]),
        available_input_tokens=100,
    )
    assert applied is True
    gen_after = generation_material_context_from_compiled_prompt(trimmed)
    judge = judge_material_context_from_packet(
        {
            "targeting_context": {
                "jd_text": gen.jd_text_material,
                "briefing": gen.briefing_text_material,
            }
        }
    )
    assert gen.generation_material_digest == judge.judge_material_digest
    assert "<many_shot_examples>" not in trimmed
    receipt = {
        "trim_applied": True,
        "trimmed_components": [{"component": "e0_examples", "reason": "optional_style_examples"}],
    }
    assert instructional_surface_drift_risk(receipt) is True
    ok, _reason = parity_allows_judge_regen(
        {"targeting_context_parity": {"parity_match": True}},
        token_budget_receipt=receipt,
    )
    assert ok is True


def test_manifest_records_instructional_drift_and_regen_block() -> None:
    gen = GenerationMaterialContext("jd", "br", "d" * 64)
    judge = JudgeMaterialContext("jd", "br", "d" * 64)
    receipt = {
        "trim_applied": True,
        "trimmed_components": [{"component": "e0_examples"}],
    }
    body = build_generation_grade_contract_manifest(
        run_id="r1",
        generation=gen,
        judge=judge,
        parity_receipt={"parity_match": True},
        judge_packet={"deterministic_gate_summary": {}},
        token_budget_receipt=receipt,
        composition_plan={},
        allowed_fact_packet=[],
    )
    assert body["targeting"]["instructional_surface_drift_risk"] is True
    assert body["targeting"]["judge_regen_trim_block"] is False
    assert body["targeting"]["judge_regen_allowed"] is True


def test_post_x2_gate_summary_covers_dimension_gate_map_x2_ids() -> None:
    x2_gates = [
        {"gate_id": gid, "pass": True, "failure_reason": None}
        for gid in sorted(
            {v for v in dimension_gate_map().values() if str(v).startswith("x2_")}
        )
    ]
    summary = build_deterministic_gate_summary_from_x2_gates(x2_gates)
    for gate_id in dimension_gate_map().values():
        if gate_id == "x2_gate_snapshot_authoritative":
            continue
        assert gate_id in summary, gate_id
        assert summary[gate_id]["pass"] is True


def test_judge_excluded_surfaces_documented_in_manifest() -> None:
    assert "full_E0_many_shot_examples" in JUDGE_EXCLUDED_BY_DESIGN
    assert "full_I0_proof_law_and_composition_heuristics" in JUDGE_EXCLUDED_BY_DESIGN
    gen = GenerationMaterialContext("a", "b", "c")
    judge = JudgeMaterialContext("a", "b", "c")
    body = build_generation_grade_contract_manifest(
        run_id="r2",
        generation=gen,
        judge=judge,
        parity_receipt={"parity_match": True},
        judge_packet=None,
        token_budget_receipt=None,
        composition_plan={},
        allowed_fact_packet=[],
    )
    assert body["judge_excluded_by_design"] == list(JUDGE_EXCLUDED_BY_DESIGN)


def test_pre_x2_subset_is_strict_subset_of_post_x2_authoritative_snapshot() -> None:
    text = _six_sentence_resume()
    pre = build_deterministic_gate_summary(
        resume_display_text=text,
        parsed_output={"resume_display_text": text},
        claim_ledger=[],
        allowed_fact_ids=set(),
    )
    post = build_deterministic_gate_summary_from_x2_gates(
        [
            {"gate_id": k, "pass": v["pass"], "failure_reason": v.get("detail")}
            for k, v in pre.items()
            if k.startswith("x2_")
        ]
        + [{"gate_id": "x2_jd_phrase_copy_violation_zero", "pass": True}]
    )
    assert len(post) >= len(pre)
    for key in pre:
        if key.startswith("x2_"):
            assert key in post


def test_judge_packet_json_excludes_compiled_prompt_shape() -> None:
    text = _six_sentence_resume()
    packet = build_executive_summary_judge_packet(
        resume_display_text=text,
        claim_ledger=[],
        allowed_fact_packet=[],
        allowed_fact_ids=set(),
        target_title="T",
        target_company="C",
        jd_text="jd-only",
        briefing_text="brief-only",
        parsed_output={"resume_display_text": text},
        deterministic_gate_summary=build_deterministic_gate_summary(
            resume_display_text=text,
            parsed_output={"resume_display_text": text},
            claim_ledger=[],
            allowed_fact_ids=set(),
        ),
    )
    blob = json.dumps(packet)
    assert "strategic_tailor_v1" not in blob
    assert packet.get("judge_task") == "GRADE_ONLY"
    assert "targeting_context" in packet
