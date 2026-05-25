"""L2 vs X1D input parity invariants (exec-summary-l2-x1d-input-parity-c4f8e1)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.prompt_assembly.e0_examples import (
    _EXEC_SUMMARY_POSITIVE_COMPILE_IDS,
    build_executive_summary_e0,
)
from apps_rg.runtime.judges.executive_summary_judge_packet import (
    build_deterministic_gate_summary,
    build_deterministic_gate_summary_from_x2_gates,
    build_executive_summary_judge_packet,
    render_judge_prompt_from_packet,
)
from apps_rg.runtime.validators.executive_summary_x2 import (
    POST_X2_X1D_WIRING_GATE_IDS,
    check_x1d_judge_packet_hash_uniform,
)
from apps_rg.runtime.sections.executive_summary_generation_grade_contract import (
    MANIFEST_SCHEMA_PATH,
    build_generation_grade_contract_manifest,
    generation_law_digest_text,
)
from apps_rg.runtime.sections.executive_summary_targeting_cap import (
    extract_frozen_targeting_from_compiled_content,
)
from apps_rg.runtime.targeting_context_authority import (
    GenerationMaterialContext,
    JudgeMaterialContext,
    generation_material_context_from_bundle,
    material_targeting_digest,
)
from apps_rg.runtime.targeting_context_authority import MaterialTargetingBundle
from apps_rg.runtime.validators.executive_summary_x2 import check_exec_summary_no_credential_dump


def test_e0_compile_leads_with_svp_strategy_not_gold_base() -> None:
    assert "exec_summary_gold_base_resume_001" not in _EXEC_SUMMARY_POSITIVE_COMPILE_IDS
    assert _EXEC_SUMMARY_POSITIVE_COMPILE_IDS[0] == "exec_summary_pos_svp_it_strategy_001"
    body = build_executive_summary_e0(template_supplement=False)
    assert "exec_summary_pos_svp_it_strategy_001" in body
    assert body.index("exec_summary_pos_svp_it_strategy_001") < body.index(
        "exec_summary_pos_credibility_implied_001"
    )


def test_credential_gate_allows_single_fsa_rigor_weave() -> None:
    """C0.3 phase-1 FSA is not a vendor cert dump (unlike AWS Associate labels)."""
    text = (
        "Technology strategy executive who operationalizes governed agentic AI platforms for regulated workflows. "
        "Platform commercialization generated proof-backed revenue while scaling engineering delivery. "
        "Basel III and CCAR lineage frameworks cut regulatory reporting errors for stakeholders. "
        "Monolithic risk analytics were containerized with HPC microservices for faster stress testing. "
        "Built advanced quantitative foundation through derivatives pricing, multi-Greek hedging, capital modeling, "
        "and FSA credential across Towers Perrin, ING, and Aetna. "
        "Governed platform delivery connects execution discipline to measurable enterprise outcomes."
    )
    ok, reason = check_exec_summary_no_credential_dump(text)
    assert ok is True, reason


def test_credential_gate_fails_fsa_mixed_with_aws() -> None:
    text = (
        "Technology strategy executive building governed platforms for enterprise delivery. "
        "Platform lifecycle spans architecture and operating model design. "
        "Commercial outcomes remain grounded in selected executive facts. "
        "Depth is supported by AWS Certified Solutions Architect and FSA credential together. "
        "Governance discipline informs delivery trade-offs across programs. "
        "Enterprise technology direction stays forward-looking when facts support it."
    )
    ok, reason = check_exec_summary_no_credential_dump(text)
    assert ok is False
    assert reason is not None
    assert "mixed" in reason.lower() or "vendor" in reason.lower()


def test_credential_gate_fails_two_fsa_mentions() -> None:
    text = (
        "Technology strategy executive with FSA rigor in quantitative foundations. "
        "Platform lifecycle spans architecture and operating model design. "
        "Commercial outcomes remain grounded in selected executive facts. "
        "Governance discipline informs delivery trade-offs across programs. "
        "Additional actuarial depth includes FSA designation in prior roles. "
        "Enterprise technology direction stays forward-looking when facts support it."
    )
    ok, reason = check_exec_summary_no_credential_dump(text)
    assert ok is False
    assert reason is not None
    assert "at most one" in reason.lower()


def test_credential_gate_fails_two_markers_in_closing_band() -> None:
    text = (
        "Technology strategy executive building governed platforms for enterprise delivery. "
        "Platform lifecycle spans architecture and operating model design. "
        "Commercial outcomes remain grounded in selected executive facts. "
        "Depth is supported by AWS Certified Solutions Architect and Databricks Lakehouse credentials. "
        "Governance discipline informs delivery trade-offs across programs. "
        "Enterprise technology direction stays forward-looking when facts support it."
    )
    ok, reason = check_exec_summary_no_credential_dump(text)
    assert ok is False
    assert reason is not None


def test_judge_packet_includes_synthesis_gates_and_generation_law_digest() -> None:
    text = (
        "Technology strategy executive building governed platforms for regulated enterprise delivery. "
        "The platform generated proof-backed revenue outcomes while scaling engineering delivery. "
        "Implementation of Basel III frameworks reduced regulatory reporting errors for stakeholders. "
        "Re-architected analytics achieved faster calculations and reliable decision support. "
        "Quantitative depth informs governance and delivery trade-offs across complex programs. "
        "Governed runtime delivery stays audit-ready without weakening commercial velocity."
    )
    summary = build_deterministic_gate_summary(
        resume_display_text=text,
        parsed_output={"resume_display_text": text},
        claim_ledger=[
            {"claim_text": "Governed platform delivery.", "source_fact_ids": ["fact_engineering_platform_001"]}
        ],
        allowed_fact_ids={"fact_engineering_platform_001"},
    )
    assert "x2_executive_summary_synthesis_quality" in summary
    assert "x2_exec_summary_mechanical_opener_stack_zero" in summary
    packet = build_executive_summary_judge_packet(
        resume_display_text=text,
        claim_ledger=[
            {"claim_text": "Governed platform delivery.", "source_fact_ids": ["fact_engineering_platform_001"]}
        ],
        allowed_fact_packet=[],
        allowed_fact_ids={"fact_engineering_platform_001"},
        target_title="SVP IT Strategy",
        target_company="Example Co",
        jd_text="jd",
        briefing_text="brief",
        parsed_output={"resume_display_text": text},
        deterministic_gate_summary=summary,
    )
    assert packet.get("generation_law_digest")
    assert packet.get("dimension_gate_map")
    prompt = render_judge_prompt_from_packet(packet)
    assert "GENERATION_LAW_DIGEST" in prompt
    assert generation_law_digest_text() in prompt


def test_manifest_schema_loads() -> None:
    raw = json.loads(MANIFEST_SCHEMA_PATH.read_text(encoding="utf-8"))
    assert raw["properties"]["schema"]["const"] == "generation_grade_contract_manifest_v1"


def test_judge_snapshot_excludes_x1d_wiring_gates() -> None:
    content_gates = [
        {"gate_id": "x2_exec_summary_sentence_count_6", "pass": True, "observed_value": "ok"},
    ]
    wiring = [
        {"gate_id": gid, "pass": True, "observed_value": "ok"} for gid in POST_X2_X1D_WIRING_GATE_IDS
    ]
    before = build_deterministic_gate_summary_from_x2_gates(content_gates)
    after = build_deterministic_gate_summary_from_x2_gates(content_gates + wiring)
    assert before == after
    assert "x2_x1d_required_judges_present" not in after


def test_structural_compiled_prompt_extract_matches_frozen_bundle_digest(
    tmp_path: Path,
) -> None:
    """Regression: legacy regex truncated briefing at in-block 'jd_alignment:' footer text."""
    run_dir = (
        Path(__file__).resolve().parents[3]
        / "artifacts"
        / "apps_rg"
        / "runtime_proofs"
        / "executive_summary"
        / "real"
        / "exec_summary_20260525_100559"
    )
    if not (run_dir / "compiled_prompt.txt").is_file():
        pytest.skip("Brown proof bundle not present")
    import json

    from apps_rg.runtime.targeting_context_authority import (
        _BRIEFING_FIELD_RE,
        _JD_FIELD_RE,
        generation_material_context_from_compiled_prompt,
    )

    rp = json.loads((run_dir / "runtime_payload.json").read_text(encoding="utf-8"))
    bundle = MaterialTargetingBundle.from_dict(rp["material_targeting_bundle"])
    gen_bundle = generation_material_context_from_bundle(bundle)
    cp = (run_dir / "compiled_prompt.txt").read_text(encoding="utf-8")
    content = json.loads(cp)[0]["content"] if cp.strip().startswith("[") else cp
    jd, br = extract_frozen_targeting_from_compiled_content(content)
    assert jd[:200] == bundle.jd_text_frozen[:200]
    assert bundle.briefing_text_frozen in br
    assert len(br) > 2596
    legacy_br = ""
    m_br = _BRIEFING_FIELD_RE.search(content)
    if m_br:
        legacy_br = m_br.group(1).strip()
    assert len(legacy_br) < len(br)
    assert gen_bundle.generation_material_digest == bundle.bundle_digest
    legacy = generation_material_context_from_compiled_prompt(cp)
    assert legacy.generation_material_digest != gen_bundle.generation_material_digest


def test_check_x1d_judge_packet_hash_uniform_fails_on_drift() -> None:
    ok, reason = check_x1d_judge_packet_hash_uniform(
        [
            {
                "provider_key": "gemini_pro",
                "evaluator_mode": "MODEL_BACKED",
                "judge_packet_hash": "aaaaaaaaaaaaaaaa",
            },
            {
                "provider_key": "anthropic_claude",
                "evaluator_mode": "MODEL_BACKED",
                "judge_packet_hash": "bbbbbbbbbbbbbbbb",
            },
        ]
    )
    assert ok is False
    assert reason is not None
    assert "aaaaaaaa" in reason


def test_build_generation_grade_contract_manifest_shape() -> None:
    gen = GenerationMaterialContext("jd", "br", "digest")
    judge = JudgeMaterialContext("jd", "br", "digest")
    body = build_generation_grade_contract_manifest(
        run_id="run_test",
        generation=gen,
        judge=judge,
        parity_receipt={"parity_match": True},
        judge_packet={"rubric_ref": "ref", "deterministic_gate_summary": {"x2_schema_valid": {"pass": True}}},
        token_budget_receipt=None,
        composition_plan={},
        allowed_fact_packet=[],
    )
    assert body["schema"] == "generation_grade_contract_manifest_v1"
    assert "exec_summary_pos_svp_it_strategy_001" in body["instructional_digests"]["e0_compile_ids"]
