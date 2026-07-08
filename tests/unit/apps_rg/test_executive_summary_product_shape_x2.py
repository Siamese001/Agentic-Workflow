"""Executive summary product shape: exactly six sentences, max 140 words, quality gates, briefing, prompt authority."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.sections.executive_summary_briefing import prepare_briefing_for_executive_summary
from apps_rg.runtime.validators.executive_summary_sentence_utils import (
    join_executive_summary_sentences,
    split_sentences,
)
from apps_rg.runtime.validators.executive_summary_x2 import (
    check_exec_summary_cross_sentence_metric_dedup,
    check_exec_summary_display_roundtrip_integrity,
)
from apps_rg.runtime.dispatch.executive_summary_pa import (
    load_executive_summary_example_after,
)
from apps_rg.runtime.validators.executive_summary_x2 import (
    append_executive_summary_x1d_x2_gate_dicts,
    check_exec_summary_jd_alignment_proof_flags,
    check_exec_summary_meta_filler_patterns,
    check_exec_summary_no_credential_dump,
    check_exec_summary_no_mechanism_inventory,
    check_exec_summary_paragraph_max_words,
    check_exec_summary_sentence_count_6,
    check_north_star_style_example_echo_unsupported,
    check_prompt_template_authority,
    check_synthesis_quality,
    EXPECTED_PROMPT_ID,
)


def _six_good_sentences() -> str:
    return (
        "Engineering executive builds governed agentic AI platforms for regulated enterprise delivery. "
        "The leader scales deterministic routing, orchestration, and policy-gated execution across programs. "
        "Platform lifecycle work ties architecture decisions to commercial adoption and operating discipline. "
        "Delivery outcomes include measurable margin and cycle-time improvements grounded in selected facts. "
        "Prior roles show quantitative platform depth across regulated enterprise programs. "
        "Governed runtime delivery stays audit-ready without weakening commercial velocity."
    )


def test_split_sentences_roundtrip_preserves_basel_after_period_boundary() -> None:
    text = (
        "Platform commercialization generated $22M in IP-led revenue while scaling teams. "
        "Basel III and CCAR data lineage, cataloging, and automated validation frameworks "
        "cut regulatory reporting errors by 40%."
    )
    joined = join_executive_summary_sentences(split_sentences(text))
    assert "Basel III" in joined
    assert "\x1f" not in joined
    ok, reason = check_exec_summary_display_roundtrip_integrity(joined)
    assert ok, reason


def test_split_sentences_handles_us_and_regulatory_prose():
    text = (
        "Engineering executive leads U.S. enterprise programs with Basel III and CCAR discipline. "
        "AWS platform delivery stays audit-ready across regulated workflows. "
        "Revenue grew 12.5% while cycle time fell 30%. "
        "The leader commercialized reusable agentic services without weakening governance posture."
    )
    sents = split_sentences(text)
    assert len(sents) == 4
    assert "U.S." in sents[0]
    assert "12.5%" in sents[2]


def _jd_alignment_fixture(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "targeting_only": True,
        "jd_used_as_proof": False,
        "briefing_used_as_proof": False,
        "graph_targeting": {
            "projection_source": "sqlite_role_family_projection",
            "sqlite_projection_row_found": True,
            "fallback_pillar_bridge_used": False,
            "release_eligible_targeting_proof": True,
            "targeting_degraded_explicit": False,
        },
    }
    base.update(overrides)
    return {"jd_alignment": base}


def test_jd_alignment_proof_flags_require_briefing_false():
    ok, _ = check_exec_summary_jd_alignment_proof_flags(_jd_alignment_fixture())
    assert ok is True
    bad, reason = check_exec_summary_jd_alignment_proof_flags(
        _jd_alignment_fixture(briefing_used_as_proof=True)
    )
    assert bad is False
    assert reason is not None


def test_sentence_count_6_pass_and_legacy_bands_fail():
    good = _six_good_sentences()
    assert check_exec_summary_sentence_count_6(good)[0] is True
    legacy = "One sentence here. Two sentences here."
    assert check_exec_summary_sentence_count_6(legacy)[0] is False
    five_only = _six_good_sentences().rsplit(". ", 1)[0] + "."
    assert check_exec_summary_sentence_count_6(five_only)[0] is False
    six = " ".join([f"Sentence {i} states executive platform value." for i in range(6)])
    assert check_exec_summary_sentence_count_6(six)[0] is True
    seven = " ".join([f"Sentence {i} states executive platform value." for i in range(7)])
    assert check_exec_summary_sentence_count_6(seven)[0] is False


def test_mechanism_inventory_fails():
    bad = (
        "Engineering executive builds governed platforms. "
        "The leader delivers deterministic routing, multi-agent orchestration, GraphRAG retrieval, "
        "sandboxed execution, policy gating, validation controls, and replayable traces. "
        "Platform lifecycle work spans architecture and operating model design. "
        "Outcomes stay grounded in selected executive facts."
    )
    ok, reason = check_exec_summary_no_mechanism_inventory(bad)
    assert ok is False
    assert reason is not None


def test_credential_dump_fixture_fails():
    bad = (
        "Engineering executive builds governed agentic AI platforms for enterprise delivery. "
        "The leader scales platform lifecycle and commercial adoption across programs. "
        "Delivery outcomes remain grounded in selected executive facts. "
        "AWS Certified Machine Learning Engineer, AWS Certified Solutions Architect, Databricks Lakehouse "
        "Fundamentals, and Fellow of the Society of Actuaries credentials reinforce senior IT strategy "
        "leadership, grounded in Basel III and CCAR lineage."
    )
    ok, reason = check_exec_summary_no_credential_dump(bad)
    assert ok is False
    assert reason is not None


def test_briefing_selection_manifest_no_silent_only_truncate(tmp_path: Path):
    long_brief = "## Target priorities\n" + ("regulated modernization emphasis. " * 1_100)
    long_brief += "\n## Secondary notes\n" + ("additional context tail. " * 1_100)
    selected, receipt = prepare_briefing_for_executive_summary(long_brief)
    assert receipt["briefing_original_chars"] > receipt["briefing_included_chars"]
    assert receipt["truncation_or_selection_reason"] == "ranked_section_selection"
    assert receipt.get("included_section_ids")
    assert receipt.get("excluded_section_ids")
    assert "TRUNCATED: briefing tail omitted" not in selected


def test_prompt_template_authority_requires_trace(tmp_path: Path):
    art = tmp_path / "prompt_selection_trace.json"
    art.write_text(
        json.dumps(
            {
                "prompt_id": "wrong_template",
                "apps_rg_prompt_template_ref": "apps_rg/prompt_assembly/templates/other.yaml",
            }
        ),
        encoding="utf-8",
    )
    ok, reason = check_prompt_template_authority(tmp_path)
    assert ok is False
    assert reason is not None

    art.write_text(
        json.dumps(
            {
                "prompt_id": EXPECTED_PROMPT_ID,
                "apps_rg_prompt_template_ref": (
                    "apps_rg/prompt_assembly/templates/executive_summary.generate_scratch_v1.yaml"
                ),
            }
        ),
        encoding="utf-8",
    )
    ok, reason = check_prompt_template_authority(tmp_path)
    assert ok is True

    (tmp_path / "compiled_prompt_artifact.json").write_text(
        json.dumps(
            {
                "apps_rg_prompt_template_ref": (
                    "apps_rg/prompt_assembly/templates/executive_summary.generate_scratch_v1.yaml"
                ),
                "compiler_template_id": "strategic_tailor_v1",
                "selected_template_id": "strategic_tailor_v1",
            }
        ),
        encoding="utf-8",
    )
    ok, reason = check_prompt_template_authority(tmp_path)
    assert ok is True

    (tmp_path / "prompt_selection_trace.json").write_text(
        json.dumps({"prompt_id": "wrong_template", "apps_rg_prompt_template_ref": "other.yaml"}),
        encoding="utf-8",
    )
    ok, reason = check_prompt_template_authority(tmp_path)
    assert ok is False


def test_style_exemplars_pass_no_credential_dump_gate():
    """Gold/variant style paragraphs must not teach a trailing FSA/AWS cert sentence that fails X2."""
    for label, text in (
        ("gold", load_executive_summary_example_after("exec_summary_base_resume_style_001")),
        ("implied", load_executive_summary_example_after("exec_summary_pos_credibility_implied_001")),
    ):
        ok, reason = check_exec_summary_no_credential_dump(text)
        assert ok, f"{label}: {reason}"


def test_north_star_echo_gate_counts_role_episode_metric_values_as_support():
    text = "Platform productization generated $22M in IP-led revenue with 20% gross margin expansion."
    facts = [
        {
            "fact_id": "reb_unify_platform_commercialization_leadership",
            "claim_text": "Platform productization, IP-led revenue, margin expansion, team scale",
            "metric_values": ["$22M IP-led revenue", "20% gross margin expansion"],
        }
    ]
    ok, reason = check_north_star_style_example_echo_unsupported(text, facts)
    assert ok, reason


def test_north_star_echo_gate_counts_gross_margin_wording_variant_as_support():
    text = (
        "Platform commercialization leadership generated $22M in IP-led revenue, "
        "expanding gross margins by 20%, and scaling the engineering team from 8 to 28 specialists."
    )
    facts = [
        {
            "fact_id": "reb_unify_platform_commercialization_leadership",
            "claim_text": "Platform productization, IP-led revenue, margin expansion, team scale",
            "metric_values": ["$22M IP-led revenue", "20% gross margin expansion"],
        }
    ]
    ok, reason = check_north_star_style_example_echo_unsupported(text, facts)
    assert ok, reason


def test_synthesis_quality_requires_six_sentences():
    short = (
        "An experienced engineering executive with a strong background in platforms. "
        "This individual scaled teams and reduced errors by 40%. "
        "Additionally, their expertise provides leadership."
    )
    assert check_synthesis_quality(short)[0] is False
    assert check_exec_summary_sentence_count_6(short)[0] is False
    assert check_exec_summary_meta_filler_patterns(short)[0] is False
    assert check_exec_summary_paragraph_max_words(short, {})[0] is True


def test_meta_filler_blocks_leadership_profile_capstone() -> None:
    bad = (
        "This leadership profile can translate into partner-led applied AI architecture "
        "that scales safely across enterprise ecosystems."
    )

    ok, reason = check_exec_summary_meta_filler_patterns(bad)

    assert ok is False
    assert reason is not None
    assert "leadership profile" in reason


def test_lane_retry_checks_word_bounds_and_meta():
    import apps_rg.runtime.sections.executive_summary_lane as lane

    src = Path(lane.__file__).read_text(encoding="utf-8")
    assert "check_exec_summary_paragraph_max_words" in src
    assert "this individual" in src.lower()
    assert "synthesis_regen_receipt.json" in src


def test_run_x2_gates_does_not_emit_retired_srfs_product_gate_ids():
    from apps_rg.runtime.sections.section_product_shape_ssot import (
        RETIRED_EXEC_SUMMARY_X2_GATE_IDS,
    )
    from apps_rg.runtime.validators.executive_summary_x2 import run_x2_gates

    gates = run_x2_gates(
        resume_display_text=_six_good_sentences(),
        parsed_output={"resume_display_text": _six_good_sentences(), "jd_alignment": {}},
        claim_ledger=[{"claim_text": "c", "source_fact_ids": ["fact_engineering_platform_001"]}],
        text_claim_coverage={"sentences": [], "overall_pass": True},
        allowed_fact_ids={"fact_engineering_platform_001"},
        target_company="Acme",
        jd_text="enterprise AI",
        temperature=0.45,
        runtime_generation_status="REAL_LLM",
        monolithic_prompt_invoked=False,
        strategic_tailor_v1_invoked=False,
    )
    emitted = {g.gate_id for g in gates}
    assert not emitted & RETIRED_EXEC_SUMMARY_X2_GATE_IDS


def test_post_x2_judge_presence_uses_runtime_required_providers(tmp_path: Path):
    rows = append_executive_summary_x1d_x2_gate_dicts(
        x1d_judges=[{"provider_key": "gemini_pro", "evaluator_mode": "MODEL_BACKED"}],
        artifacts_dir=tmp_path,
        required_providers=["gemini_pro"],
    )
    required_gate = next(r for r in rows if r["gate_id"] == "x2_x1d_required_judges_present")
    assert required_gate["pass"] is True

    rows = append_executive_summary_x1d_x2_gate_dicts(
        x1d_judges=[{"provider_key": "gemini_pro", "evaluator_mode": "MODEL_BACKED"}],
        artifacts_dir=tmp_path,
        required_providers=["gemini_pro", "openai_chatgpt"],
    )
    required_gate = next(r for r in rows if r["gate_id"] == "x2_x1d_required_judges_present")
    assert required_gate["pass"] is False
    assert "openai_chatgpt" in str(required_gate["failure_reason"])
